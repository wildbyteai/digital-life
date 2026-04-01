# 数字人生.skill

> *"你发了 3 万条朋友圈，收获 2 个真心朋友。"*
>
> *"你十年前在QQ空间写的'莪の丗堺伱卜懂'，至今还在。"*
>
> *"你的支付宝年度账单告诉你：你花了 47% 的钱在吃上面。"*

每一个工具都是一面镜子。你不想看的，才是你最需要看的。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blueviolet)](https://docs.openclaw.ai)
[![clawhub](https://img.shields.io/badge/clawhub-published-green)](https://clawhub.com)

&nbsp;

用你的数字痕迹照见真实的自己  
每个 skill 生成一个 **结构化 Profile**——可迭代、可纠错、可回滚

[安装](#安装) · [5 个工具](#5-个考古工具) · [使用](#使用) · [效果示例](#效果示例)

---

## 5 个考古工具

按人生时间线排列：

| # | 工具 | 触发词 | 核心问题 | 哲学锚点 |
|---|------|--------|----------|----------|
| 1 | 👻 前世 | 前世、上辈子 | 你以为是性格的东西，只是惯性吗？ | 佛教：业力与因果 |
| 2 | 💀 社死考古 | 社死考古、黑历史 | 你从什么时候开始学会表演体面的？ | 阿伦特：公共/私人的边界 |
| 3 | 🤖 AI替身 | AI替身、克隆我 | 公开的你和私密的你，是同一个人吗？ | 图灵测试：什么是"你" |
| 4 | 🪦 遗产清算 | 遗产清算、数字遗产 | 你留下了什么？ | 海德格尔：向死而生 |
| 5 | 🪦 墓志铭 | 墓志铭、墓碑 | 你想被记住的方式，和你正在过的生活，一致吗？ | 塞涅卡：论生命的短促 |

---

## 安装

对话安装：

```
安装 digital-life
```

CLI 安装：

```bash
npx clawhub install digital-life
```

---

## 使用

在对话中说出触发词即可：

```
我想做遗产清算
```

Agent 确认后进入对话模式，你提供数字生活的描述，agent 生成结构化 Profile。

每个 profile 存储在 `profiles/` 目录下：

```
profiles/
├── past_life_{slug}.json          # 前世 profile
├── cringe_archaeology_{slug}.json # 社死考古 profile
├── ai_clone_{slug}.json           # AI替身 profile
├── legacy_audit_{slug}.json       # 遗产清算 profile
└── epitaph_{slug}.json            # 墓志铭 profile
```

### 管理命令

| 命令 | 说明 |
|------|------|
| `列出 profile` | 扫描 profiles/ 目录，列出所有已生成的 profile |
| `回滚 profile {slug}` | 将 profile 回滚到指定版本 |
| `删除 profile {slug}` | 确认后删除指定 profile |

---

## 效果示例

> 输入：`我在微信上发了5年的朋友圈，每周至少3条。微博更了8年，大概3000条。QQ空间从08年用到15年，现在回头看全是黑历史。`

**遗产清算输出摘要：**

```
📊 数字生命审计
  - 数字生命：18 年，3 个平台
  - 总发言：~5000 条
  - 估算浪费时间：2847 小时 = 28 本书 / 3 次环球旅行
  - 最大的谎言："明天开始早睡"
  - 存在追问：如果明天这些平台全部关闭，你最想留下哪一条？

🪦 数字墓碑
┌─────────────────────────────────┐
│  这里躺着一个发了 5000 条动态的人  │
│  他用 2847 小时学会了如何让别人     │
│  觉得他过得很好                    │
│  却没学会如何让自己过得好          │
│                                  │
│  "明天开始早睡"                    │
│  ——最后登录于 2026-03-28 02:47    │
└─────────────────────────────────┘
```

---

## 核心设计

- **Persona 5 层结构**：Layer 0 硬规则 → Layer 1 身份 → Layer 2 表达 → Layer 3 思维 → Layer 4 边界
- **可迭代 Profile**：每次分析生成结构化 JSON，可追加、可纠正、可回滚
- **进化机制**：用户追加新信息或纠正错误时，Profile 增量更新
- **隐私优先**：所有分析本地进行，不上传任何服务器

---

## 目录结构

```
digital-life/
├── SKILL.md                  # Agent 指令
├── README.md
├── LICENSE
├── prompts/
│   ├── persona_builder.md    # 通用 5 层 Persona 生成模板
│   ├── evolution.md          # 追加/纠正流程模板
│   ├── past_life.md          # 前世 prompt
│   ├── cringe_archaeology.md # 社死考古 prompt
│   ├── ai_clone.md           # AI替身 prompt
│   ├── legacy_audit.md       # 遗产清算 prompt
│   └── epitaph.md            # 墓志铭 prompt
├── profiles/                 # Profile JSON 模板
├── layer0/                   # 各 skill 的 Layer 0 硬规则
└── references/               # 各 skill 的方法论文档
```

---

## 版本

- v1.0.2：改名 digital-life，README 重构
- v1.0.0：完全重构，5 层 Persona + 结构化 Profile + 进化机制
- v0.3.0：初始版本，基于 prompt 模板

---

*你的数字生活是一部连续剧。这些 skill 帮你回看、预演、解构。*
*但最终，只有你自己能决定：这部剧的结局，值不值得。*
