# -*- coding: utf-8 -*-
"""History data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class HistoryRecord:
    """History record for pipeline execution."""
    id: str
    description: str
    type: str
    system_name: str
    roles_count: int
    score: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    folder_name: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "systemName": self.system_name,
            "rolesCount": self.roles_count,
            "score": self.score,
            "createdAt": self.created_at,
            "folderName": self.folder_name
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HistoryRecord":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            type=data.get("type", ""),
            system_name=data.get("systemName", ""),
            roles_count=data.get("rolesCount", 0),
            score=data.get("score", 0.0),
            created_at=data.get("createdAt", datetime.now().isoformat()),
            folder_name=data.get("folderName")
        )
