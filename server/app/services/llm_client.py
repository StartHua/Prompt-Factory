# -*- coding: utf-8 -*-
"""LLM client service for OpenAI API calls."""

from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI


def log(msg: str, level: str = "INFO"):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [LLM] [{level}] {msg}", flush=True)


@dataclass
class ChatMessage:
    """Chat message structure."""
    role: str  # 'system', 'user', 'assistant'
    content: str


class LLMClient:
    """Client for LLM API calls."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.apiyi.com/v1"):
        """Initialize LLM client.
        
        Args:
            api_key: OpenAI API key
            base_url: API base URL
        """
        # 确保 base_url 格式正确
        if not base_url.endswith('/v1'):
            if base_url.endswith('/'):
                base_url = base_url + 'v1'
            else:
                base_url = base_url + '/v1'
        
        self.client = OpenAI(
            api_key=api_key, 
            base_url=base_url,
            timeout=120.0,  # 增加超时时间
        )
        self.api_key = api_key
        self.base_url = base_url
        log(f"LLMClient 初始化: base_url={base_url}, api_key={api_key[:10] if api_key else 'None'}...")
    
    def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        stream: bool = False,
        max_tokens: Optional[int] = None,
        on_stream: Optional[Callable[[str], None]] = None
    ) -> str:
        """Call LLM chat API.
        
        Args:
            messages: List of chat messages
            model: Model name
            stream: Whether to stream response
            max_tokens: Maximum tokens in response
            on_stream: Callback for streaming chunks
            
        Returns:
            Complete response content
        """
        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
        
        # 打印完整的请求 URL
        request_url = f"{self.base_url}/chat/completions"
        log(f"请求 URL: {request_url}")
        log(f"调用 API: model={model}, stream={stream}, messages={len(messages)}条")
        log(f"  api_key: {self.api_key[:15] if self.api_key else 'None'}...")
        log(f"  system prompt 长度: {len(messages[0].content) if messages else 0}")
        log(f"  user message 长度: {len(messages[1].content) if len(messages) > 1 else 0}")
        
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": msg_dicts,
            "stream": stream
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        try:
            if stream:
                log(f"开始流式请求...")
                response = self.client.chat.completions.create(**kwargs)
                full_content = ""
                chunk_count = 0
                
                for chunk in response:
                    # 处理不同的响应格式
                    try:
                        # 如果 chunk 是字符串，直接使用
                        if isinstance(chunk, str):
                            full_content += chunk
                            chunk_count += 1
                            if on_stream:
                                on_stream(chunk)
                            continue
                        
                        if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            content = ""
                            if hasattr(delta, 'content') and delta.content:
                                content = delta.content
                            elif hasattr(delta, 'text') and delta.text:
                                content = delta.text
                            
                            if content:
                                full_content += content
                                chunk_count += 1
                                if on_stream:
                                    on_stream(content)
                        
                        # 打印第一个 chunk 的结构用于调试
                        if chunk_count <= 1:
                            log(f"  chunk {chunk_count} 类型: {type(chunk)}, 内容: {str(chunk)[:200]}")
                    except Exception as chunk_err:
                        log(f"  处理 chunk 出错: {chunk_err}", "WARN")
                        continue
                
                log(f"流式请求完成: {chunk_count} chunks, {len(full_content)} 字符")
                
                # 如果流式没有内容，尝试同步请求
                if not full_content:
                    log("流式响应为空，尝试同步请求...", "WARN")
                    kwargs["stream"] = False
                    response = self.client.chat.completions.create(**kwargs)
                    log(f"同步响应类型: {type(response)}")
                    
                    # 处理不同类型的响应
                    if isinstance(response, str):
                        full_content = response
                        log(f"响应是字符串: {len(full_content)} 字符")
                    elif hasattr(response, 'choices') and response.choices and len(response.choices) > 0:
                        msg = response.choices[0].message
                        full_content = msg.content or ""
                        log(f"同步请求获取到: {len(full_content)} 字符")
                    else:
                        # 尝试其他方式获取内容
                        log(f"未知响应格式，尝试转换...")
                        full_content = str(response)
                
                return full_content
            else:
                log(f"开始同步请求...")
                response = self.client.chat.completions.create(**kwargs)
                log(f"同步响应类型: {type(response)}")
                
                content = ""
                if isinstance(response, str):
                    content = response
                elif hasattr(response, 'choices') and response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content or ""
                else:
                    content = str(response)
                    
                log(f"同步请求完成: {len(content)} 字符")
                return content
        except Exception as e:
            log(f"API 调用失败: {type(e).__name__}: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            raise
    
    def run_agent(
        self,
        system_prompt: str,
        user_message: str,
        model: str,
        on_stream: Optional[Callable[[str], None]] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Run an agent with system prompt and user message.
        
        Args:
            system_prompt: System prompt for the agent
            user_message: User input message
            model: Model name
            on_stream: Callback for streaming chunks
            max_tokens: Maximum tokens in response
            
        Returns:
            Agent response
        """
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_message)
        ]
        return self.chat(
            messages=messages,
            model=model,
            stream=on_stream is not None,
            max_tokens=max_tokens,
            on_stream=on_stream
        )


# Global instance
_client: Optional[LLMClient] = None


def get_llm_client() -> Optional[LLMClient]:
    """Get the global LLM client instance."""
    return _client


def init_llm_client(api_key: str, base_url: str) -> LLMClient:
    """Initialize the global LLM client."""
    global _client
    _client = LLMClient(api_key=api_key, base_url=base_url)
    return _client
