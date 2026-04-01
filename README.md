# Skill Box — 数字人格考古工具箱

> 用数字痕迹照见真实的自己。

## 5 个考古工具

| Skill | 触发词 | 核心问题 |
|-------|--------|----------|
| 🪦 遗产清算 | 遗产清算、数字遗产 | 你留下了什么？ |
| 💀 社死考古 | 社死考古、黑历史 | 你从什么时候开始学会表演体面的？ |
| 🤖 AI替身 | AI替身、克隆我 | 公开的你和私密的你，是同一个人吗？ |
| 👻 前世 | 前世、上辈子 | 你以为是性格的东西，只是惯性吗？ |
| 🪦 墓志铭 | 墓志铭、墓碑 | 你想被记住的方式，和你正在过的生活，一致吗？ |

## 安装

```bash
clawhub install skill-box
```

或克隆到本地：

```bash
git clone https://github.com/wildbyteai/skill-box.git
```

## 触发方式

直接说触发词，或说 `skill box` / `考古工具箱` 查看全部工具列表。

## 核心设计

- **5 层 Persona 结构**：Layer 0 硬规则 → Layer 1 身份锚定 → Layer 2 表达风格 → Layer 3 思维模式 → Layer 4 边界雷区
- **可迭代 Profile**：每次分析生成结构化 JSON Profile，可追加、可纠正、可回滚
- **进化机制**：用户可以追加新信息或纠正错误，Profile 增量更新
- **隐私优先**：所有数据本地分析，不上传任何服务器

## 目录结构

```
skill-box/
├── SKILL.md                  # 主入口，包含所有触发规则和执行流程
├── README.md
├── LICENSE
├── .gitignore
├── prompts/
│   ├── persona_builder.md    # 通用 5 层 Persona 生成模板
│   └── evolution.md          # 追加/纠正流程模板
├── profiles/                  # 生成的 Profile 文件（JSON）
│   └── {user_slug}_{skill}.json
├── layer0/                    # 各 skill 的 Layer 0 硬规则
│   ├── legacy_audit.md
│   ├── cringe_archaeology.md
│   ├── ai_clone.md
│   ├── past_life.md
│   └── epitaph.md
└── references/                # 各 skill 的方法论文档
    ├── legacy-audit.md
    ├── cringe-archaeology.md
    ├── ai-clone.md
    ├── past-life.md
    └── epitaph.md
```

## 哲学锚点

- 遗产清算：海德格尔 — 向死而生
- 社死考古：汉娜·阿伦特 — 公共领域与私人领域
- AI替身：图灵测试 — 什么是"你"
- 前世：佛教 — 业力与因果
- 墓志铭：塞涅卡 — 论生命的短促

## 版本

- v1.0.0：完全重构，5 层 Persona + 结构化 Profile + 进化机制
- v0.3.0：初始版本，基于 prompt 模板
