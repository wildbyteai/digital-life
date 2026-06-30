# Local Evidence Intake v0 设计方案

> 状态：设计稿，待用户审阅批准后再进入实施计划。  
> 项目：[`wildbyteai/digital-life`](https://github.com/wildbyteai/digital-life)  
> 本地路径：`/Users/kyle/Documents/self/AI/digital-life`  
> 基线提交：[`daee44e76fa87afe8cf65bdd20b2a96d0161400f`](https://github.com/wildbyteai/digital-life/commit/daee44e76fa87afe8cf65bdd20b2a96d0161400f)  
> 日期：2026-06-30

## 1. 背景

`digital-life` 当前已经具备一套比较完整的数字人生 Skill 体系：

- 6 个基于数字痕迹的自我考古与经验蒸馏 skill。
- 结构化 Profile + Markdown 报告双格式输出。
- `profile-manager.py` 管理 profile 生命周期。
- `package-manager.py` 支持 Life Skill Package。
- `validation_rules.py` 和 CI 提供结构校验与静态测试。

下一阶段的关键问题不是再增加一个分析 skill，而是补上“真实/半真实材料进入系统前”的可信入口：

```text
用户主动提供材料
→ 本地隐私预检
→ 风险报告
→ 证据包
→ profile / package / 后续 skill 消费
→ CI 回归
```

国内数字生态的材料尤其敏感：微信聊天、QQ 空间、飞书会议纪要、工作群、朋友圈、小红书、知乎、豆瓣和 B 站都可能包含第三方信息、公司信息、身份信息、联系方式、长段原文引用和未授权内容。如果没有本地 hard gate，项目越容易用，隐私风险越大。

## 2. 目标

Local Evidence Intake v0 的目标是建立一个：

```text
本地、只读、确定性、可测试、可 CI 回归的隐私预检与证据包生成入口。
```

它回答三个问题：

1. 这份材料是否包含明显隐私风险？
2. 如果允许进入后续流程，它应该带着什么权限、引用策略和风险摘要进入？
3. 后续 profile / package / skill 如何引用这份材料，而不是直接吞原文？

## 3. 非目标

v0 明确不做：

- 不登录微信、飞书、小红书、知乎、豆瓣、B 站或任何线上平台。
- 不破解微信数据库。
- 不做 browser / WebFetch 运行时拦截。
- 不调用 LLM。
- 不生成完整人格报告。
- 不修改现有 6 个 skill 主流程。
- 不把真实聊天原文写入 profile。
- 不做加密 vault。
- 不做跨 skill 知识图谱。
- 不做长期 monitor / daemon。
- 不做 marketplace 或 Skill Package v2。

v0 是 Level 1 静态预检，不替代法律、安全、心理或合规审查。

## 4. 推荐方案概览

新增一个脚本：

```text
scripts/privacy-gate.py
```

提供两个入口：

1. CLI：给用户、CI 和手动调试使用。
2. Python API：给未来 browser / WebFetch 获取内容后的 agent 流程调用，避免动态内容绕过隐私检查。

推荐链路：

```text
inspect_file(path, preset)
  → 读取本地文件
  → deterministic scanner
  → privacy_report
  → evidence_bundle
  → JSON stdout 或 output-dir
```

未来动态链路预留：

```text
browser / WebFetch 获取文本
  → inspect_text(text, preset, source_hint)
  → privacy_report
  → 只有通过 gate 后才允许 LLM 分析或写入 profile
```

## 5. CLI 设计

### 5.1 基本命令

```bash
python3 scripts/privacy-gate.py inspect <path> --preset generic|chat|work --json
```

示例：

```bash
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/chat/wechat_redacted_sample.txt --preset chat --json
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/work/feishu_meeting_note_sample.md --preset work --json
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/generic/personal_journal_sample.md --preset generic --json
```

### 5.2 可选参数

v0 建议只做少量参数：

```bash
--json                 # 输出单个 JSON 对象到 stdout
--output-dir <dir>     # 写出 privacy_report.json 和 evidence_bundle.json
--fail-on <level>      # low|medium|high|critical，达到或超过该级别时非 0 退出
```

暂不做：

- `--redaction strict|balanced|off`
- 自动改写/脱敏原文
- 批量目录递归扫描
- 多文件 bundle 合并

这些留到后续版本。

### 5.3 stdout 结构

`--json` 输出一个对象，包含两个主要字段：

```json
{
  "privacy_report": {},
  "evidence_bundle": {}
}
```

这样单元测试可以一次解析完整结果；`--output-dir` 再拆成两个文件。

## 6. Python API 设计

为了避免未来 browser / WebFetch 动态获取内容绕过 privacy gate，`scripts/privacy-gate.py` 应把核心逻辑写成可导入函数。

建议函数：

```python
def inspect_text(text: str, *, preset: str, source_hint: str | None = None) -> dict:
    """扫描一段文本，返回包含 privacy_report 和 evidence_bundle 的结果。"""


def inspect_file(path: Path, *, preset: str) -> dict:
    """扫描本地文件，返回包含 privacy_report 和 evidence_bundle 的结果。"""
```

CLI 只负责参数解析和调用 API。

v0 不要求现有 6 个 skill 立即调用 API，但需要在文档和后续 Layer0 规则中明确：任何 browser / WebFetch 获取的文本，在进入 LLM 分析或 profile 写入前，都应先通过 `inspect_text()` 扫描。

## 7. Preset 设计

### 7.1 `generic`

适用于：

- 日记
- 自述
- 公开材料摘录
- 用户手动整理的普通 Markdown / TXT / JSONL

重点检测：

- 手机号
- 身份证号
- 邮箱
- 地址线索
- API key / token
- 长引用

### 7.2 `chat`

适用于：

- 微信 / QQ / Telegram / Slack 式聊天文本
- 脱敏群聊记录
- 用户复制的私聊片段

额外重点检测：

- 行首发言人前缀，例如 `张三:`、`User:`、`[同事A]:`
- 第三方称谓
- 长段连续对话
- 未经授权的他人原话

### 7.3 `work`

适用于：

- 飞书会议纪要
- 工作群摘要
- 文档评论摘录
- 项目复盘

额外重点检测：

- 职场称谓，例如 `x总`、`x经理`、`x工`、`x老师`
- 公司、客户、项目、会议、行动项线索
- token / 链接 / 内部资源路径
- 长引用和第三方发言

## 8. `privacy_report` 结构

`privacy_report` 负责描述风险和准入判断。

建议结构：

```json
{
  "schema_version": "0.1.0",
  "input": {
    "path": "examples/evidence_fixtures/chat/wechat_redacted_sample.txt",
    "preset": "chat",
    "size_bytes": 2048,
    "sha256": "<computed_sha256>"
  },
  "status": "warn",
  "risk_level": "medium",
  "risk_counts": {
    "phone": 0,
    "id_card": 0,
    "email": 0,
    "address": 0,
    "bank_card": 0,
    "api_key_or_token": 0,
    "third_party_name_or_alias": 3,
    "company_or_project": 1,
    "speaker_prefix": 4,
    "work_title": 0,
    "long_exact_quote": 2
  },
  "warnings": [
    {
      "code": "third_party_present",
      "severity": "medium",
      "message": "检测到第三方称谓或发言人前缀，后续输出不得公开引用原文。"
    }
  ],
  "recommended_permission": "private_only",
  "recommended_audience": "owner_only",
  "recommended_quote_policy": "do_not_quote",
  "redaction_status": "partially_redacted",
  "allowed_for_profile": true,
  "allowed_for_public_demo": false
}
```

### 8.1 字段约束

应复用现有枚举：

- `permission`：复用 `validation_rules.py` 中的 `PERMISSION_VALUES`。
- `audience`：复用 `validation_rules.py` 中的 `AUDIENCE_VALUES`。
- `confidence`：复用 `validation_rules.py` 中的 `CONFIDENCE_VALUES`。

### 8.2 `quote_policy` 说明

现有 `PERMISSION_VALUES` 中已经包含 `do_not_quote`。因此正式实现时有两个选择：

1. 把 `do_not_quote` 继续作为 `permission` 值使用，不新增 `quote_policy`。
2. 保留 `quote_policy`，但明确它是引用策略，不是权限等级。

v0 推荐保留 `recommended_quote_policy`，但仅作为报告建议字段；后续如果发现与 `permission` 重复，再合并。

## 9. `evidence_bundle` 结构

`evidence_bundle` 负责让后续 skill 引用证据，而不是直接吞原文。

二次评审指出，结构应向现有 Skill Package manifest 的 `sources` 对齐，使用 `id` / `type`，不要使用 `source_id` / `source_type`。

建议结构：

```json
{
  "schema_version": "0.1.0",
  "bundle_id": "evidence_bundle_wechat_redacted_sample",
  "sources": [
    {
      "id": "src_wechat_redacted_sample",
      "type": "chat_export_redacted",
      "path": "examples/evidence_fixtures/chat/wechat_redacted_sample.txt",
      "sha256": "<computed_sha256>",
      "permission": "private_only",
      "audience": "owner_only",
      "confidence": "low",
      "redaction_status": "partially_redacted",
      "third_party_present": true,
      "source_summary": "虚构脱敏微信聊天样本，用于测试第三方称谓、发言人前缀和长引用检测。",
      "time_range": {
        "start": null,
        "end": null
      },
      "risk_counts": {
        "third_party_name_or_alias": 3,
        "speaker_prefix": 4,
        "long_exact_quote": 2
      }
    }
  ],
  "evidence": [
    {
      "id": "evidence_privacy_gate_result",
      "claim": "该样本包含第三方发言线索和长引用风险，后续输出不得公开引用原文。",
      "source_ids": ["src_wechat_redacted_sample"],
      "confidence": "high",
      "status": "needs_review",
      "permission": "private_only"
    }
  ]
}
```

### 9.1 不保存原文

`evidence_bundle` 不保存用户原文，只保存：

- 路径
- 哈希
- 摘要
- 风险计数
- 权限
- audience
- confidence
- redaction status

### 9.2 与 Profile 的关系

Profile 中已有 `evidence_trace` 使用 `source_id` / `source_type`。v0 不立即迁移 Profile 结构。

后续如果要让 Profile 直接消费 `evidence_bundle`，可以在转换层中映射：

```text
evidence_bundle.sources[].id   → profile.evidence_trace[].source_id
evidence_bundle.sources[].type → profile.evidence_trace[].source_type
```

这样 v0 既对齐 Skill Package，又不破坏现有 Profile。

## 10. 风险检测规则

### 10.1 手机号

检测大陆手机号，兼容 `+86`、`86`、空格和连字符：

```text
+86 138 0013 8000
13800138000
138-0013-8000
```

实现应先规范化候选字符串，再判断。

### 10.2 身份证号

检测 18 位身份证号，并实现 ISO 7064:1983.MOD 11-2 校验码，降低把订单号误判成身份证的概率。

### 10.3 邮箱

检测常规邮箱模式：

```text
name@example.com
```

### 10.4 银行卡

v0 可以先做弱检测：连续 16-19 位数字触发 low/medium warning，不做完整银行卡 BIN 校验。

### 10.5 API key / token

检测常见前缀：

```text
sk-
ghp_
gho_
ghu_
ghs_
ghr_
xoxb-
xoxp-
AKIA
```

### 10.6 第三方姓名 / 称谓

v0 不做复杂中文姓名识别，只做保守规则：

- `[同事A]`
- `[朋友B]`
- `[他人姓名]`
- `张三:` 这类行首发言人前缀
- `User:` / `用户A:` / `对方:`

### 10.7 职场称谓

`work` preset 检测：

```text
王总
李经理
张工
陈老师
客户A
供应商B
项目X
```

### 10.8 长引用

触发条件：

- 单行超过 120 个字符。
- Markdown blockquote 单块超过 120 个字符。
- 连续聊天行累计超过阈值。

触发后推荐：

```json
{
  "recommended_quote_policy": "do_not_quote",
  "allowed_for_public_demo": false
}
```

### 10.9 地址

v0 做弱检测，匹配常见地名后缀：

```text
省、市、区、县、路、街、号、室、小区、大厦
```

地址检测容易误报，应默认 medium 以下 warning。

## 11. 风险级别与准入策略

建议风险级别：

```text
none
low
medium
high
critical
```

建议准入策略：

| 风险 | 默认处理 |
|---|---|
| `none` | 可进入 profile，仍需保留 source summary |
| `low` | 可进入 profile，标记 `low` risk |
| `medium` | 可进入 profile，但默认 `private_only` / `owner_only` |
| `high` | 不建议进入 LLM 分析，除非用户明确脱敏后重试 |
| `critical` | 阻断，禁止进入 profile/package |

v0 的 CLI 可用 `--fail-on high` 在 CI 或严格模式下阻断。

## 12. Fixtures 设计

新增目录：

```text
examples/evidence_fixtures/
```

首批 fixture：

```text
examples/evidence_fixtures/README.md
examples/evidence_fixtures/chat/wechat_redacted_sample.txt
examples/evidence_fixtures/work/feishu_meeting_note_sample.md
examples/evidence_fixtures/generic/personal_journal_sample.md
```

### 12.1 `wechat_redacted_sample.txt`

用途：模拟虚构、脱敏的微信聊天文本。

应包含：

- 行首发言人前缀。
- 第三方占位符，例如 `[朋友A]`。
- 一段超过 120 字的长聊天引用。
- 明确声明该文件是 fictional demo。

### 12.2 `feishu_meeting_note_sample.md`

用途：模拟虚构飞书会议纪要。

应包含：

- 发言人。
- 行动项。
- 虚构项目名称。
- 职场称谓，例如 `王总`、`李经理`。
- 一个内部链接或 token-like 占位字符串。

### 12.3 `personal_journal_sample.md`

用途：模拟个人日记。

应包含：

- 虚构地址线索。
- 个人情绪描述。
- 邮箱或手机号占位。
- 明确标注不是诊断材料。

所有 fixture 必须是虚构数据，不得来自真实用户。

## 13. 测试策略

### 13.1 单元测试

在 `scripts/test_scripts.py` 中增加测试类，覆盖：

- CLI help 可运行。
- `inspect_text()` 输出结构稳定。
- `inspect_file()` 输出结构稳定。
- 不存在路径返回非 0。
- 目录路径返回非 0。
- 空文件返回明确 warning 或错误。
- 手机号检测。
- 身份证校验码检测。
- 邮箱检测。
- token 检测。
- speaker prefix 检测。
- work title 检测。
- long exact quote 检测。
- `evidence_bundle.sources[].id/type` 存在。
- `permission` / `audience` / `confidence` 使用现有枚举。

### 13.2 CI

优先通过 unit tests 覆盖，避免 workflow 命令膨胀。

可在 `.github/workflows/validate.yml` 中保留现有：

```bash
python3 -m unittest discover -s scripts -p 'test_scripts.py'
```

如果需要显式 smoke test，可新增：

```bash
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/chat/wechat_redacted_sample.txt --preset chat --json
```

### 13.3 Schema 校验

v0 可以先用 Python validator 校验输出结构，不强制新增 JSON Schema。

如果新增 schema，建议：

```text
schemas/privacy_report.schema.json
schemas/evidence_bundle.schema.json
```

但为控制范围，v0 可以只在 `validation_rules.py` 中新增轻量校验函数。

## 14. 文档变更

### 14.1 新增文档

建议新增：

```text
docs/local_evidence_intake.md
```

内容包括：

- 为什么需要 privacy gate。
- CLI 用法。
- Python API 用法。
- Preset 说明。
- 风险等级说明。
- v0 边界。

### 14.2 更新 README

README 只加简短链接，不做大规模首屏改造：

```text
如果你要用聊天记录、会议纪要或工作文本作为输入，请先阅读 Local Evidence Intake。
```

### 14.3 更新 SKILL.md / Layer0

正式实现后，应补一条硬规则：

```text
任何通过 browser、WebFetch、文件或用户粘贴获得的高敏材料，在分析、总结或写入 profile 前，必须先经过 privacy gate；未通过时不得引用原文或写入 profile。
```

v0 如果暂不修改 6 个 skill prompt，也至少在 `SKILL.md` 总入口说明该规则。

## 15. 实施切分建议

后续进入 implementation plan 时，建议分成以下步骤：

1. 新增 fixture 目录和 3 个虚构样本。
2. 新增 `privacy-gate.py` 的 API skeleton 和 CLI parser。
3. 实现 deterministic scanner。
4. 实现 `privacy_report` 输出。
5. 实现 `evidence_bundle` 输出，使用 `id` / `type` 对齐 Skill Package。
6. 增加 unit tests。
7. 增加文档 `docs/local_evidence_intake.md`。
8. 在 README / SKILL.md 添加最小入口说明。
9. 运行现有全部验证命令。

## 16. 风险与缓解

### 16.1 范围膨胀

风险：从 privacy gate 扩张成平台 adapter、vault、LLM 报告或知识图谱。

缓解：v0 只做本地文本、deterministic scanner、report、bundle、tests。

### 16.2 误报 / 漏报

风险：正则规则不能理解复杂中文语境。

缓解：明确声明 Level 1 静态预检；风险等级保守；对模糊项给 warning 而不是强结论。

### 16.3 与现有 schema 冲突

风险：Profile 使用 `source_id` / `source_type`，Skill Package 使用 `id` / `type`。

缓解：`evidence_bundle` 对齐 Skill Package；未来 Profile 消费用映射层转换。

### 16.4 动态抓取绕过

风险：browser / WebFetch 内容不经过本地 CLI。

缓解：v0 提供 `inspect_text()` API，并在文档 / SKILL.md 写入 hard gate 规则。运行时工具拦截留给后续。

### 16.5 用户以为已经“完全安全”

风险：privacy gate 被误解为完整隐私合规系统。

缓解：文档明确它只是本地静态预检，不替代用户审阅、法律合规或安全审计。

## 17. 验收标准

实施完成后应满足：

- `python3 scripts/privacy-gate.py --version` 可输出版本。
- `python3 scripts/privacy-gate.py inspect <fixture> --preset <preset> --json` 可运行。
- 三个首批 fixture 都能生成稳定 JSON。
- `privacy_report` 包含风险计数、warnings、推荐权限和准入字段。
- `evidence_bundle.sources[]` 使用 `id` / `type`，不使用 `source_id` / `source_type`。
- 输出不包含 fixture 原文全文。
- 手机号、身份证、邮箱、token、speaker prefix、work title、long quote 规则有测试覆盖。
- 现有 `validate-skill.py`、`profile-manager.py doctor`、`package-manager.py validate/test` 不受影响。
- CI 通过。

## 18. 后续阶段

v0 完成后，再考虑：

1. README 首屏重塑和 30 秒低敏试用包。
2. 公私人格对照报告 v0。
3. Profile 消费 `evidence_bundle` 的转换层。
4. Skill Package 协议升级。
5. browser / WebFetch 动态内容的更强运行时拦截。
6. 自我认知版本管理和跨 skill 推理网络。

## 19. 待用户确认的问题

进入 implementation plan 前，需要用户确认：

1. v0 是否同时包含 `privacy_report` 和 `evidence_bundle`，还是只做 `privacy_report`？
2. 是否同意 `evidence_bundle.sources[]` 对齐 Skill Package，使用 `id` / `type`？
3. 是否接受 v0 不做真实平台采集，只做本地文本和 fixture？
4. 是否同意先用 Python validator，不强制新增 JSON Schema？

本文推荐答案：

1. 同时做两者，但保持结构很薄。
2. 同意使用 `id` / `type`。
3. 同意不做真实平台采集。
4. 同意先用 Python validator 控范围。
