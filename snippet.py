"""
代码片段实体类
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any


class Snippet:
    """代码片段实体类"""
    
    def __init__(
        self,
        title: str = "",
        code: str = "",
        language: str = "text",
        description: str = "",
        tags: List[str] = None,
        is_favorite: bool = False,
        id: str = None,
        created_at: str = None,
        updated_at: str = None
    ):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.code = code
        self.language = language
        self.description = description
        self.tags = tags or []
        self.is_favorite = is_favorite
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def get_preview(self, lines: int = 3) -> str:
        """返回代码前N行摘要"""
        code_lines = self.code.split('\n')
        preview_lines = code_lines[:lines]
        preview = '\n'.join(preview_lines)
        if len(code_lines) > lines:
            preview += '...'
        return preview
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'code': self.code,
            'language': self.language,
            'description': self.description,
            'tags': self.tags,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snippet':
        """从字典反序列化"""
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            code=data.get('code', ''),
            language=data.get('language', 'text'),
            description=data.get('description', ''),
            tags=data.get('tags', []),
            is_favorite=data.get('is_favorite', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def update_timestamp(self):
        """更新修改时间"""
        self.updated_at = datetime.now().isoformat()
    
    def __repr__(self):
        return f"<Snippet '{self.title}' ({self.language})>"
