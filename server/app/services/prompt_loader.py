# -*- coding: utf-8 -*-
"""Prompt loader service."""

from pathlib import Path
from typing import Dict, Optional
from app.config import Config


class PromptLoader:
    """Service for loading agent prompts from files."""
    
    AGENT_PROMPTS = {
        'analyzer': 'analyzer.md',
        'generator': 'generator.md',
        'reviewer': 'reviewer.md',
        'optimizer': 'optimizer.md',
        'tester': 'tester.md',
    }
    
    SUPPORTED_LANGUAGES = ['cn', 'en']
    DEFAULT_LANGUAGE = 'cn'
    
    def __init__(self, prompts_dir: Optional[Path] = None, language: str = None):
        """Initialize prompt loader.
        
        Args:
            prompts_dir: Base directory containing prompt files
            language: Language code ('cn' or 'en')
        """
        self.base_prompts_dir = prompts_dir or Config.PROMPTS_DIR
        self._language = language or self.DEFAULT_LANGUAGE
        self._cache: Dict[str, str] = {}
    
    @property
    def language(self) -> str:
        return self._language
    
    @language.setter
    def language(self, value: str):
        if value not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {value}. Supported: {self.SUPPORTED_LANGUAGES}")
        if value != self._language:
            self._language = value
            self.clear_cache()  # Clear cache when language changes
    
    @property
    def prompts_dir(self) -> Path:
        """Get the prompts directory for current language."""
        return self.base_prompts_dir / self._language
    
    def load(self, agent_name: str, language: str = None) -> str:
        """Load prompt for an agent.
        
        Args:
            agent_name: Name of the agent (analyzer, generator, etc.)
            language: Optional language override for this load
            
        Returns:
            Prompt content
            
        Raises:
            ValueError: If agent name is unknown
            FileNotFoundError: If prompt file doesn't exist
        """
        if agent_name not in self.AGENT_PROMPTS:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        # Use provided language or default
        lang = language or self._language
        cache_key = f"{lang}:{agent_name}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load from file
        filename = self.AGENT_PROMPTS[agent_name]
        filepath = self.base_prompts_dir / lang / filename
        
        if not filepath.exists():
            # Fallback to default language if file not found
            fallback_path = self.base_prompts_dir / self.DEFAULT_LANGUAGE / filename
            if fallback_path.exists():
                filepath = fallback_path
            else:
                raise FileNotFoundError(f"Prompt file not found: {filepath}")
        
        content = filepath.read_text(encoding='utf-8')
        self._cache[cache_key] = content
        return content
    
    def clear_cache(self) -> None:
        """Clear the prompt cache."""
        self._cache.clear()


# Global instance
_loader: Optional[PromptLoader] = None
_current_language: str = 'cn'


def get_prompt_loader() -> PromptLoader:
    """Get the global prompt loader instance."""
    global _loader, _current_language
    if _loader is None:
        _loader = PromptLoader(language=_current_language)
    return _loader


def set_language(language: str) -> None:
    """Set the global language for prompt loading."""
    global _current_language, _loader
    if language not in PromptLoader.SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    _current_language = language
    if _loader:
        _loader.language = language


def get_language() -> str:
    """Get the current global language."""
    return _current_language


def load_prompt(agent_name: str, language: str = None) -> str:
    """Load prompt for an agent using the global loader.
    
    Args:
        agent_name: Name of the agent
        language: Optional language override
    """
    return get_prompt_loader().load(agent_name, language)
