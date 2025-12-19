# -*- coding: utf-8 -*-
"""Pipeline service for orchestrating prompt generation."""

import uuid
import asyncio
import threading
from pathlib import Path
from queue import Queue
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from app.config import Config
from app.models.pipeline import (
    PipelineState, PipelineEvent, SystemArchitecture, SystemRole,
    RolePrompt, RoleProcessState, ReviewResult, TestResult, PromptSuite,
    WeaknessItem, SuggestionItem
)
from app.services.llm_client import LLMClient
from app.services.prompt_loader import load_prompt
from app.services.storage_service import get_storage_service
from app.utils.json_utils import parse_json_response


def log(msg: str, level: str = "INFO"):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {msg}", flush=True)


class PipelineService:
    """Service for managing prompt generation pipeline."""
    
    MAX_ITERATIONS = Config.MAX_ITERATIONS
    PASS_SCORE = Config.PASS_SCORE
    DEFAULT_MAX_PARALLEL = Config.DEFAULT_MAX_PARALLEL
    
    def __init__(self, llm_client: LLMClient, use_stream: bool = True, max_parallel: int = None):
        self.llm_client = llm_client
        self.use_stream = use_stream
        self.state: Optional[PipelineState] = None
        self.event_queue: Queue = Queue()
        self._paused = False
        self._cancelled = False
        self._max_parallel = max_parallel or self.DEFAULT_MAX_PARALLEL
        self._executor = ThreadPoolExecutor(max_workers=self._max_parallel)
        self._storage = get_storage_service()
        self._completed_prompts: Dict[int, RolePrompt] = {}  # 已完成的角色结果缓存
        self._lock = threading.Lock()  # 线程锁，保护并发写入
        self._task_dir: Optional[Path] = None  # 任务结果目录
        log(f"PipelineService 初始化完成, use_stream={use_stream}, max_parallel={self._max_parallel}")
    
    def _emit_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Emit a pipeline event."""
        event = PipelineEvent(
            type=event_type,
            data=data or {},
            timestamp=datetime.now().isoformat()
        )
        self.event_queue.put(event)
    
    def _check_cancelled(self) -> bool:
        """Check if pipeline is cancelled."""
        return self._cancelled
    
    async def _wait_if_paused(self) -> bool:
        """Wait while paused, return False if cancelled."""
        while self._paused and not self._cancelled:
            await asyncio.sleep(0.1)
        return not self._cancelled
    
    def _save_progress(self) -> None:
        """Save current pipeline progress for recovery."""
        if not self.state:
            return
        
        progress = {
            'task_id': self.state.task_id,
            'status': self.state.status,
            'description': self.state.description,
            'prompt_type': self.state.prompt_type,
            'model': self.state.model,
            'current_step': self.state.current_step,
            'total_roles': len(self.state.role_states) if self.state.role_states else 0,
            'system_architecture': self._serialize_architecture() if self.state.system_architecture else None,
            'role_results': {
                str(idx): self._serialize_role_prompt(prompt)
                for idx, prompt in self._completed_prompts.items()
            }
        }
        self._storage.save_task_progress(self.state.task_id, progress)
        log(f"进度已保存: {len(self._completed_prompts)}/{progress['total_roles']} 角色完成")
    
    def _serialize_architecture(self) -> Dict[str, Any]:
        """Serialize SystemArchitecture to dict."""
        arch = self.state.system_architecture
        if not arch:
            return None
        return {
            'system_name': arch.system_name,
            'system_description': arch.system_description,
            'domain': arch.domain,
            'target_user': arch.target_user,
            'use_cases': arch.use_cases,
            'roles': [
                {
                    'id': r.id, 'name': r.name, 'type': r.type,
                    'description': r.description, 'responsibilities': r.responsibilities,
                    'inputs': r.inputs, 'outputs': r.outputs, 'triggers': r.triggers, 'priority': r.priority
                }
                for r in arch.roles
            ]
        }
    
    def _serialize_role_prompt(self, prompt: RolePrompt) -> Dict[str, Any]:
        """Serialize RolePrompt to dict."""
        return {
            'role_id': prompt.role_id,
            'role_name': prompt.role_name,
            'role_type': prompt.role_type,
            'description': prompt.description,
            'prompt': prompt.prompt,
            'input_template': prompt.input_template,
            'output_format': prompt.output_format,
            'triggers': prompt.triggers
        }
    
    def _clean_prompt_content(self, raw_prompt: str) -> str:
        """清理 prompt 内容，从 JSON 代码块中提取真正的提示词."""
        import json
        import re
        
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
                    extracted = data['prompt']
                    if isinstance(extracted, str):
                        log(f"  从 JSON 代码块中提取 prompt，长度: {len(extracted)}")
                        return extracted
            except json.JSONDecodeError:
                # JSON 解析失败，可能是 XML 格式，检查是否包含提示词标签
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
    
    def _save_role_result(self, role_index: int, role_prompt: RolePrompt) -> None:
        """Save individual role result immediately after completion (线程安全).
        
        立即将角色提示词写入 md 文件，同时更新进度文件用于断点恢复。
        """
        with self._lock:
            self._completed_prompts[role_index] = role_prompt
            self._save_progress()
            
            # 立即写入 md 文件到结果目录
            if self._task_dir and self.state:
                try:
                    filename = self._storage.save_role_prompt_md(
                        task_dir=self._task_dir,
                        role_index=role_index,
                        role_name=role_prompt.role_name,
                        role_type=role_prompt.role_type,
                        description=role_prompt.description,
                        prompt_content=role_prompt.prompt  # 直接使用干净的 prompt 内容
                    )
                    log(f"  角色 {role_prompt.role_name} 已保存到: {self._task_dir / filename}")
                except Exception as e:
                    log(f"  保存角色 md 文件失败: {e}", "ERROR")
        
        self._emit_event('role_saved', {'roleIndex': role_index, 'roleName': role_prompt.role_name})
    
    def load_progress(self, task_id: str) -> bool:
        """Load saved progress for resuming a task."""
        progress = self._storage.load_task_progress(task_id)
        if not progress:
            log(f"未找到任务进度: {task_id}", "WARN")
            return False
        
        log(f"加载任务进度: {task_id}")
        
        # Restore state
        self.state = PipelineState(
            task_id=task_id,
            status='running',
            description=progress.get('description', ''),
            prompt_type=progress.get('prompt_type', ''),
            model=progress.get('model', ''),
            current_step=progress.get('current_step', 0)
        )
        
        # Restore architecture
        arch_data = progress.get('system_architecture')
        if arch_data:
            role_fields = {'id', 'name', 'type', 'description', 'responsibilities', 'inputs', 'outputs', 'triggers', 'priority'}
            roles = [SystemRole(**{k: v for k, v in r.items() if k in role_fields}) for r in arch_data.get('roles', [])]
            self.state.system_architecture = SystemArchitecture(
                system_name=arch_data.get('system_name', ''),
                system_description=arch_data.get('system_description', ''),
                domain=arch_data.get('domain', ''),
                target_user=arch_data.get('target_user', ''),
                use_cases=arch_data.get('use_cases', []),
                roles=roles
            )
            # Initialize role states
            self.state.role_states = [
                RoleProcessState(role_id=r.id, role_name=r.name, role_type=r.type, status='pending')
                for r in roles
            ]
        
        # Restore completed prompts
        role_results = progress.get('role_results', {})
        for idx_str, prompt_data in role_results.items():
            idx = int(idx_str)
            self._completed_prompts[idx] = RolePrompt(**prompt_data)
            if self.state.role_states and idx < len(self.state.role_states):
                self.state.role_states[idx].status = 'completed'
        
        log(f"已恢复 {len(self._completed_prompts)} 个已完成的角色")
        return True
    
    def get_pending_role_indices(self) -> List[int]:
        """Get indices of roles that haven't been completed yet."""
        if not self.state or not self.state.role_states:
            return []
        return [i for i in range(len(self.state.role_states)) if i not in self._completed_prompts]

    def start(self, description: str, prompt_type: str, model: str) -> str:
        """Start a new pipeline execution."""
        task_id = str(uuid.uuid4())
        log(f"========== 流水线启动 ==========")
        log(f"任务ID: {task_id}")
        log(f"需求描述: {description[:100]}...")
        log(f"提示词类型: {prompt_type}")
        log(f"目标模型: {model}")
        
        self.state = PipelineState(
            task_id=task_id,
            status='running',
            description=description,
            prompt_type=prompt_type,
            model=model
        )
        self._paused = False
        self._cancelled = False
        
        # 创建任务结果目录（用于立即保存每个角色的 md 文件）
        self._task_dir = self._storage.get_or_create_task_dir(description, task_id)
        log(f"结果目录: {self._task_dir}")
        
        self._emit_event('pipeline_started', {'taskId': task_id})
        return task_id
    
    def pause(self) -> None:
        """Pause pipeline execution."""
        log("流水线暂停")
        self._paused = True
        if self.state:
            self.state.status = 'paused'
        self._emit_event('pipeline_paused')
    
    def resume(self) -> None:
        """Resume pipeline execution."""
        log("流水线恢复")
        self._paused = False
        if self.state:
            self.state.status = 'running'
        self._emit_event('pipeline_resumed')
    
    def cancel(self) -> None:
        """Cancel pipeline execution."""
        log("流水线取消", "WARN")
        self._cancelled = True
        self._paused = False
        if self.state:
            self.state.status = 'cancelled'
        self._emit_event('pipeline_cancelled')
    
    def run_analyzer(self, on_output: Optional[Callable[[str], None]] = None) -> Optional[SystemArchitecture]:
        """Run the Analyzer agent."""
        if not self.state:
            log("错误: state 为空", "ERROR")
            return None
        
        log("---------- [1/5] Analyzer 开始 ----------")
        log(f"正在加载 analyzer 提示词...")
        self._emit_event('agent_started', {'agent': 'analyzer'})
        
        try:
            prompt = load_prompt('analyzer')
            log(f"提示词加载成功，长度: {len(prompt)} 字符")
        except Exception as e:
            log(f"提示词加载失败: {e}", "ERROR")
            return None
        
        user_input = f"用户需求：{self.state.description}\n提示词类型：{self.state.prompt_type}\n目标模型：{self.state.model}"
        log(f"用户输入构建完成，长度: {len(user_input)} 字符")
        
        output = ""
        chunk_count = 0
        
        if self.use_stream:
            def stream_handler(chunk: str):
                nonlocal output, chunk_count
                output += chunk
                chunk_count += 1
                if chunk_count % 50 == 0:
                    log(f"Analyzer 已接收 {chunk_count} 个 chunks，输出长度: {len(output)}")
                if on_output:
                    on_output(chunk)
                self._emit_event('agent_output', {'agent': 'analyzer', 'chunk': chunk})
            
            log(f"开始调用 LLM (流式, 模型: {self.state.model})...")
            try:
                self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=stream_handler)
                log(f"LLM 调用完成，总输出长度: {len(output)} 字符，共 {chunk_count} 个 chunks")
            except Exception as e:
                log(f"LLM 调用失败: {e}", "ERROR")
                self._emit_event('agent_completed', {'agent': 'analyzer', 'success': False})
                return None
        else:
            log(f"开始调用 LLM (同步, 模型: {self.state.model})...")
            try:
                output = self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=None)
                log(f"LLM 调用完成，总输出长度: {len(output)} 字符")
            except Exception as e:
                log(f"LLM 调用失败: {e}", "ERROR")
                self._emit_event('agent_completed', {'agent': 'analyzer', 'success': False})
                return None
        
        # Parse response
        log("正在解析 JSON 响应...")
        data = parse_json_response(output)
        if not data or 'roles' not in data:
            log(f"JSON 解析失败或缺少 roles 字段", "ERROR")
            log(f"原始输出前500字符: {output[:500]}")
            self._emit_event('agent_completed', {'agent': 'analyzer', 'success': False})
            return None
        
        # Build SystemArchitecture - filter to valid fields only
        role_fields = {'id', 'name', 'type', 'description', 'responsibilities', 'inputs', 'outputs', 'triggers', 'priority'}
        roles = [SystemRole(**{k: v for k, v in r.items() if k in role_fields}) for r in data.get('roles', [])]
        log(f"解析成功，系统名称: {data.get('system_name')}, 角色数量: {len(roles)}")
        for i, r in enumerate(roles):
            log(f"  角色 {i+1}: {r.name} ({r.type}) - {r.description[:50]}...")
        
        architecture = SystemArchitecture(
            system_name=data.get('system_name', ''),
            system_description=data.get('system_description', ''),
            domain=data.get('domain', ''),
            target_user=data.get('target_user', ''),
            use_cases=data.get('use_cases', []),
            roles=roles
        )
        
        self.state.system_architecture = architecture
        self.state.current_step = 1
        
        # Initialize role states
        self.state.role_states = [
            RoleProcessState(
                role_id=r.id,
                role_name=r.name,
                role_type=r.type,
                status='pending'
            )
            for r in roles
        ]
        
        log("---------- [1/5] Analyzer 完成 ✓ ----------")
        self._emit_event('agent_completed', {'agent': 'analyzer', 'success': True})
        return architecture

    def _build_generator_context(self, role: SystemRole) -> str:
        """Build context for generator agent."""
        arch = self.state.system_architecture
        other_roles = [r for r in arch.roles if r.id != role.id]
        other_roles_str = '\n'.join(
            f"- {r.name} ({r.type}): {r.description}"
            for r in other_roles
        ) or '无'
        
        return f"""## 系统信息
系统名称：{arch.system_name}
系统描述：{arch.system_description}
目标用户：{arch.target_user}
使用场景：{'、'.join(arch.use_cases)}

## 当前需要生成提示词的角色
```json
{{"id": "{role.id}", "name": "{role.name}", "type": "{role.type}", "description": "{role.description}", "responsibilities": {role.responsibilities}, "inputs": {role.inputs}, "outputs": {role.outputs}, "triggers": {role.triggers}}}
```

## 其他角色（用于理解协作关系）
{other_roles_str}

请为「{role.name}」生成完整的提示词。"""
    
    def run_generator(
        self,
        role_index: int,
        on_output: Optional[Callable[[str], None]] = None
    ) -> Optional[RolePrompt]:
        """Run the Generator agent for a single role."""
        if not self.state or not self.state.system_architecture:
            log("错误: state 或 system_architecture 为空", "ERROR")
            return None
        
        role = self.state.system_architecture.roles[role_index]
        log(f"  [Generator] 开始生成角色 {role_index+1}: {role.name}")
        
        self.state.role_states[role_index].status = 'generating'
        self._emit_event('role_state_updated', {
            'roleIndex': role_index,
            'status': 'generating'
        })
        
        try:
            prompt = load_prompt('generator')
            log(f"  [Generator] 提示词加载成功")
        except Exception as e:
            log(f"  [Generator] 提示词加载失败: {e}", "ERROR")
            return None
        
        user_input = self._build_generator_context(role)
        
        output = ""
        
        if self.use_stream:
            chunk_count = 0
            def stream_handler(chunk: str):
                nonlocal output, chunk_count
                output += chunk
                chunk_count += 1
                if on_output:
                    on_output(chunk)
            
            log(f"  [Generator] 调用 LLM (流式)...")
            try:
                self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=stream_handler)
                log(f"  [Generator] LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"  [Generator] LLM 调用失败: {e}", "ERROR")
                return None
        else:
            log(f"  [Generator] 调用 LLM (同步)...")
            try:
                output = self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=None)
                log(f"  [Generator] LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"  [Generator] LLM 调用失败: {e}", "ERROR")
                return None
        
        # Parse response
        data = parse_json_response(output)
        if data:
            log(f"  [Generator] JSON 解析成功")
            # 清理 prompt 内容，确保是纯文本
            raw_prompt = data.get('prompt', '')
            clean_prompt = self._clean_prompt_content(raw_prompt)
            
            role_prompt = RolePrompt(
                role_id=data.get('role_id', role.id),
                role_name=data.get('role_name', role.name),
                role_type=data.get('role_type', role.type),
                description=data.get('description', role.description),
                prompt=clean_prompt,
                input_template=data.get('input_template', ''),
                output_format=data.get('output_format', ''),
                triggers=data.get('triggers', role.triggers)
            )
        else:
            log(f"  [Generator] JSON 解析失败，使用原始输出作为提示词", "WARN")
            # 尝试从原始输出中提取 prompt
            clean_prompt = self._clean_prompt_content(output)
            role_prompt = RolePrompt(
                role_id=role.id,
                role_name=role.name,
                role_type=role.type,
                description=role.description,
                prompt=clean_prompt,
                triggers=role.triggers
            )
        
        self.state.role_states[role_index].prompt = role_prompt.prompt
        log(f"  [Generator] 角色 {role.name} 生成完成 ✓")
        return role_prompt

    def run_reviewer(
        self,
        role_prompt: RolePrompt,
        on_output: Optional[Callable[[str], None]] = None
    ) -> Optional[ReviewResult]:
        """Run the Reviewer agent."""
        log(f"  [Reviewer] 开始审核: {role_prompt.role_name}")
        
        try:
            prompt = load_prompt('reviewer')
        except Exception as e:
            log(f"  [Reviewer] 提示词加载失败: {e}", "ERROR")
            return None
        
        user_input = f"""## 待审核的角色提示词

角色ID：{role_prompt.role_id}
角色名称：{role_prompt.role_name}
角色类型：{role_prompt.role_type}
角色描述：{role_prompt.description}

## 完整提示词内容
```
{role_prompt.prompt}
```

## 输入模板
{role_prompt.input_template or '无'}

## 触发条件
{'、'.join(role_prompt.triggers) or '无'}

请审核这个角色的提示词质量。"""
        
        output = ""
        
        if self.use_stream:
            def stream_handler(chunk: str):
                nonlocal output
                output += chunk
                if on_output:
                    on_output(chunk)
            
            try:
                self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=stream_handler)
                log(f"  [Reviewer] LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"  [Reviewer] LLM 调用失败: {e}", "ERROR")
                return ReviewResult(score=7.0, strengths=[], weaknesses=[], suggestions=[])
        else:
            try:
                output = self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=None)
                log(f"  [Reviewer] LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"  [Reviewer] LLM 调用失败: {e}", "ERROR")
                return ReviewResult(score=7.0, strengths=[], weaknesses=[], suggestions=[])
        
        data = parse_json_response(output)
        if not data:
            log(f"  [Reviewer] JSON 解析失败，使用默认评分 7.0", "WARN")
            return ReviewResult(score=7.0, strengths=[], weaknesses=[], suggestions=[])
        
        score = data.get('score', 7.0)
        log(f"  [Reviewer] 审核完成，评分: {score}")
        
        # Filter to only valid fields for each dataclass
        weakness_fields = {'issue', 'severity', 'location', 'impact'}
        suggestion_fields = {'priority', 'suggestion', 'example'}
        
        weaknesses = [
            WeaknessItem(**{k: v for k, v in w.items() if k in weakness_fields}) if isinstance(w, dict) else WeaknessItem(issue=str(w), severity='中', location='')
            for w in data.get('weaknesses', [])
        ]
        suggestions = [
            SuggestionItem(**{k: v for k, v in s.items() if k in suggestion_fields}) if isinstance(s, dict) else SuggestionItem(priority='中', suggestion=str(s))
            for s in data.get('suggestions', [])
        ]
        
        return ReviewResult(
            score=score,
            strengths=data.get('strengths', []),
            weaknesses=weaknesses,
            suggestions=suggestions,
            verdict=data.get('verdict'),
            dimensions=data.get('dimensions'),
            role_id=data.get('role_id'),
            role_name=data.get('role_name')
        )
    
    def run_optimizer(
        self,
        role_prompt: RolePrompt,
        review_output: str,
        on_output: Optional[Callable[[str], None]] = None
    ) -> Optional[RolePrompt]:
        """Run the Optimizer agent."""
        log(f"  [Optimizer] 开始优化: {role_prompt.role_name}")
        
        try:
            prompt = load_prompt('optimizer')
        except Exception as e:
            log(f"  [Optimizer] 提示词加载失败: {e}", "ERROR")
            return None
        
        user_input = f"""## 原始角色提示词

角色ID：{role_prompt.role_id}
角色名称：{role_prompt.role_name}
角色类型：{role_prompt.role_type}

### 完整提示词
```
{role_prompt.prompt}
```

### 输入模板
{role_prompt.input_template or '无'}

## 审核报告
{review_output}

请根据审核报告优化这个角色的提示词。"""
        
        output = ""
        
        if self.use_stream:
            def stream_handler(chunk: str):
                nonlocal output
                output += chunk
                if on_output:
                    on_output(chunk)
            
            try:
                self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=stream_handler)
                log(f"  [Optimizer] LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"  [Optimizer] LLM 调用失败: {e}", "ERROR")
                return None
        else:
            try:
                output = self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=None)
                log(f"  [Optimizer] LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"  [Optimizer] LLM 调用失败: {e}", "ERROR")
                return None
        
        data = parse_json_response(output)
        
        # 如果 JSON 解析完全失败，尝试从输出中提取提示词内容
        if not data:
            log(f"  [Optimizer] JSON 解析失败，尝试提取提示词内容", "WARN")
            # 尝试提取 XML 标签包裹的内容作为提示词
            import re
            # 查找 <role>...</role> 或类似的结构
            xml_match = re.search(r'(<(?:role|system|prompt|task)>[\s\S]*</(?:role|system|prompt|task)>)', output)
            if xml_match:
                extracted_prompt = xml_match.group(1)
                log(f"  [Optimizer] 从输出中提取到提示词内容，长度: {len(extracted_prompt)}")
                data = {'prompt': extracted_prompt, '_extracted': True}
            else:
                # 如果没有 XML 结构，检查是否输出本身就是提示词
                if len(output) > 500 and ('<' in output or '#' in output):
                    log(f"  [Optimizer] 使用原始输出作为提示词")
                    data = {'prompt': output.strip(), '_raw': True}
                else:
                    return None
        
        # 清理 prompt 内容
        raw_prompt = data.get('prompt', role_prompt.prompt)
        clean_prompt = self._clean_prompt_content(raw_prompt)
        
        log(f"  [Optimizer] 优化完成 ✓")
        return RolePrompt(
            role_id=data.get('role_id', role_prompt.role_id),
            role_name=data.get('role_name', role_prompt.role_name),
            role_type=data.get('role_type', role_prompt.role_type),
            description=data.get('description', role_prompt.description),
            prompt=clean_prompt,
            input_template=data.get('input_template', ''),
            output_format=data.get('output_format', ''),
            triggers=data.get('triggers', role_prompt.triggers)
        )

    def process_role(
        self,
        role_index: int,
        on_output: Optional[Callable[[str], None]] = None
    ) -> Optional[RolePrompt]:
        """Process a single role through generate-review-optimize cycle."""
        total_roles = len(self.state.role_states) if self.state else 0
        log(f"---------- [2/5] 处理角色 {role_index+1}/{total_roles} ----------")
        
        if self._check_cancelled():
            log("流水线已取消", "WARN")
            return None
        
        # Generate
        role_prompt = self.run_generator(role_index, on_output)
        if not role_prompt:
            log(f"角色 {role_index+1} 生成失败", "ERROR")
            self.state.role_states[role_index].status = 'error'
            return None
        
        # Review-Optimize cycle
        current_prompt = role_prompt
        iteration = 0
        review = None
        
        while iteration < self.MAX_ITERATIONS:
            if self._check_cancelled():
                log("流水线已取消", "WARN")
                return None
            
            iteration += 1
            log(f"  迭代 {iteration}/{self.MAX_ITERATIONS}")
            
            self.state.role_states[role_index].status = 'reviewing'
            self._emit_event('role_state_updated', {
                'roleIndex': role_index,
                'status': 'reviewing'
            })
            
            review = self.run_reviewer(current_prompt, on_output)
            if not review:
                log(f"  审核失败，跳出循环", "WARN")
                break
            
            self.state.role_states[role_index].review = review
            self.state.role_states[role_index].iterations = iteration
            
            log(f"  评分: {review.score}, 通过阈值: {self.PASS_SCORE}")
            
            if review.score >= self.PASS_SCORE:
                log(f"  评分达标，跳出循环 ✓")
                break
            
            if iteration >= self.MAX_ITERATIONS:
                log(f"  达到最大迭代次数，跳出循环")
                break
            
            # Optimize
            if self._check_cancelled():
                return None
            
            self.state.role_states[role_index].status = 'optimizing'
            self._emit_event('role_state_updated', {
                'roleIndex': role_index,
                'status': 'optimizing'
            })
            
            # Build review output string for optimizer
            review_output = f"""评分: {review.score}
优点: {', '.join(review.strengths) if review.strengths else '无'}
缺点: {'; '.join([f"{w.issue}({w.severity})" for w in review.weaknesses]) if review.weaknesses else '无'}
建议: {'; '.join([f"{s.suggestion}({s.priority})" for s in review.suggestions]) if review.suggestions else '无'}
结论: {review.verdict or '无'}"""
            
            optimized = self.run_optimizer(current_prompt, review_output, on_output)
            if optimized:
                current_prompt = optimized
                self.state.role_states[role_index].prompt = optimized.prompt
        
        # Mark completed
        self.state.role_states[role_index].status = 'completed'
        self.state.role_states[role_index].final_score = review.score if review else 0.0
        log(f"---------- 角色 {role_index+1} 处理完成，最终评分: {self.state.role_states[role_index].final_score} ----------")
        
        # 增量保存：立即保存已完成的角色结果
        self._save_role_result(role_index, current_prompt)
        
        self._emit_event('role_state_updated', {
            'roleIndex': role_index,
            'status': 'completed',
            'score': self.state.role_states[role_index].final_score
        })
        
        return current_prompt
    
    def run_tester(
        self,
        prompts: List[RolePrompt],
        on_output: Optional[Callable[[str], None]] = None
    ) -> Optional[TestResult]:
        """Run the Tester agent."""
        log(f"---------- [4/5] Tester 开始 ----------")
        log(f"测试 {len(prompts)} 个角色的提示词")
        self._emit_event('agent_started', {'agent': 'tester'})
        
        # Build test input
        suite_json = {
            'system_name': self.state.system_architecture.system_name if self.state.system_architecture else '',
            'prompts': [
                {
                    'role_id': p.role_id,
                    'role_name': p.role_name,
                    'role_type': p.role_type,
                    'prompt': p.prompt[:500]  # Truncate for context
                }
                for p in prompts
            ]
        }
        
        try:
            prompt = load_prompt('tester')
            log(f"Tester 提示词加载成功")
        except Exception as e:
            log(f"Tester 提示词加载失败: {e}", "ERROR")
            return None
        
        user_input = f"请为以下提示词套件生成测试报告：\n\n{suite_json}"
        
        output = ""
        
        if self.use_stream:
            chunk_count = 0
            def stream_handler(chunk: str):
                nonlocal output, chunk_count
                output += chunk
                chunk_count += 1
                if on_output:
                    on_output(chunk)
                self._emit_event('agent_output', {'agent': 'tester', 'chunk': chunk})
            
            log(f"调用 LLM (流式)...")
            try:
                self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=stream_handler)
                log(f"LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"LLM 调用失败: {e}", "ERROR")
                self._emit_event('agent_completed', {'agent': 'tester', 'success': False})
                return None
        else:
            log(f"调用 LLM (同步)...")
            try:
                output = self.llm_client.run_agent(prompt, user_input, self.state.model, on_stream=None)
                log(f"LLM 完成，输出长度: {len(output)}")
            except Exception as e:
                log(f"LLM 调用失败: {e}", "ERROR")
                self._emit_event('agent_completed', {'agent': 'tester', 'success': False})
                return None
        
        data = parse_json_response(output)
        self._emit_event('agent_completed', {'agent': 'tester', 'success': data is not None})
        
        if not data:
            log(f"JSON 解析失败", "WARN")
            return None
        
        # Parse test result (simplified)
        from app.models.pipeline import TestSummary, TestCase, TestIssue
        
        summary_data = data.get('summary', {})
        summary = TestSummary(
            total_tests=summary_data.get('total_tests', 0),
            passed=summary_data.get('passed', 0),
            failed=summary_data.get('failed', 0),
            warnings=summary_data.get('warnings', 0),
            pass_rate=summary_data.get('pass_rate', 0.0),
            verdict=summary_data.get('verdict', '')
        )
        
        log(f"---------- [4/5] Tester 完成 ✓ ----------")
        log(f"测试结果: {summary.passed}/{summary.total_tests} 通过, 通过率: {summary.pass_rate}")
        
        # Filter to valid fields only
        test_case_fields = {'id', 'category', 'name', 'input', 'expected', 'actual', 'status', 'notes'}
        test_issue_fields = {'severity', 'test_id', 'description', 'recommendation'}
        
        return TestResult(
            summary=summary,
            test_cases=[TestCase(**{k: v for k, v in tc.items() if k in test_case_fields}) for tc in data.get('test_cases', [])],
            issues_found=[TestIssue(**{k: v for k, v in i.items() if k in test_issue_fields}) for i in data.get('issues_found', [])],
            recommendations=data.get('recommendations', [])
        )
    
    def assemble_suite(self, prompts: List[RolePrompt]) -> PromptSuite:
        """Assemble the final PromptSuite."""
        log(f"---------- [5/5] 组装最终套件 ----------")
        arch = self.state.system_architecture
        suite = PromptSuite(
            system_name=arch.system_name if arch else '',
            total_roles=len(prompts),
            prompts=prompts,
            workflow_summary=arch.workflow.description if arch and arch.workflow else '',
            integration_notes=f"包含 {len(prompts)} 个角色的提示词套件"
        )
        log(f"套件组装完成: {suite.system_name}, {suite.total_roles} 个角色")
        
        # 保存最终结果到 result 目录
        self._save_final_result(suite)
        
        log(f"========== 流水线完成 ==========")
        
        # 清理任务进度文件（任务完成）
        if self.state:
            self._storage.delete_task_progress(self.state.task_id)
        
        return suite
    
    def _save_final_result(self, suite: PromptSuite) -> None:
        """Save final result to result directory.
        
        注意：每个角色的 md 文件已经在 _save_role_result 中立即保存了，
        这里只需要保存概览文件和 JSON 备份。
        """
        if not self.state or not self._task_dir:
            return
        
        try:
            import json
            
            # 保存概览文件
            overview_content = self._generate_overview_md(suite)
            overview_file = self._task_dir / '0_概览.md'
            overview_file.write_text(overview_content, encoding='utf-8')
            log(f"概览文件已保存: {overview_file}")
            
            # 保存 JSON 备份（用于导入/导出）
            data = {
                'requirement': {
                    'description': self.state.description,
                    'type': self.state.prompt_type,
                    'target_model': self.state.model
                },
                'promptSuite': {
                    'system_name': suite.system_name,
                    'total_roles': suite.total_roles,
                    'prompts': [self._serialize_role_prompt(p) for p in suite.prompts],
                    'workflow_summary': suite.workflow_summary,
                    'integration_notes': suite.integration_notes
                },
                'savedAt': datetime.now().isoformat()
            }
            
            json_file = self._task_dir / '_data.json'
            json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            log(f"JSON 备份已保存: {json_file}")
            
            self._emit_event('suite_saved', {
                'folder': self._task_dir.name,
                'path': str(self._task_dir)
            })
        except Exception as e:
            log(f"保存结果失败: {e}", "ERROR")
    
    def _generate_overview_md(self, suite: PromptSuite) -> str:
        """Generate overview markdown for the suite."""
        roles_table = '\n'.join(
            f"| {i+1} | {p.role_name} | {p.role_type} | {p.description[:50]}{'...' if len(p.description) > 50 else ''} |"
            for i, p in enumerate(suite.prompts)
        )
        
        return f"""# {suite.system_name}

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 角色数量: {suite.total_roles}

## 需求描述

{self.state.description if self.state else ''}

## 角色列表

| 序号 | 角色名称 | 类型 | 描述 |
|------|----------|------|------|
{roles_table}

## 工作流程

{suite.workflow_summary or ''}

## 集成说明

{suite.integration_notes or ''}
"""
    
    def process_roles_parallel(
        self,
        role_indices: List[int] = None,
        on_output: Optional[Callable[[str], None]] = None
    ) -> List[RolePrompt]:
        """Process multiple roles in parallel (并行执行)."""
        if not self.state or not self.state.role_states:
            return []
        
        # 如果没有指定，处理所有未完成的角色
        if role_indices is None:
            role_indices = self.get_pending_role_indices()
        
        if not role_indices:
            log("没有需要处理的角色")
            return list(self._completed_prompts.values())
        
        total = len(role_indices)
        log(f"---------- 并行处理 {total} 个角色 (最大并发: {self._max_parallel}) ----------")
        
        from concurrent.futures import as_completed
        
        futures = {}
        results = {}
        
        # 提交所有任务
        for idx in role_indices:
            if self._check_cancelled():
                break
            future = self._executor.submit(self.process_role, idx, on_output)
            futures[future] = idx
        
        # 收集结果
        for future in as_completed(futures):
            if self._check_cancelled():
                break
            idx = futures[future]
            try:
                result = future.result()
                if result:
                    results[idx] = result
                    log(f"角色 {idx+1} 并行处理完成 ✓")
                else:
                    log(f"角色 {idx+1} 并行处理失败", "ERROR")
            except Exception as e:
                log(f"角色 {idx+1} 并行处理异常: {e}", "ERROR")
        
        # 合并已完成的结果（按索引排序）
        all_prompts = {**self._completed_prompts, **results}
        sorted_prompts = [all_prompts[i] for i in sorted(all_prompts.keys())]
        
        log(f"并行处理完成: {len(sorted_prompts)}/{len(self.state.role_states)} 个角色成功")
        return sorted_prompts
    
    def run_full_pipeline(
        self,
        parallel: bool = True,
        on_output: Optional[Callable[[str], None]] = None
    ) -> Optional[PromptSuite]:
        """Run the complete pipeline with optional parallel processing."""
        if not self.state:
            log("错误: 流水线未启动", "ERROR")
            return None
        
        # Step 1: Analyzer
        arch = self.run_analyzer(on_output)
        if not arch:
            log("Analyzer 失败", "ERROR")
            return None
        
        # 保存初始进度
        self._save_progress()
        
        # Step 2-3: Process roles (parallel or sequential)
        if parallel and self._max_parallel > 1:
            prompts = self.process_roles_parallel(on_output=on_output)
        else:
            prompts = []
            for i in range(len(self.state.role_states)):
                if self._check_cancelled():
                    break
                result = self.process_role(i, on_output)
                if result:
                    prompts.append(result)
        
        if not prompts:
            log("没有成功生成的提示词", "ERROR")
            return None
        
        # Step 4: Tester (optional, can fail)
        self.run_tester(prompts, on_output)
        
        # Step 5: Assemble
        suite = self.assemble_suite(prompts)
        self.state.prompt_suite = suite
        self.state.status = 'completed'
        
        return suite
    
    def resume_pipeline(
        self,
        task_id: str,
        parallel: bool = True,
        on_output: Optional[Callable[[str], None]] = None
    ) -> Optional[PromptSuite]:
        """Resume a previously interrupted pipeline (断点恢复)."""
        if not self.load_progress(task_id):
            return None
        
        log(f"========== 恢复流水线执行 ==========")
        log(f"任务ID: {task_id}")
        log(f"已完成: {len(self._completed_prompts)} 个角色")
        
        # 恢复任务结果目录
        if self.state:
            self._task_dir = self._storage.get_or_create_task_dir(self.state.description, task_id)
            log(f"结果目录: {self._task_dir}")
        
        pending = self.get_pending_role_indices()
        log(f"待处理: {len(pending)} 个角色")
        
        if not pending:
            # 所有角色已完成，直接组装
            prompts = [self._completed_prompts[i] for i in sorted(self._completed_prompts.keys())]
        else:
            # 处理剩余角色
            if parallel and self._max_parallel > 1:
                prompts = self.process_roles_parallel(pending, on_output)
            else:
                for i in pending:
                    if self._check_cancelled():
                        break
                    self.process_role(i, on_output)
                prompts = [self._completed_prompts[i] for i in sorted(self._completed_prompts.keys())]
        
        if not prompts:
            log("没有成功生成的提示词", "ERROR")
            return None
        
        # Tester and assemble
        self.run_tester(prompts, on_output)
        suite = self.assemble_suite(prompts)
        self.state.prompt_suite = suite
        self.state.status = 'completed'
        
        return suite
