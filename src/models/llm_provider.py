# src/models/llm_provider.py
from typing import Optional
from litellm import completion
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str  # "openai" / "ollama" / "claude" / "gemini"
    model: str     # "gpt-4" / "llama2" / "claude-3" etc
    temperature: float = 0.7
    max_tokens: int = 2000

class LLMProvider:
    """LLM 统一提供者（使用 LiteLLM）"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._validate_credentials()
    
    def _validate_credentials(self):
        """验证凭证"""
        if self.config.provider == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("Missing OPENAI_API_KEY")
        elif self.config.provider == "ollama":
            # Ollama 通常是本地，不需要 key
            pass
        elif self.config.provider == "claude":
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError("Missing ANTHROPIC_API_KEY")
    
    def call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        统一的 LLM 调用接口
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = completion(
                model=f"{self.config.provider}/{self.config.model}",
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"LLM call failed: {e}")
            raise
    
    def call_with_json(self, prompt: str) -> dict:
        """调用并返回 JSON"""
        # 这个在 Agent 中很有用
        import json
        response = self.call(prompt + "\nRespond in JSON format.")
        try:
            return json.loads(response)
        except:
            # Fallback：尽力从响应中提取 JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Failed to parse JSON", "raw": response}

# 预定义的 LLM 配置
LLM_CONFIGS = {
    "gpt4": LLMConfig(provider="openai", model="gpt-4"),
    "gpt35": LLMConfig(provider="openai", model="gpt-3.5-turbo"),
    "ollama_llama": LLMConfig(provider="ollama", model="llama2"),
    "claude": LLMConfig(provider="claude", model="claude-3-sonnet"),
}

def get_llm_provider(config_name: str = "gpt35") -> LLMProvider:
    """工厂函数：获取 LLM 提供者"""
    config = LLM_CONFIGS.get(config_name)
    if not config:
        raise ValueError(f"Unknown LLM config: {config_name}")
    return LLMProvider(config)