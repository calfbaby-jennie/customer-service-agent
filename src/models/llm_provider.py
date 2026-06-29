"""LLM provider abstraction backed by LiteLLM.

DeepSeek is the default runtime provider. OpenAI and Claude remain supported by
the provider layer, but their concrete configs are intentionally left commented
out in ``LLM_CONFIGS`` until those keys are needed.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # Allows DEFAULT_LLM=mock smoke tests before deps are installed.
    def load_dotenv(path: Optional[str] = None, *args, **kwargs):  # type: ignore[no-redef]
        env_path = Path(path) if path else Path.cwd() / ".env"
        if not env_path.exists():
            return False

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if " #" in value:
                value = value.split(" #", 1)[0].rstrip()
            os.environ.setdefault(key, value)
        return True


load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    """Runtime LLM configuration."""

    provider: str
    model: str
    api_key_env: Optional[str] = None
    base_url_env: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 2000


class LLMProvider:
    """Unified LLM provider using LiteLLM-compatible model names."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._validate_credentials()

    @property
    def model_name(self) -> str:
        if self.config.provider == "mock":
            return "mock"
        if "/" in self.config.model:
            return self.config.model
        return f"{self.config.provider}/{self.config.model}"

    def _validate_credentials(self) -> None:
        """Validate only credentials that are required for the selected provider."""
        if self.config.provider in {"mock", "ollama"}:
            return

        if self.config.api_key_env and not os.getenv(self.config.api_key_env):
            raise ValueError(
                f"Missing {self.config.api_key_env}. "
                f"Set it in .env or run with DEFAULT_LLM=mock for an offline smoke test."
            )

    def call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call the configured LLM and return text content."""
        if self.config.provider == "mock":
            return self._mock_response(prompt)

        try:
            from litellm import completion
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency: litellm. Run `python -m pip install -r requirements.txt` "
                "or use `DEFAULT_LLM=mock python test_local.py` for an offline smoke test."
            ) from exc

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        api_key = os.getenv(self.config.api_key_env or "")
        if api_key:
            kwargs["api_key"] = api_key

        api_base = os.getenv(self.config.base_url_env or "")
        if api_base:
            kwargs["api_base"] = api_base

        try:
            response = completion(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as exc:
            raise RuntimeError(f"LLM call failed for {self.model_name}: {exc}") from exc

    def call_with_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """Call the LLM and parse a JSON object from the response."""
        json_prompt = (
            f"{prompt}\n\n"
            "只返回一个合法 JSON 对象，不要使用 Markdown 代码块，不要输出额外解释。"
        )
        response = self.call(json_prompt, system_prompt=system_prompt).strip()
        return _parse_json_object(response)

    def _mock_response(self, prompt: str) -> str:
        """Deterministic local response for smoke tests without network access."""
        content = prompt.lower()
        ticket_match = re.search(r"工单内容：(.+?)(?:\n\n|$)", prompt, re.DOTALL)
        ticket_text = ticket_match.group(1).strip() if ticket_match else prompt
        is_return_ticket = any(
            keyword in ticket_text
            for keyword in ("退货", "退款", "售后", "质量", "没收到", "未收到", "破损")
        )

        if '"is_return"' in prompt or "是否是退货" in prompt:
            return json.dumps(
                {
                    "is_return": is_return_ticket,
                    "confidence": 0.92 if is_return_ticket else 0.18,
                    "reason": "命中退货/售后关键词" if is_return_ticket else "更像普通咨询，需转其他队列",
                },
                ensure_ascii=False,
            )

        if '"eligible"' in prompt or "是否符合退货条件" in prompt:
            return json.dumps(
                {
                    "eligible": True,
                    "steps": ["核验订单状态", "确认商品状态", "生成退货处理建议"],
                    "compensation": "如物流超时或商品质量问题，可优先免除退货运费。",
                },
                ensure_ascii=False,
            )

        if '"score"' in prompt and "should_auto_send" in prompt:
            return json.dumps(
                {
                    "score": 86,
                    "reasoning": "建议覆盖订单、政策、客户动作和平台动作，风险可控。",
                    "should_auto_send": True,
                    "issues": [],
                },
                ensure_ascii=False,
            )

        if "非退货" in content:
            return "该工单不属于退货/售后自动化范围，建议转人工或对应客服队列继续处理。"

        return (
            "建议批准客户退货申请。请客户保持商品及包装完整，在工单中补充商品照片，"
            "平台核验后生成退货地址并跟进退款；如确认物流超时或商品质量问题，可免除退货运费。"
        )


def _parse_json_object(response: str) -> dict:
    """Parse JSON while tolerating common fenced-code responses."""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"error": "Failed to parse JSON", "raw": response}


def _normalize_config_name(config_name: Optional[str]) -> str:
    raw = config_name or os.getenv("DEFAULT_LLM") or "deepseek"
    # Be tolerant of .env values such as: DEFAULT_LLM=deepseek  # comment
    return raw.split("#", 1)[0].strip()


# Active configs. DeepSeek is the production default; mock is for offline smoke tests.
LLM_CONFIGS = {
    "deepseek": LLMConfig(
        provider="deepseek",
        model="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
    ),
    "deepseek_chat": LLMConfig(
        provider="deepseek",
        model="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
    ),
    "deepseek_reasoner": LLMConfig(
        provider="deepseek",
        model="deepseek-reasoner",
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        temperature=0.1,
    ),
    "mock": LLMConfig(provider="mock", model="mock"),
    "ollama_llama": LLMConfig(
        provider="ollama",
        model="llama2",
        base_url_env="OLLAMA_BASE_URL",
    ),

    # OpenAI 能力保留：需要时取消注释，并在 .env 中配置 OPENAI_API_KEY。
    # "gpt4o_mini": LLMConfig(
    #     provider="openai",
    #     model="gpt-4o-mini",
    #     api_key_env="OPENAI_API_KEY",
    # ),
    # "gpt4o": LLMConfig(
    #     provider="openai",
    #     model="gpt-4o",
    #     api_key_env="OPENAI_API_KEY",
    # ),

    # Claude 能力保留：需要时取消注释，并在 .env 中配置 ANTHROPIC_API_KEY。
    # "claude_sonnet": LLMConfig(
    #     provider="anthropic",
    #     model="claude-3-5-sonnet-latest",
    #     api_key_env="ANTHROPIC_API_KEY",
    # ),
}


def get_llm_provider(config_name: Optional[str] = None) -> LLMProvider:
    """Factory function for the selected LLM provider."""
    normalized_name = _normalize_config_name(config_name)
    config = LLM_CONFIGS.get(normalized_name)
    if not config:
        available = ", ".join(sorted(LLM_CONFIGS))
        raise ValueError(f"Unknown LLM config: {normalized_name}. Available: {available}")
    return LLMProvider(config)
