# 数字人生.skills

> *"你发了 3 万条朋友圈，收获 2 个真心朋友。"*
>
> *"你十年前在QQ空间写的'莪の丗堺伱卜懂'，至今还在。"*
>
> *"你的支付宝年度账单告诉你：你花了 47% 的钱在吃上面。"*

每一个工具都是一面镜子。你不想看的，才是你最需要看的。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blueviolet)](https://docs.openclaw.ai)
[![clawhub](https://img.shields.io/badge/clawhub-published-green)](https://clawhub.com)
[![Version](https://img.shields.io/badge/version-1.2.0-1E6B5B)](CHANGELOG.md)

![数字人生标志](assets/digital-life-large.svg)

&nbsp;

用你的数字痕迹照见真实的自己  
每个 skill 生成**结构化 Profile + 人话解读**——可迭代、可纠错、可回滚

[安装](#安装) · [5 个工具](#5-个考古工具) · [使用](#使用) · [数据获取](#数据获取) · [效果示例](#效果示例)

---

## 为什么它有意思

- 不是玄学皮肤的聊天玩具，而是有结构、有模板、有回滚的 skill 包
- 不是只生成一段文案，而是同时产出 `JSON Profile + Markdown 报告`
- 不是一次性输出，而是支持追加、纠正、历史快照
- 不是默认把隐私送上云，而是把真实用户输出默认排除出 Git 仓库

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

说出触发词，agent 确认后进入引导模式：

```
我想做遗产清算
```

每个 skill 的执行流程：

```
① 引导语（告诉你这个 skill 要干什么）
② 问你要什么（2-4 个关键问题，不过度追问）
③ 拿数据（browser 代操作 / 口述 / 文件上传）
④ 分析 + 落地
⑤ 存在追问（逼你面对一个真实的问题）
```

**严酷但温暖**：不说鸡汤，不说"加油"。用你自己的数字痕迹，讲一个你不敢对自己讲的故事。

---

## 数据获取

三级优先级：

| 优先级 | 方式 | 说明 |
|--------|------|------|
| 🥇 最高 | **Browser 代操作** | 你登录社交平台，agent 直接抓你的个人页面（最准确） |
| 🥈 备选 | 你口述 / 上传文件 | 粘贴聊天记录、截图、年度报告 |
| 🥉 降级 | 公开 URL | ⚠️ 有同名风险，必须先确认是本人 |

Agent 会根据你提供的信息类型，自动选择最高效的数据获取路径。

---

## 产出

每次分析会生成一份**当前生效 profile**，并在后续追加/纠正时保存**历史快照**：

```
profiles/
├── README.md
├── past_life_{slug}.json                # 当前生效 profile
├── past_life_{slug}.md
├── cringe_archaeology_{slug}.json
├── cringe_archaeology_{slug}.md
├── ai_clone_{slug}.json
├── ai_clone_{slug}.md
├── legacy_audit_{slug}.json
├── legacy_audit_{slug}.md
├── epitaph_{slug}.json
├── epitaph_{slug}.md
├── history/
│   └── legacy_audit_{slug}_{timestamp}.json
└── templates/
    ├── past_life.json
    ├── cringe_archaeology.json
    ├── ai_clone.json
    ├── legacy_audit.json
    └── epitaph.json
```

- **JSON** — 结构化 Profile，供后续追加/纠正/版本管理
- **Markdown** — 人话解读，包含完整分析、关键洞察、数字墓碑（如果适用）
- **templates/** — 仓库内置模板；生成结果默认写在 `profiles/` 根目录
- **history/** — 每次追加/纠正前的快照，便于回滚
- **隐私默认优先** — 真实 profile 和历史快照已加入 `.gitignore`，避免把私人数据提交到 GitHub

---

## 管理命令

| 命令 | 说明 |
|------|------|
| `列出 profile` | 扫描 `profiles/` 根目录，列出当前生效的 profile |
| `回滚 profile {slug}` | 从 `profiles/history/` 选择一个快照恢复为当前版本 |
| `删除 profile {slug}` | 确认后删除指定 profile |

---

## 开发者自检

维护 prompt、模板或目录结构后，可运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-skill.ps1
```

或跨平台运行：

```bash
python scripts/validate-skill.py
```

这个脚本会检查：

- 5 个 skill 的 `prompts / layer0 / references / templates` 是否齐全
- 模板 JSON 的 `skill` 字段是否和文件名一致
- `profiles/` 目录和 `.gitignore` 的隐私规则是否存在

---

## 仓库示例

仓库内置了两组**纯虚构、脱敏**的示例输出，方便你在 GitHub 上直接看成品：

- [legacy_audit_demo.md](examples/legacy_audit_demo.md)
- [legacy_audit_demo.json](examples/legacy_audit_demo.json)
- [ai_clone_demo.md](examples/ai_clone_demo.md)
- [ai_clone_demo.json](examples/ai_clone_demo.json)

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
- **结构化 Profile**：JSON 存数据，Markdown 讲故事，可追加、可纠正、可回滚
- **Browser 代操作**：用户已登录时，agent 直接抓个人页面数据（最准确）
- **隐私优先**：所有分析本地进行，不上传任何服务器
- **安全边界**：agent 确认触发，不会泛激活；数据获取分级降级
- **进化机制**：用户追加新信息或纠正错误时，Profile 增量更新

---

## 哲学背景

5 个 skill 的设计灵感，来自三个永恒的自我认知问题：

1. **我是谁？** → 前世（习惯=业力）+ AI替身（表演=面具）
2. **我留下了什么？** → 社死考古（黑历史=真相）+ 遗产清算（时间=生命）
3. **我想成为谁？** → 墓志铭（终点=起点）

参考：佛教业力论、阿伦特公共/私人理论、图灵测试、海德格尔向死而生、塞涅卡论生命短促。

---

## 目录结构

```
digital-life/
├── SKILL.md                  # Agent 指令（执行流程 + 安全边界）
├── README.md
├── LICENSE
├── VERSION
├── CHANGELOG.md
├── agents/
│   └── openai.yaml           # UI 元数据（显示名、图标、默认提示词）
├── assets/
│   ├── digital-life-small.svg
│   └── digital-life-large.svg
├── examples/
│   ├── README.md             # 脱敏示例说明
│   ├── legacy_audit_demo.md
│   ├── legacy_audit_demo.json
│   ├── ai_clone_demo.md
│   └── ai_clone_demo.json
├── scripts/
│   ├── validate-skill.ps1    # Windows 自检
│   └── validate-skill.py     # 跨平台自检
├── prompts/
│   ├── persona_builder.md    # 通用 5 层 Persona 生成模板
│   ├── evolution.md          # 追加/纠正流程模板
│   ├── past_life.md          # 👻 前世 prompt
│   ├── cringe_archaeology.md # 💀 社死考古 prompt
│   ├── ai_clone.md           # 🤖 AI替身 prompt
│   ├── legacy_audit.md       # 🪦 遗产清算 prompt
│   └── epitaph.md            # 🪦 墓志铭 prompt
├── profiles/
│   ├── README.md             # 当前 profile / 模板 / 快照约定
│   ├── templates/            # 5 个 skill 的结构化输出模板
│   └── history/              # 追加 / 纠正前的历史快照
├── layer0/                   # 各 skill 的 Layer 0 硬规则
└── references/               # 各 skill 的方法论文档
```

---

## 版本

- v1.2.0：补齐 `agents/openai.yaml`、SVG 图标、脱敏示例输出与双端校验脚本，仓库从“可读”提升到“可展示、可调用、可校验”
- v1.1.0：统一 profile 命名规范，补齐 `profiles/templates` 与 `profiles/history`，默认忽略真实用户输出，避免私人数据误提交
- v1.0.3：改名「数字人生.skills」，补全 5 个 prompt（引导语 + 数据获取 + 落地输出），SKILL.md 重写执行流程
- v1.0.2：改名 digital-life，README 重构
- v1.0.0：完全重构，5 层 Persona + 结构化 Profile + 进化机制
- v0.3.0：初始版本，基于 prompt 模板

---

*你的数字生活是一部连续剧。这些 skill 帮你回看、预演、解构。*
*但最终，只有你自己能决定：这部剧的结局，值不值得。*
