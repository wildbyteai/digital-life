# Distilled Life Skill Package Spec

`distilled_life` 的核心不是“复制一个人”，而是把一段经历、表达样本或决策记录蒸馏成一个可检查、可迁移、可复用的 Life Skill Package。

一个 package 必须回答四个问题：

1. **它能做什么？** — `scope` 和 `skills` 说明适用场景、方法和反例。
2. **它像谁/什么风格？** — `persona` 说明表达偏好和边界，但不能冒充真实用户。
3. **它凭什么这么说？** — `sources` 和 `evidence` 保存出处、权限、hash 和确认状态。
4. **它怎么被使用和测试？** — `exports` 和 `tests` 提供系统提示词、摘要和静态 eval cases。

## 文件结构

```text
examples/skill_packages/<package_id>/
├── manifest.json          # package 主清单
├── tests.json             # 静态测试用例
├── sources/               # 虚构、脱敏或已授权来源
│   └── *.md
└── exports/
    ├── system_prompt.md   # 给 LLM/agent 加载的提示词
    └── package_summary.md # 人类可读摘要
```

## Manifest 字段

- `schema_version`：schema 版本，当前示例使用 `0.1.0`。
- `package`：id、名称、描述、版本、许可证、可见性和语言。
- `scope`：领域、用例和限制。
- `persona`：角色、语气、偏好和不可越界事项。
- `skills`：可复用的方法资产，必须包含适用场景、步骤、反例和测试提示。
- `sources`：来源文件、sha256、permission 和 audience。
- `evidence`：每条蒸馏结论的 claim、source_ids、confidence、status 和 permission。
- `exports`：可导出的工件，例如 system prompt 和 markdown summary。
- `tests`：指向 `tests.json`，并列出 positive / negative 测试 id。

完整 JSON Schema 见：[`schemas/distilled_life.skill_package.schema.json`](../schemas/distilled_life.skill_package.schema.json)。Schema 负责字段形状和基础路径格式；发布前仍必须运行 `package-manager.py validate`，因为 source 文件存在性、sha256 匹配、重复 id、evidence source 引用、public permission 安全性等约束需要仓库级校验。

## 隐私和发布规则

公开 package 必须满足：

- 示例来源是虚构、脱敏、不可回溯到真实个人，或明确为 `public_source`。
- `package.visibility = public` 时，不允许 `private_only`、`user_review_required`、`do_not_quote` evidence 进入 package。
- `sources[].sha256` 必须匹配本地 source 文件，避免来源被悄悄替换。
- `exports/system_prompt.md` 必须写清楚边界：只能作为草稿和风格/方法参考，不能冒充本人、不能编造私人记忆、不能替用户承诺或发送。

## CLI

```bash
python3 scripts/package-manager.py validate examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py test examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py export-prompt examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py build-from-profile examples/distilled_life_demo.json --output /tmp/decision_principles_demo --package-id decision_principles_demo_tmp --name "Decision Principles Demo" --force
```

MVP 阶段的 `test` 是静态测试：检查测试用例是否声明输入、期望行为/特征、禁止行为/特征。它不会调用云端模型，也不会把来源上传到外部服务。

## 与 `distilled_life` profile 的关系

`profiles/templates/distilled_life.json` 是一次蒸馏的结构化 profile；Life Skill Package 是从 profile 中抽出的可迁移工件。

```text
Life Story + Expression/Decision Model
→ Skill Asset + Boundary Rule
→ Evidence Trace + Eval Case
→ portable skill package
```

这让 `蒸馏人生` 从“报告”进入“可复用能力资产”：它可以被复制、审计、导出给不同 agent runtime，但仍然保留证据和边界。
