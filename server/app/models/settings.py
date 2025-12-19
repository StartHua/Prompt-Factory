# -*- coding: utf-8 -*-
"""Settings data model."""

from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""
    api_key: str = ""
    base_url: str = "https://api.apiyi.com/v1"
    default_model: str = "claude-sonnet-4-5-20251022"
    use_stream: bool = True  # 是否使用流式输出
    language: str = "cn"  # 语言设置: cn/en
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "apiKey": self.api_key,
            "baseUrl": self.base_url,
            "defaultModel": self.default_model,
            "useStream": self.use_stream,
            "language": self.language
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Create from dictionary."""
        return cls(
            api_key=data.get("apiKey", ""),
            base_url=data.get("baseUrl", "https://api.apiyi.com/v1"),
            default_model=data.get("defaultModel", "claude-sonnet-4-5-20251022"),
            use_stream=data.get("useStream", True),
            language=data.get("language", "cn")
        )
