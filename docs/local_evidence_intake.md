# Local Evidence Intake

Local Evidence Intake 是 `digital-life` 的本地隐私预检入口。它在 LLM 分析、profile 写入或 skill package 生成之前，用确定性规则扫描用户主动提供的文本材料。

## 目标

```text
本地材料 → privacy-gate → privacy_report + evidence_bundle → 后续 profile/package 流程
```

它解决的是第一层问题：材料里是否有明显隐私风险，以及后续流程应该用什么权限和引用策略处理。

## 非目标

v0 不做：

- 不登录微信、飞书、小红书、知乎、豆瓣或 B 站。
- 不破解微信数据库。
- 不调用 LLM。
- 不自动脱敏或改写原文。
- 不替代法律、安全或心理风险审查。

## CLI

```bash
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/chat/wechat_redacted_sample.txt --preset chat --json
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/work/feishu_meeting_note_sample.md --preset work --output-dir /tmp/digital-life-evidence
```

Preset：

- `generic`：普通 Markdown / TXT / JSONL。
- `chat`：聊天式文本，额外检测发言人前缀和第三方称谓。
- `work`：会议纪要、工作群、文档评论，额外检测职场称谓和项目线索。

## Python API

```python
import importlib
pg = importlib.import_module("privacy-gate")

result = pg.inspect_text("[朋友A]: 这是一段虚构聊天", preset="chat", source_hint="inline_chat")
```

后续 browser / WebFetch 获取到的文本，在进入 LLM 分析或写入 profile 前，应先调用 `inspect_text()`。

## 输出

`privacy_report` 描述风险、建议权限和准入判断。

`evidence_bundle` 描述可被后续流程引用的证据摘要。它不保存原文，只保存路径、哈希、风险计数、权限、audience、confidence 和摘要。

## 风险规则

v0 覆盖：

- 大陆手机号。
- 18 位身份证号校验码。
- 邮箱。
- token / API key 常见前缀。
- 聊天发言人前缀。
- 职场称谓。
- 地址线索。
- 长段 exact quote。

v0 是 Level 1 静态预检。没有被检测到不代表材料完全安全。
