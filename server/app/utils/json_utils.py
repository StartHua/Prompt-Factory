# -*- coding: utf-8 -*-
"""JSON parsing utilities."""

import json
import re
from typing import TypeVar, Type, Optional, Any

T = TypeVar('T')


def extract_json_from_text(text: str) -> str:
    """Extract JSON from text that may contain markdown code blocks.
    
    Args:
        text: Raw text that may contain JSON in markdown code blocks
        
    Returns:
        Extracted JSON string
    """
    # Try to extract from markdown code block
    json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if json_match:
        return json_match.group(1).strip()
    
    # Try to find raw JSON object
    obj_match = re.search(r'\{[\s\S]*\}', text)
    if obj_match:
        return obj_match.group(0)
    
    # Return original text if no JSON found
    return text.strip()


def parse_json_response(text: str) -> Optional[dict]:
    """Parse JSON from LLM response.
    
    Args:
        text: Raw LLM response text
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        json_str = extract_json_from_text(text)
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 尝试修复常见的 JSON 问题
        try:
            # 移除可能的尾部逗号
            fixed = re.sub(r',\s*}', '}', json_str)
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 prompt 字段（即使整体 JSON 无效）
        prompt_match = re.search(r'"prompt"\s*:\s*"((?:[^"\\]|\\.)*)"|"prompt"\s*:\s*`((?:[^`\\]|\\.)*)`', text)
        if prompt_match:
            prompt_content = prompt_match.group(1) or prompt_match.group(2)
            if prompt_content:
                # 使用 json.loads 来正确解码 JSON 字符串中的转义字符
                try:
                    prompt_content = json.loads(f'"{prompt_content}"')
                except:
                    pass
                return {'prompt': prompt_content, '_partial': True}
        
        return None


def safe_parse_json(text: str, default: Any = None) -> Any:
    """Safely parse JSON with a default fallback.
    
    Args:
        text: Raw text to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed value or default
    """
    result = parse_json_response(text)
    return result if result is not None else default
