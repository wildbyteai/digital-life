"""
Skill Box — API 调用层
支持 OpenAI 兼容格式 API（含 Ollama / LM Studio 等本地部署）
"""

import os
import json
import yaml
import requests
from pathlib import Path


CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


class SkillBoxAPI:
    """LLM API 客户端"""

    def __init__(self):
        cfg = _load_config()
        self.base_url = cfg.get("base_url", os.getenv("SKILLBOX_API_BASE", ""))
        self.api_key = cfg.get("api_key", os.getenv("SKILLBOX_API_KEY", ""))
        self.model = cfg.get("model", os.getenv("SKILLBOX_MODEL", "gpt-4o"))
        self.temperature = cfg.get("temperature", 0.9)
        self.max_tokens = cfg.get("max_tokens", 4096)

    def chat(self, system: str, user: str) -> str:
        """
        发送对话请求

        Args:
            system: 系统提示词
            user: 用户输入

        Returns:
            模型回复
        """
        if not self.base_url or not self.api_key:
            print("⚠️  未配置 API，使用 prompt 模式（输出提示词供手动粘贴到 ChatGPT）")
            print("=" * 50)
            print(f"\n【系统提示词】\n{system}\n")
            print(f"【用户输入】\n{user}\n")
            print("=" * 50)
            print("请将以上内容粘贴到 ChatGPT / Claude 等 AI 助手中。\n")
            return ""

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            resp = requests.post(url, headers=headers, json=body, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到 {self.base_url}")
            print("   请检查网络或 base_url 配置。")
            return ""
        except Exception as e:
            print(f"❌ API 调用失败: {e}")
            return ""
