# -*- coding: utf-8 -*-
"""Storage service for file-based persistence."""

import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.config import Config
from app.models.settings import Settings
from app.models.history import HistoryRecord
from app.utils.crypto import encrypt, decrypt


class StorageService:
    """Service for file-based storage operations."""
    
    def __init__(
        self,
        config_dir: Optional[Path] = None,
        result_dir: Optional[Path] = None,
        encryption_key: Optional[str] = None
    ):
        self.config_dir = config_dir or Config.CONFIG_DIR
        self.result_dir = result_dir or Config.RESULT_DIR
        self.encryption_key = encryption_key or Config.ENCRYPTION_KEY
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== Settings ====================
    
    def save_settings(self, settings: Settings) -> None:
        """Save settings with encryption."""
        settings_file = self.config_dir / "settings.enc"
        json_str = json.dumps(settings.to_dict(), ensure_ascii=False)
        encrypted = encrypt(json_str, self.encryption_key)
        settings_file.write_text(encrypted, encoding='utf-8')
    
    def load_settings(self) -> Settings:
        """Load and decrypt settings."""
        settings_file = self.config_dir / "settings.enc"
        if not settings_file.exists():
            return Settings()
        
        try:
            encrypted = settings_file.read_text(encoding='utf-8')
            decrypted = decrypt(encrypted, self.encryption_key)
            data = json.loads(decrypted)
            return Settings.from_dict(data)
        except Exception:
            return Settings()

    # ==================== Suites ====================
    
    def _extract_keyword(self, description: str) -> str:
        """Extract keyword from description for folder naming."""
        prefixes = ['我需要', '我想要', '帮我', '请', '给我', '创建', '生成', '做一个', '写一个', '一个']
        suffixes = ['的提示词', '提示词', '的prompt', 'prompt', '助手', '系统']
        
        keyword = description.strip()
        for prefix in prefixes:
            if keyword.startswith(prefix):
                keyword = keyword[len(prefix):].strip()
        
        for suffix in suffixes:
            if keyword.endswith(suffix) and len(keyword) > len(suffix):
                keyword = keyword[:-len(suffix)].strip()
        
        if len(keyword) > 20:
            keyword = keyword[:20]
        
        if not keyword:
            keyword = f"prompt_{int(datetime.now().timestamp())}"
        
        # Clean invalid filename characters
        keyword = re.sub(r'[<>:"/\\|?*]', '_', keyword)
        return keyword
    
    def save_suite(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a prompt suite to disk."""
        requirement = data.get('requirement', {})
        prompt_suite = data.get('promptSuite', {})
        review = data.get('review')
        test_result = data.get('testResult')
        versions = data.get('versions', [])
        
        # Create folder name
        keyword = self._extract_keyword(requirement.get('description', ''))
        timestamp = datetime.now().strftime('%Y-%m-%d')
        folder_name = f"{keyword}_{timestamp}"
        suite_dir = self.result_dir / folder_name
        suite_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        # Save overview markdown
        overview = self._generate_overview_md(prompt_suite, requirement, review, test_result, versions)
        (suite_dir / '0_概览.md').write_text(overview, encoding='utf-8')
        saved_files.append('0_概览.md')
        
        # Save each role prompt
        prompts = prompt_suite.get('prompts', [])
        for i, role_prompt in enumerate(prompts):
            filename = self._generate_role_filename(i, role_prompt)
            content = self._generate_role_md(role_prompt, prompt_suite.get('system_name', ''))
            (suite_dir / filename).write_text(content, encoding='utf-8')
            saved_files.append(filename)
        
        # Save full JSON data
        full_data = {**data, 'savedAt': datetime.now().isoformat()}
        (suite_dir / '_data.json').write_text(
            json.dumps(full_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        saved_files.append('_data.json')
        
        return {
            'folder': folder_name,
            'path': str(suite_dir),
            'files': saved_files
        }

    def _generate_role_filename(self, index: int, role_prompt: Dict) -> str:
        """Generate filename for a role prompt."""
        role_name = role_prompt.get('role_name') or role_prompt.get('role_id') or f'role_{index}'
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', role_name)
        return f"{index + 1}_{safe_name}.md"
    
    def get_or_create_task_dir(self, description: str, task_id: str = None) -> Path:
        """Get or create a directory for task results."""
        keyword = self._extract_keyword(description)
        timestamp = datetime.now().strftime('%Y-%m-%d')
        folder_name = f"{keyword}_{timestamp}"
        task_dir = self.result_dir / folder_name
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir
    
    def save_role_prompt_md(
        self, 
        task_dir: Path, 
        role_index: int, 
        role_name: str,
        role_type: str,
        description: str,
        prompt_content: str
    ) -> str:
        """Save a single role prompt as markdown file immediately.
        
        Args:
            task_dir: Directory to save the file
            role_index: Index of the role (0-based)
            role_name: Name of the role
            role_type: Type of the role (core/quality/support)
            description: Role description
            prompt_content: The actual prompt content (clean, ready to use)
            
        Returns:
            The filename that was saved
        """
        # Generate filename
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', role_name)
        filename = f"{role_index + 1}_{safe_name}.md"
        
        # Generate clean markdown content - directly usable
        content = f"""# {role_name}

> {description}

---

{prompt_content}
"""
        
        # Write file
        filepath = task_dir / filename
        filepath.write_text(content, encoding='utf-8')
        
        return filename
    
    def _generate_role_md(self, role_prompt: Dict, system_name: str) -> str:
        """Generate markdown content for a role prompt - 直接可复制使用的格式."""
        prompt_content = role_prompt.get('prompt', '')
        role_name = role_prompt.get('role_name', role_prompt.get('role_id', ''))
        description = role_prompt.get('description', '')
        
        # 如果 prompt 是 JSON 代码块格式，尝试提取真正的 prompt 内容
        prompt_content = self._extract_prompt_content(prompt_content)
        
        return f"""# {role_name}

> {description}

---

{prompt_content}
"""
    
    def _extract_prompt_content(self, raw_prompt: str) -> str:
        """从可能包含 JSON 代码块的内容中提取真正的 prompt."""
        import json
        
        if not raw_prompt:
            return ''
        
        raw_stripped = raw_prompt.strip()
        
        # 如果内容以 ```json 或 ``` 开头，尝试解析 JSON 并提取 prompt 字段
        if raw_stripped.startswith('```'):
            # 移除代码块标记
            content = re.sub(r'^```(?:json|xml)?\s*\n?', '', raw_stripped)
            content = re.sub(r'\n?```\s*$', '', content)
            
            try:
                data = json.loads(content)
                if isinstance(data, dict) and 'prompt' in data:
                    # 提取 prompt 字段，处理转义字符
                    extracted = data['prompt']
                    if isinstance(extracted, str):
                        return extracted
            except json.JSONDecodeError:
                # JSON 解析失败，可能是 XML 格式，直接返回内容
                if '<role>' in content or '<task>' in content or '<system>' in content:
                    return content
        
        # 如果内容包含 <role> 或 <task> 等 XML 标签，说明已经是提示词内容
        if '<role>' in raw_prompt or '<task>' in raw_prompt or '<system>' in raw_prompt:
            return raw_prompt
        
        # 尝试直接解析为 JSON（可能是没有代码块包裹的 JSON）
        try:
            data = json.loads(raw_prompt)
            if isinstance(data, dict) and 'prompt' in data:
                return data['prompt']
        except json.JSONDecodeError:
            pass
        
        # 无法解析，返回原内容
        return raw_prompt
    
    def _generate_overview_md(
        self,
        prompt_suite: Dict,
        requirement: Dict,
        review: Optional[Dict],
        test_result: Optional[Dict],
        versions: List
    ) -> str:
        """Generate overview markdown for a suite."""
        prompts = prompt_suite.get('prompts', [])
        roles_table = '\n'.join(
            f"| {i+1} | {p.get('role_name', p.get('role_id', ''))} | {p.get('role_type', 'core')} | {(p.get('description', '')[:50] + '...' if len(p.get('description', '')) > 50 else p.get('description', ''))} |"
            for i, p in enumerate(prompts)
        )
        
        score = review.get('score', 'N/A') if review else 'N/A'
        pass_rate = f"{test_result['summary']['pass_rate']*100:.0f}%" if test_result and 'summary' in test_result else 'N/A'
        
        return f"""# {prompt_suite.get('system_name', '提示词套件')}

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 角色数量: {prompt_suite.get('total_roles', len(prompts))}
> 最终评分: {score}/10
> 测试通过率: {pass_rate}

## 需求描述

{requirement.get('description', '')}

## 角色列表

| 序号 | 角色名称 | 类型 | 描述 |
|------|----------|------|------|
{roles_table}

## 工作流程

{prompt_suite.get('workflow_summary', '')}

## 集成说明

{prompt_suite.get('integration_notes', '')}
"""

    def list_suites(self) -> List[Dict[str, Any]]:
        """List all saved suites."""
        if not self.result_dir.exists():
            return []
        
        suites = []
        for folder in self.result_dir.iterdir():
            if not folder.is_dir():
                continue
            
            data_file = folder / '_data.json'
            metadata = {'name': folder.name}
            
            if data_file.exists():
                try:
                    data = json.loads(data_file.read_text(encoding='utf-8'))
                    prompt_suite = data.get('promptSuite', {})
                    metadata = {
                        'name': folder.name,
                        'systemName': prompt_suite.get('system_name'),
                        'description': data.get('requirement', {}).get('description'),
                        'score': data.get('review', {}).get('score') if data.get('review') else None,
                        'rolesCount': prompt_suite.get('total_roles') or len(prompt_suite.get('prompts', [])),
                        'savedAt': data.get('savedAt')
                    }
                except Exception:
                    pass
            
            suites.append(metadata)
        
        # Sort by savedAt descending
        suites.sort(key=lambda x: x.get('savedAt', ''), reverse=True)
        return suites
    
    def get_suite(self, name: str) -> Optional[Dict[str, Any]]:
        """Get suite details by name."""
        suite_dir = self.result_dir / name
        data_file = suite_dir / '_data.json'
        
        if not data_file.exists():
            return None
        
        return json.loads(data_file.read_text(encoding='utf-8'))
    
    # ==================== History ====================
    
    def _get_history_file(self) -> Path:
        return self.config_dir / 'history.json'
    
    def _load_history(self) -> List[Dict]:
        history_file = self._get_history_file()
        if not history_file.exists():
            return []
        try:
            return json.loads(history_file.read_text(encoding='utf-8'))
        except Exception:
            return []
    
    def _save_history(self, history: List[Dict]) -> None:
        history_file = self._get_history_file()
        history_file.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def add_history(self, record: HistoryRecord) -> HistoryRecord:
        """Add a history record."""
        history = self._load_history()
        history.insert(0, record.to_dict())
        history = history[:100]  # Keep max 100 records
        self._save_history(history)
        return record
    
    def get_history(self, limit: int = 50) -> List[HistoryRecord]:
        """Get history records."""
        history = self._load_history()
        return [HistoryRecord.from_dict(h) for h in history[:limit]]
    
    def delete_history(self, record_id: str) -> None:
        """Delete a history record."""
        history = self._load_history()
        history = [h for h in history if h.get('id') != record_id]
        self._save_history(history)
    
    def clear_history(self) -> None:
        """Clear all history records."""
        self._save_history([])
    
    # ==================== Task Progress (断点恢复) ====================
    
    def _get_tasks_dir(self) -> Path:
        """Get tasks directory for progress tracking."""
        tasks_dir = self.config_dir / 'tasks'
        tasks_dir.mkdir(parents=True, exist_ok=True)
        return tasks_dir
    
    def save_task_progress(self, task_id: str, progress: Dict[str, Any]) -> None:
        """Save task progress for recovery."""
        task_file = self._get_tasks_dir() / f'{task_id}.json'
        progress['updated_at'] = datetime.now().isoformat()
        task_file.write_text(
            json.dumps(progress, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def load_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load task progress for recovery."""
        task_file = self._get_tasks_dir() / f'{task_id}.json'
        if not task_file.exists():
            return None
        try:
            return json.loads(task_file.read_text(encoding='utf-8'))
        except Exception:
            return None
    
    def delete_task_progress(self, task_id: str) -> None:
        """Delete task progress file after completion."""
        task_file = self._get_tasks_dir() / f'{task_id}.json'
        if task_file.exists():
            task_file.unlink()
    
    def list_incomplete_tasks(self) -> List[Dict[str, Any]]:
        """List all incomplete tasks that can be resumed."""
        tasks_dir = self._get_tasks_dir()
        if not tasks_dir.exists():
            return []
        
        tasks = []
        for task_file in tasks_dir.glob('*.json'):
            try:
                data = json.loads(task_file.read_text(encoding='utf-8'))
                if data.get('status') not in ('completed', 'cancelled'):
                    tasks.append({
                        'task_id': task_file.stem,
                        'description': data.get('description', ''),
                        'status': data.get('status', 'unknown'),
                        'completed_roles': len([r for r in data.get('role_results', {}).values() if r]),
                        'total_roles': data.get('total_roles', 0),
                        'updated_at': data.get('updated_at')
                    })
            except Exception:
                pass
        
        tasks.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return tasks
    
    def save_role_result(self, task_id: str, role_index: int, role_prompt: Dict) -> None:
        """Save individual role result (增量保存)."""
        progress = self.load_task_progress(task_id) or {}
        if 'role_results' not in progress:
            progress['role_results'] = {}
        progress['role_results'][str(role_index)] = role_prompt
        self.save_task_progress(task_id, progress)


# Global instance
_storage: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get the global storage service instance."""
    global _storage
    if _storage is None:
        _storage = StorageService()
    return _storage
