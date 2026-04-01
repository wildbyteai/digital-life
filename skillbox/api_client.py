"""
Skill Box — API 调用层
支持 OpenAI 兼容格式的任何 API
"""

import yaml
import requests
from pathlib import Path


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def call(system_prompt: str, user_prompt: str, temperature: float = None) -> str:
    """
    调用 LLM API（OpenAI 兼容格式）

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户输入
        temperature: 温度参数（可选，覆盖配置）

    Returns:
        模型回复文本
    """
    config = load_config()
    api_config = config.get("api", {})

    base_url = api_config.get("base_url", "")
    api_key = api_config.get("api_key", "")
    model = api_config.get("model", "gpt-4o")
    temp = temperature or api_config.get("temperature", 0.9)
    max_tokens = api_config.get("max_tokens", 4096)

    if not base_url or not api_key:
        raise ValueError(
            "❌ 未配置 API！\n"
            "请编辑 skillbox/config.yaml，填入你的 API 地址和密钥。\n"
            "支持任何 OpenAI 兼容格式的 API。"
        )

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temp,
        "max_tokens": max_tokens,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"❌ 无法连接到 {base_url}，请检查 API 地址是否正确。")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"❌ API 返回错误：{resp.status_code} — {resp.text[:200]}")
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"❌ API 返回格式异常：{e}")
