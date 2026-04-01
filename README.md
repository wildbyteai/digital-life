# Digital Persona — 数字人格考古工具箱

> 用数字痕迹照见真实的自己。

## 5 个考古工具

按人生时间线排列：

| # | Skill | 触发词 | 核心问题 |
|---|-------|--------|----------|
| 1 | 👻 前世 | 前世、上辈子 | 你以为是性格的东西，只是惯性吗？ |
| 2 | 💀 社死考古 | 社死考古、黑历史 | 你从什么时候开始学会表演体面的？ |
| 3 | 🤖 AI替身 | AI替身、克隆我 | 公开的你和私密的你，是同一个人吗？ |
| 4 | 🪦 遗产清算 | 遗产清算、数字遗产 | 你留下了什么？ |
| 5 | 🪦 墓志铭 | 墓志铭、墓碑 | 你想被记住的方式，和你正在过的生活，一致吗？ |

## 安装

```bash
clawhub install digital-persona
```

或对话安装：

```
安装 digital-persona
```

## 触发方式

直接说触发词，或说 `digital-persona` / `考古工具箱` 查看全部工具列表。

## 核心设计

- **5 层 Persona 结构**：Layer 0 硬规则 → Layer 1 身份锚定 → Layer 2 表达风格 → Layer 3 思维模式 → Layer 4 边界雷区
- **可迭代 Profile**：每次分析生成结构化 JSON Profile，可追加、可纠正、可回滚
- **进化机制**：用户可以追加新信息或纠正错误，Profile 增量更新
- **隐私优先**：所有数据本地分析，不上传任何服务器

## 目录结构

```
digital-persona/
├── SKILL.md                  # 主入口，包含所有触发规则和执行流程
├── README.md
├── LICENSE
├── .gitignore
├── prompts/
│   ├── persona_builder.md    # 通用 5 层 Persona 生成模板
│   ├── evolution.md          # 追加/纠正流程模板
│   ├── past_life.md          # 前世 prompt
│   ├── cringe_archaeology.md # 社死考古 prompt
│   ├── ai_clone.md           # AI替身 prompt
│   ├── legacy_audit.md       # 遗产清算 prompt
│   └── epitaph.md            # 墓志铭 prompt
├── profiles/                 # Profile JSON 模板
│   ├── past_life.json
│   ├── cringe_archaeology.json
│   ├── ai_clone.json
│   ├── legacy_audit.json
│   └── epitaph.json
├── layer0/                   # 各 skill 的 Layer 0 硬规则
│   ├── past_life.md
│   ├── cringe_archaeology.md
│   ├── ai_clone.md
│   ├── legacy_audit.md
│   └── epitaph.md
└── references/               # 各 skill 的方法论文档
```

## 哲学锚点

- 前世：佛教 — 业力与因果
- 社死考古：汉娜·阿伦特 — 公共领域与私人领域
- AI替身：图灵测试 — 什么是"你"
- 遗产清算：海德格尔 — 向死而生
- 墓志铭：塞涅卡 — 论生命的短促

## 版本

- v1.0.0：完全重构，5 层 Persona + 结构化 Profile + 进化机制
- v0.3.0：初始版本，基于 prompt 模板
