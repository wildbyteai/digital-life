# digital-life 下一版优化方案审阅材料：Local Evidence Intake v0

> 给无上下文的新 agent / reviewer 使用。本文是方案审阅材料，不代表已经开始实现。

## 0. 快速入口

- GitHub 仓库：https://github.com/wildbyteai/digital-life
- 当前远程：`https://github.com/wildbyteai/digital-life.git`
- 当前分支：`main`
- 当前基线提交：[`daee44e76fa87afe8cf65bdd20b2a96d0161400f`](https://github.com/wildbyteai/digital-life/commit/daee44e76fa87afe8cf65bdd20b2a96d0161400f)
- 当前版本：`1.6.0-beta`
- 本地路径：`/Users/kyle/Documents/self/AI/digital-life`
- 本文建议优先方向：**Local Evidence Intake v0：本地隐私预检 + Evidence Bundle + Level 1 确定性评测**

相关 GitHub 文件链接：

- [README.md](https://github.com/wildbyteai/digital-life/blob/main/README.md)
- [SKILL.md](https://github.com/wildbyteai/digital-life/blob/main/SKILL.md)
- [CHANGELOG.md](https://github.com/wildbyteai/digital-life/blob/main/CHANGELOG.md)
- [VERSION](https://github.com/wildbyteai/digital-life/blob/main/VERSION)
- [profiles/contracts/skill-contract.json](https://github.com/wildbyteai/digital-life/blob/main/profiles/contracts/skill-contract.json)
- [profiles/README.md](https://github.com/wildbyteai/digital-life/blob/main/profiles/README.md)
- [schemas/distilled_life.skill_package.schema.json](https://github.com/wildbyteai/digital-life/blob/main/schemas/distilled_life.skill_package.schema.json)
- [scripts/profile-manager.py](https://github.com/wildbyteai/digital-life/blob/main/scripts/profile-manager.py)
- [scripts/package-manager.py](https://github.com/wildbyteai/digital-life/blob/main/scripts/package-manager.py)
- [scripts/validate-skill.py](https://github.com/wildbyteai/digital-life/blob/main/scripts/validate-skill.py)
- [scripts/validation_rules.py](https://github.com/wildbyteai/digital-life/blob/main/scripts/validation_rules.py)
- [scripts/test_scripts.py](https://github.com/wildbyteai/digital-life/blob/main/scripts/test_scripts.py)
- [.github/workflows/validate.yml](https://github.com/wildbyteai/digital-life/blob/main/.github/workflows/validate.yml)
- [examples/](https://github.com/wildbyteai/digital-life/tree/main/examples)
- [examples/skill_packages/](https://github.com/wildbyteai/digital-life/tree/main/examples/skill_packages)
- [docs/distilled_life_skill_package.md](https://github.com/wildbyteai/digital-life/blob/main/docs/distilled_life_skill_package.md)

---

## 1. 当前状态说明

截至本文编写时，当前会话**尚未实现方案**，只做了项目分析、方向收敛和审阅材料整理。

也就是说：

- 尚未新增 `scripts/privacy-gate.py`。
- 尚未新增 schema。
- 尚未新增 fixture。
- 尚未修改 CI。
- 尚未修改 6 个 skill 主流程。
- 尚未提交 commit。

本文目标是让新 agent 在没有上下文的情况下，能够审阅“下一版到底该做什么”。

---

## 2. 项目一句话定位

`digital-life` 是一个 OpenClaw / Clawhub Skill 包，提供 6 个基于数字痕迹的自我考古与经验蒸馏工具，用用户的社交、聊天、工作、公开表达等数字痕迹生成结构化 Profile 和可读 Markdown 报告。

项目当前不是普通 prompt 集，而更像一套：

```text
数字痕迹 → 证据 → Persona/Profile → Markdown 报告 → Life Skill Package
```

的个人经验与数字自我建模基础设施。

---

## 3. 当前 6 个 skill

| Skill slug | 中文名 | 核心问题 | 关键文件 |
|---|---|---|---|
| `past_life` | 前世 | 你现在的执念，可能只是过去惯性的延续吗？ | [`prompts/past_life.md`](https://github.com/wildbyteai/digital-life/blob/main/prompts/past_life.md) |
| `cringe_archaeology` | 社死考古 | 你从什么时候开始学会表演体面？ | [`prompts/cringe_archaeology.md`](https://github.com/wildbyteai/digital-life/blob/main/prompts/cringe_archaeology.md) |
| `ai_clone` | AI 替身 | 公开的你和私密的你，是同一个人吗？ | [`prompts/ai_clone.md`](https://github.com/wildbyteai/digital-life/blob/main/prompts/ai_clone.md) |
| `legacy_audit` | 遗产清算 | 你在数字世界留下了什么？ | [`prompts/legacy_audit.md`](https://github.com/wildbyteai/digital-life/blob/main/prompts/legacy_audit.md) |
| `epitaph` | 墓志铭 | 你想被记住的方式，和你正在过的生活一致吗？ | [`prompts/epitaph.md`](https://github.com/wildbyteai/digital-life/blob/main/prompts/epitaph.md) |
| `distilled_life` | 蒸馏人生 | 你的经历能否变成可复用的判断和表达能力？ | [`prompts/distilled_life.md`](https://github.com/wildbyteai/digital-life/blob/main/prompts/distilled_life.md) |

每个 skill 通常有四类配套文件：

```text
prompts/{skill}.md
layer0/{skill}.md
references/{skill}.md
profiles/templates/{skill}.json
```

---

## 4. 当前已有工程能力

### 4.1 契约驱动

项目通过 [`profiles/contracts/skill-contract.json`](https://github.com/wildbyteai/digital-life/blob/main/profiles/contracts/skill-contract.json) 统一管理 6 个 skill 的：

- `slug`
- `display_name`
- `triggers`
- `prompt_path`
- `layer0_path`
- `reference_path`
- `template_path`
- `required_top_level_keys`

这让新增或校验 skill 有清晰入口。

### 4.2 Profile 生命周期管理

通过 [`scripts/profile-manager.py`](https://github.com/wildbyteai/digital-life/blob/main/scripts/profile-manager.py) 支持：

```bash
python3 scripts/profile-manager.py list
python3 scripts/profile-manager.py init --skill <skill> --slug <slug>
python3 scripts/profile-manager.py snapshot --skill <skill> --slug <slug>
python3 scripts/profile-manager.py rollback --skill <skill> --slug <slug>
python3 scripts/profile-manager.py validate --skill <skill> --slug <slug>
python3 scripts/profile-manager.py delete --skill <skill> --slug <slug> --yes --with-history
python3 scripts/profile-manager.py doctor
```

真实用户 profile 默认被 `.gitignore` 排除，避免提交隐私输出。

### 4.3 Life Skill Package 能力

`distilled_life` 已有 Life Skill Package 概念，可以从人生经验 Profile 导出为可移植 skill package。

相关文件：

- [`scripts/package-manager.py`](https://github.com/wildbyteai/digital-life/blob/main/scripts/package-manager.py)
- [`schemas/distilled_life.skill_package.schema.json`](https://github.com/wildbyteai/digital-life/blob/main/schemas/distilled_life.skill_package.schema.json)
- [`docs/distilled_life_skill_package.md`](https://github.com/wildbyteai/digital-life/blob/main/docs/distilled_life_skill_package.md)
- [`examples/skill_packages/writing_style_demo/`](https://github.com/wildbyteai/digital-life/tree/main/examples/skill_packages/writing_style_demo)
- [`examples/skill_packages/decision_principles_demo/`](https://github.com/wildbyteai/digital-life/tree/main/examples/skill_packages/decision_principles_demo)

### 4.4 CI / Validation

CI 文件：[`validate.yml`](https://github.com/wildbyteai/digital-life/blob/main/.github/workflows/validate.yml)

当前 CI 大致执行：

```bash
python3 -m py_compile scripts/*.py
python3 scripts/validate-skill.py
python3 scripts/package-manager.py validate examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py validate examples/skill_packages/decision_principles_demo
python3 scripts/package-manager.py test examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py test examples/skill_packages/decision_principles_demo
python3 scripts/profile-manager.py doctor
python3 -m unittest discover -s scripts -p 'test_scripts.py'
python3 scripts/profile-manager.py --version
python3 scripts/validate-skill.py --version
python3 scripts/package-manager.py --version
```

---

## 5. 多 agent 分析后的主要诊断

### 5.1 当前项目不是缺愿景，而是缺一个可信输入闭环

项目理念、demo、文档、profile 生命周期和 package 概念已经比较完整。当前最大缺口在于：

```text
真实/半真实数字痕迹
→ 隐私预检
→ 证据结构化
→ profile / package 消费
→ 可回归测试
```

这条链路还没有工程化打通。

如果没有这个底座，后续做微信、飞书、小红书、豆瓣、B站、AI 替身、公私人格对照、个人能力包市场，都容易踩隐私和信任问题。

### 5.2 国内生态下最大风险是隐私入口

中国用户的数字痕迹通常集中在：

- 微信聊天记录
- QQ / QQ 空间
- 飞书会议纪要 / 文档评论 / 工作群
- 小红书 / 知乎 / 豆瓣 / B站公开足迹
- 朋友圈、微博、贴吧、公众号评论等平台

这些材料常常包含：

- 第三方姓名、称谓、群聊他人发言
- 手机号、身份证号、邮箱、地址
- 公司、客户、项目、会议纪要、内部文档
- API key、token、链接、截图中的隐私信息
- 未经授权的 exact quote

因此，适配国内生态的第一步不应是“自动接平台”，而应是“本地材料进入系统之前的隐私预检与证据标准化”。

### 5.3 传播层也有明显优化空间，但不建议作为第一实现主体

另一个 agent 对 README / 传播做了分析，认为：

- README 首屏信息过载。
- 最强传播素材没有放在首屏：
  - “你发了 3 万条朋友圈，收获 2 个真心朋友。”
  - ASCII 数字墓碑。
  - “莪の丗堺伱卜懂”。
- 缺少 30 秒理解区块。
- 缺少 GIF / 可视化 demo。
- 安装前置条件不够清楚。
- `examples/` 示例质量很高，但埋得较深。

这些建议有价值，但本轮用户已选择优先验证“隐私入口”，因此 README 重塑建议作为第二阶段，而不是第一阶段主体。

---

## 6. 多 agent 提出的非显而易见长期方向

### 6.1 Skill Package 作为个人 AI 能力交换协议

当前 [`distilled_life.skill_package.schema.json`](https://github.com/wildbyteai/digital-life/blob/main/schemas/distilled_life.skill_package.schema.json) 不只是导出格式。它可以被重新定位为：

```text
把一个人的判断方式、表达习惯、边界规则，打包成 agent runtime 可加载的能力单元。
```

类比：

- Docker 之于部署
- npm 之于软件包
- Life Skill Package 之于个人经验 / 表达 / 判断能力

这是长期高杠杆方向，但对普通用户冷启动稍远。

### 6.2 6 个 skill 组成跨 skill 推理网络

目前 6 个 skill 是独立工具。长期可以让它们互相验证：

```text
legacy_audit 的 regret_patterns
+ cringe_archaeology 的 top_cringe
+ ai_clone 的 similarity_score
+ distilled_life 的 decision_model
→ 统一数字自我知识图谱
```

但这依赖更稳定的 evidence 结构。

### 6.3 Profile 版本管理 = 自我认知时间线

当前 snapshot / rollback 更像防丢数据。长期可以升级成：

```text
自我认知版本管理
人生 diff
哪些信念变了
哪些模式重复了
哪些判断被新证据推翻了
```

但也依赖更规范的 evidence / correction 记录。

### 6.4 Evidence Provenance 作为 AI 可信度层

当前 profile 和 package 中已有 evidence trace / sha256 / permission 雏形。可以抽象成通用 AI 输出审计协议：

```text
每个洞察都能追溯到证据
每个证据都有权限和置信度
每个 package 都能被验证
```

这同样需要从输入证据包做起。

### 6.5 行为监测 + 认知漂移预警

长期可做：

```text
定期扫描用户指定平台
对比当前行为和历史 profile
发现认知漂移
```

例如：

> 你的 profile 说你倾向“先验证再投入”，但最近连续快速答应了 3 个合作，这是有意识改变还是惯性复发？

但第一版不建议做持续监测，隐私和授权风险太高。

---

## 7. 已收敛出的 3 条候选路线

### 方案 A：隐私入口优先：Local Evidence Intake v0【当前推荐】

新增本地只读预检链路：

```text
用户主动提供脱敏/半脱敏材料
→ privacy-gate 本地扫描
→ privacy_report.json 风险报告
→ evidence_bundle.json 证据包
→ CI 固定 fixture 回归
→ 后续 skill/profile/package 再消费证据包
```

核心价值：

- 先解决真实材料进入系统前的隐私风险。
- 不碰平台登录、不碰微信数据库、不联网、不调用 LLM。
- 用 deterministic fixture 和 CI 建立可信底座。
- 为后续微信/飞书/公私人格对照/Skill Package 打基础。

### 方案 B：低敏传播优先：30 秒数字人生试用包

新增：

- 三句话输入模板
- 脱敏截图卡
- README 首屏重塑
- 低置信示例输出

核心价值：

- 快速验证陌生用户是否愿意试。
- 适合中文互联网传播。
- 隐私风险最低。

缺点：

- 不解决高敏材料进入系统的问题。
- 容易被误解为 AI 算命或年度总结文案。

### 方案 C：公私人格对照报告 v0

用户提供两类脱敏样本：

```text
私域：微信 / QQ / 朋友圈 / 口述
工作：飞书 / 会议纪要 / 文档评论 / 工作群
```

输出：

```text
私域表达 vs 工作表达 对照报告
表达边界提醒
可复用表达卡
```

核心价值：

- 国内场景非常强。
- 用户保存价值高。
- 可承接 `AI替身` 和 `蒸馏人生`。

缺点：

- 隐私风险较高。
- 需要先有 Privacy Gate。

---

## 8. 用户已选择的优先方向

用户已在本轮讨论中选择：

```text
隐私入口
```

因此当前建议进入：

```text
Local Evidence Intake v0
```

---

## 9. Local Evidence Intake v0 初步方案

### 9.1 核心目标

建立一个本地、只读、确定性、可 CI 回归的隐私预检与证据包生成入口。

它不负责“理解人生”，只负责回答：

```text
这份材料能不能安全进入 digital-life？
如果能，它应以什么证据摘要和权限进入？
如果不能，风险在哪里？
```

### 9.2 建议新增 CLI

建议新增：

```bash
python3 scripts/privacy-gate.py inspect <path> --preset generic|chat|work --json
```

可选扩展参数可在设计时讨论：

```bash
--output-dir <dir>
--fail-on high|critical
--redaction strict|balanced|off
--format json|pretty
```

但 v0 不宜过度设计。

### 9.3 输入范围

第一版只支持用户主动提供的本地文件，不接平台。

支持 preset：

```text
generic  普通 Markdown / TXT / JSONL
chat     脱敏聊天式文本 / JSONL
work     飞书 / 会议纪要 / 文档评论式工作沟通 Markdown 或 JSON
```

不建议第一版读取真实平台导出数据库或调用平台 API。

### 9.4 输出

建议输出两个 JSON：

```text
privacy_report.json
evidence_bundle.json
```

也可以支持 `--json` 时直接打印到 stdout，便于测试。

---

## 10. `privacy_report.json` 建议职责

`privacy_report.json` 关注“风险与准入”。

它应回答：

- 材料里有哪些隐私风险？
- 是否包含手机号？
- 是否包含身份证号？
- 是否包含邮箱？
- 是否包含地址？
- 是否包含银行卡？
- 是否包含 API key / token 风险？
- 是否有第三方姓名 / 称谓 / 公司 / 群聊他人发言？
- 是否有长段 exact quote？
- 默认应该是什么 `permission`？
- 默认应该是什么 `quote_policy`？
- 是否允许进入后续 profile/package 流程？

一个可能的 v0 结构：

```json
{
  "schema_version": "0.1.0",
  "input_path": "examples/evidence_fixtures/chat/redacted_wechat_sample.md",
  "preset": "chat",
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
    "long_exact_quote": 2
  },
  "warnings": [
    {
      "code": "third_party_present",
      "message": "检测到第三方称谓或姓名占位，后续输出不得公开引用原文。",
      "severity": "medium"
    }
  ],
  "recommended_permission": "private_only",
  "recommended_quote_policy": "do_not_quote",
  "redaction_status": "partially_redacted",
  "allowed_for_profile": true,
  "allowed_for_public_demo": false
}
```

字段名只是草案，审阅时请重点判断是否与现有 `permission` / `publication_policy` 命名冲突。

---

## 11. `evidence_bundle.json` 建议职责

`evidence_bundle.json` 关注“后续 skill 如何引用证据，而不是直接吞原文”。

它应回答：

- 这份材料作为证据，最小可记录什么？
- `source_id` 是什么？
- `source_type` 是什么？
- `sha256` 是什么？
- 时间范围是什么？
- 摘要是什么？
- 风险计数是什么？
- 是否出现第三方？
- 是否已经脱敏？
- 默认权限和引用策略是什么？

一个可能的 v0 结构：

```json
{
  "schema_version": "0.1.0",
  "bundle_id": "evidence_bundle_redacted_wechat_sample",
  "sources": [
    {
      "source_id": "src_redacted_wechat_sample",
      "source_type": "chat_export_redacted",
      "sha256": "<computed_sha256>",
      "time_range": {
        "start": "2026-01-01",
        "end": "2026-01-07"
      },
      "source_summary": "一组虚构的脱敏私域聊天片段，用于测试第三方称谓和长引用检测。",
      "permission": "private_only",
      "quote_policy": "do_not_quote",
      "confidence": "low",
      "redaction_status": "partially_redacted",
      "third_party_present": true,
      "risk_counts": {
        "third_party_name_or_alias": 3,
        "long_exact_quote": 2
      }
    }
  ]
}
```

注意：v0 不应保存原文，只保存摘要、哈希、权限和风险信息。

---

## 12. v0 明确不做

```text
不登录微信
不登录飞书
不登录小红书
不登录知乎
不登录豆瓣
不登录 B站
不破解微信数据库
不调用 LLM
不生成完整人格报告
不修改现有 6 个 skill 主流程
不把真实聊天原文写入 profile
不做加密 vault
不做跨 skill 知识图谱
不做平台 adapter 大框架
不做长期 monitor / daemon
不做自动浏览器采集
```

这个范围限制很重要。否则项目容易从“隐私入口”滑向“高敏数据吸尘器”。

---

## 13. 建议新增文件

如果方案获批，可能新增：

```text
scripts/privacy-gate.py
schemas/evidence_bundle.schema.json
schemas/privacy_report.schema.json
examples/evidence_fixtures/README.md
examples/evidence_fixtures/generic/*.md
examples/evidence_fixtures/chat/*.md
examples/evidence_fixtures/work/*.md
```

可能修改：

```text
scripts/test_scripts.py
.github/workflows/validate.yml
README.md
SKILL.md
docs/distilled_life_skill_package.md
```

第一版建议尽量少改现有主流程，避免牵动 6 个 skill。

---

## 14. 建议测试策略

### 14.1 确定性 fixture

新增虚构中文 fixture，覆盖：

1. 普通低敏文本。
2. 脱敏聊天文本。
3. 含第三方称谓的群聊文本。
4. 含手机号 / 邮箱 / 地址的高风险文本。
5. 含身份证号 / 银行卡样式的高风险文本。
6. 含 API key / token 风险的文本。
7. 含长 exact quote 的文本。
8. 飞书 / 会议纪要式工作沟通文本。

所有 fixture 必须虚构，不能包含真实个人信息。

### 14.2 单元测试重点

应测试：

- 同一输入多次运行输出稳定。
- `sha256` 稳定。
- 风险计数稳定。
- 高风险内容触发 warning。
- 第三方内容触发 warning。
- 长 exact quote 触发 warning。
- `private_only` / `do_not_quote` 不会被升级为公开。
- `--preset chat` 和 `--preset work` 的规则差异可见。
- CLI 对不存在路径、目录、空文件、非法 JSONL 有明确错误。

### 14.3 CI 接入

建议在 `.github/workflows/validate.yml` 中新增：

```bash
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/chat/redacted_wechat_sample.md --preset chat --json
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/work/feishu_meeting_note_sample.md --preset work --json
```

或通过 unit tests 覆盖，避免 CI 命令过多。

---

## 15. 风险与反对意见

### 15.1 方案可能仍然过大

`privacy_report.json` 和 `evidence_bundle.json` 同时做，可能会让 v0 变重。

替代收窄方案：

```text
只做 privacy_report.json
先不做 evidence_bundle.json
```

或者：

```text
只做 fixture + deterministic tests
暂不新增 CLI
```

但缺点是后续 profile/package 消费路径仍不清晰。

### 15.2 字段可能与现有 schema 重复

现有 Skill Package schema 已有：

- `sources`
- `evidence`
- `permission`
- `exports`
- `tests`

v0 新增 `evidence_bundle.json` 时，要避免定义一套平行但不兼容的来源结构。

审阅重点：是复用现有 package schema 的 `sources/evidence`，还是先做独立 v0 schema？

### 15.3 规则检测可能过于粗糙

不调用 LLM 的 deterministic 规则能检测手机号、身份证、邮箱、token 等模式，但对：

- 第三方姓名
- 公司项目代号
- 语境里的敏感关系
- 阴阳怪气的伤害性表达

识别有限。

v0 应明确：这是 Level 1 静态预检，不是完整隐私审计。

### 15.4 用户感知弱

Privacy Gate 是底座，用户可能不觉得“好玩”。因此第二阶段应接：

- 30 秒试用模板
- 脱敏截图卡
- 公私人格对照报告 v0

但第一阶段不要让传播目标污染隐私底座。

---

## 16. 推荐分阶段路线

### 第一阶段：Local Evidence Intake v0

目标：

```text
本地、只读、确定性、可 CI 回归的隐私预检与证据包生成入口。
```

范围：

1. 新增 `scripts/privacy-gate.py`。
2. 新增虚构中文 fixture。
3. 新增 `privacy_report.json` 输出结构。
4. 新增 `evidence_bundle.json` 输出结构。
5. 新增 deterministic tests。
6. CI 接入测试。
7. 文档说明“这是后续微信/飞书/公私人格/Skill Package 的安全入口”。

### 第二阶段：低敏传播入口

目标：

```text
让陌生用户 30 秒理解并低风险试用。
```

范围：

- README 首屏重塑。
- 三句话试用模板。
- 脱敏截图卡。
- 强钩子前置：朋友圈、数字墓碑、火星文。

### 第三阶段：公私人格对照报告 v0

目标：

```text
在 Privacy Gate 保护下，用私域样本 × 工作样本生成用户可保存的对照报告。
```

范围：

- 私域表达摘要。
- 工作表达摘要。
- 表达差异。
- 边界提醒。
- 可复用表达卡。

### 第四阶段：个人 AI 能力协议

目标：

```text
把 Life Skill Package 从 distilled_life 的导出格式，升级为个人 AI 能力交换协议。
```

范围：

- package schema v2。
- evidence provenance。
- eval cases。
- portable system prompt。
- package lint / publish readiness。

---

## 17. 给新 agent 的审阅任务

请重点审阅以下问题：

### 17.1 方向是否正确

对 `digital-life` 来说，下一版是否应该优先做 `Local Evidence Intake v0`？

还是应该优先做：

- README 首屏/传播改造？
- 三句话低敏入口？
- 公私人格对照报告？
- Skill Package 协议升级？

### 17.2 范围是否足够窄

当前 `Local Evidence Intake v0` 是否仍然过大？

是否应收窄为：

```text
只做 privacy_report.json，不做 evidence_bundle.json
```

或：

```text
只做 fixture + validation，不新增 CLI
```

### 17.3 数据结构是否合理

`privacy_report.json` 和 `evidence_bundle.json` 是否应该分开？

字段命名是否应贴合现有：

- `permission`
- `publication_policy`
- `source_summary`
- `evidence_trace`
- `sources`
- `eval_cases`

是否应该复用 [`schemas/distilled_life.skill_package.schema.json`](https://github.com/wildbyteai/digital-life/blob/main/schemas/distilled_life.skill_package.schema.json) 的结构，而不是新增平行 schema？

### 17.4 国内生态适配是否真实

第一版只支持用户主动提供的本地脱敏文本，是否过于保守？

是否应该加入：

- 微信聊天导出 fixture？
- 飞书会议纪要 fixture？
- 小红书/知乎/豆瓣公开页文本 fixture？

注意：当前建议是不碰真实平台登录和自动采集。

### 17.5 隐私红线是否充分

请审：

- 第三方隐私
- 公司/客户/项目机密
- exact quote
- 手机号/身份证/邮箱/地址
- API key / token
- 群聊内容
- 未经授权的他人发言
- 云端模型上下文风险

### 17.6 工程落地是否符合现有项目风格

当前项目是纯 Python 脚本 + JSON schema + Markdown 文档。

请审阅是否建议新增：

```text
scripts/privacy-gate.py
schemas/evidence_bundle.schema.json
schemas/privacy_report.schema.json
examples/evidence_fixtures/
docs/local_evidence_intake.md
```

以及是否要修改：

```text
scripts/validation_rules.py
scripts/test_scripts.py
.github/workflows/validate.yml
README.md
SKILL.md
```

---

## 18. 推荐结论

当前推荐：

> 下一版优先做 `Local Evidence Intake v0`，即本地隐私预检 + Evidence Bundle + Level 1 确定性评测。

原因：

1. 它补的是项目长期演进的关键入口层。
2. 它符合国内生态高敏数据现实。
3. 它能让后续微信/飞书/公私人格/Skill Package 都建立在可信证据上。
4. 它可以通过 fixture 和 CI 验证，而不是只靠 prompt 声明。
5. 它避免一开始就陷入平台登录、反爬、微信数据库和真实隐私材料处理。

## 19. 二次交叉评审吸收意见

新 agent 对本文做了二次交叉评审，结论中有几项需要纳入后续正式 spec。

### 19.1 Evidence Bundle 字段应向 Skill Package `sources` 对齐

现有 codebase 里有两套证据相关结构：

| 阶段 | 代表文件 | 证据字段 | 主要键名 |
|---|---|---|---|
| Profile | `examples/distilled_life_demo.json` | `evidence_trace` | `source_id`, `source_type`, `claim`, `confidence`, `permission` |
| Skill Package | `examples/skill_packages/*/manifest.json` | `sources` / `evidence` | `id`, `type`, `path`, `sha256`, `permission`, `audience` |

二次评审指出：本文第 11 节示例里的 `sources[].source_id` / `sources[].source_type` 更像 Profile 风格，但如果 `evidence_bundle.json` 未来要进入 Skill Package 管线，应优先向 Skill Package 的 `sources` 结构对齐。

因此后续正式 spec 应调整为：

```json
{
  "schema_version": "0.1.0",
  "bundle_id": "evidence_bundle_redacted_wechat_sample",
  "sources": [
    {
      "id": "src_redacted_wechat_sample",
      "type": "chat_export_redacted",
      "sha256": "<computed_sha256>",
      "time_range": {
        "start": "2026-01-01",
        "end": "2026-01-07"
      },
      "source_summary": "一组虚构的脱敏私域聊天片段，用于测试第三方称谓和长引用检测。",
      "permission": "private_only",
      "audience": "owner_only",
      "quote_policy": "do_not_quote",
      "confidence": "low",
      "redaction_status": "partially_redacted",
      "third_party_present": true,
      "risk_counts": {
        "third_party_name_or_alias": 3,
        "long_exact_quote": 2
      }
    }
  ]
}
```

并明确：

- `permission` 应复用 `validation_rules.py` 中的 `PERMISSION_VALUES`。
- `audience` 应复用 `validation_rules.py` 中的 `AUDIENCE_VALUES`。
- `confidence` 应复用 `validation_rules.py` 中的 `CONFIDENCE_VALUES`。
- 如果保留 `quote_policy`，需要决定它是 `permission` 的别名、补充策略，还是 v0 独立字段；避免与 `do_not_quote` 这个 permission 值职责混淆。

### 19.2 动态 Web / Browser Intake 绕过风险需要单独处理

二次评审指出，现有 prompt 中已经允许在运行环境支持时通过 browser / WebFetch 获取线上内容，例如：

- `prompts/past_life.md` 中的豆瓣、微博、小红书、微信数据获取说明。
- `prompts/cringe_archaeology.md` 中的 QQ 空间、人人网、贴吧、微博等数据获取说明。

如果 `privacy-gate.py` 只做用户手动提供的本地文件扫描，那么 agent 动态抓取到的线上文本可能绕过隐私预检，直接进入 LLM 分析或 profile 写入。

因此正式 spec 需要至少覆盖一个“防绕过”设计：

1. **v0 最小实现**：`privacy-gate.py` 暴露可编程 Python API，例如 `inspect_text(text, preset=...)` 和 `inspect_file(path, preset=...)`，供未来 prompt / agent 流程调用。
2. **文档硬规则**：在 `SKILL.md` 或相关 Layer0 中补充：任何通过 browser / WebFetch / 在线页面获取的文本，在用于分析、总结、写入 profile 前，必须先经过 privacy gate 扫描。
3. **v0 不自动拦截工具流量**：第一版不做运行时级别的工具拦截，不伪装成已解决所有动态抓取风险；只把 API 和规则边界先立住。

### 19.3 Privacy Gate 应定位为 Hard Gate，而不是可选辅助工具

现有 prompt 里有很多隐私提醒，例如“不要粘贴密码、API keys、身份证号、完整私人聊天记录、第三方秘密”等，但它们是软提示词。

二次评审建议把 `privacy-gate.py` 定位为：

```text
LLM 介入前的确定性硬门槛。
```

这意味着正式设计中应避免把它写成“可选检查工具”，而应写成后续所有高敏材料入口的默认前置步骤。

但 v0 仍需诚实标注边界：它是 Level 1 静态预检，不能替代完整法律/安全/心理风险审查。

### 19.4 国内隐私规则应更具体

二次评审建议 v0 至少考虑以下 deterministic 规则：

1. **大陆手机号**：匹配 `(?:86)?1[3-9]\d{9}`，并兼容空格或连字符分隔。
2. **身份证号**：不仅做 18 位正则，还应实现 ISO 7064:1983.MOD 11-2 校验码，降低订单号误报。
3. **第三方称谓 / 人名线索**：
   - `chat` preset：识别行首对话人前缀，例如 `张三:`、`User:`、`[同事A]:`。
   - `work` preset：识别职场称谓，例如 `x总`、`x经理`、`x工`、`x老师`。
4. **敏感 token / API key**：匹配常见前缀，例如 `sk-`、`ghp_` 等。
5. **长引用检测**：单行或 blockquote 超过 120 个中文字/字符时触发 `long_exact_quote` warning，并推荐 `do_not_quote`。

这些规则应作为 v0 测试样例的一部分，而不是只写在文档里。

### 19.5 Fixtures 布局可进一步具体化

二次评审建议首批 fixture 至少包含：

```text
examples/evidence_fixtures/chat/wechat_redacted_sample.txt
examples/evidence_fixtures/work/feishu_meeting_note_sample.md
examples/evidence_fixtures/generic/personal_journal_sample.md
```

要求：

- 全部为虚构数据。
- 明确标注 demo / fictional / redacted。
- 覆盖第三方称谓、工作项、公司/项目占位、虚构地址、长引用、手机号/邮箱/token 等规则。

### 19.6 更新后的推荐结论

二次评审没有推翻“优先做 Local Evidence Intake v0”的方向，但要求调整重点：

1. `evidence_bundle.json` 的 `sources` 字段向 Skill Package manifest 对齐，使用 `id` / `type`，不要使用 `source_id` / `source_type`。
2. `privacy-gate.py` 除 CLI 外，应设计可编程 API，以便未来 browser / WebFetch 动态内容也能先扫描。
3. 在正式 spec 中明确它是 hard gate 的第一步，而不是可选辅助脚本。
4. v0 隐私规则要包含中国手机号、身份证校验码、职场称谓、聊天发言人前缀、token、长引用等具体检测。
5. fixtures 要先围绕微信脱敏样本、飞书会议纪要样本、个人日记样本建立最小回归集。
