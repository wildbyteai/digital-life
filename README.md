# 数字人生.skills

> *"你不是被数据定义的人。*
>
> *但你会被自己反复留下的痕迹，慢慢塑形。"*

每一个工具都是一面镜子。它不替你下结论，只把那些你已经重复了很多次的选择，翻译成你终于愿意承认的话。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blueviolet)](https://docs.openclaw.ai)
[![clawhub](https://img.shields.io/badge/clawhub-published-green)](https://clawhub.com)
[![Version](https://img.shields.io/badge/version-1.3.2--beta-1E6B5B)](CHANGELOG.md)

用你的数字痕迹照见真实的自己  
每个 skill 生成**结构化 Profile + 人话解读**，可迭代、可纠错、可回滚，也能把“发生了什么”翻译成“这说明了什么”

[安装](#安装) · [5 个工具](#5-个考古工具) · [使用](#使用) · [数据获取](#数据获取) · [效果示例](#效果示例)

---

## 为什么它值得做

- 它不是把用户包装成一个“深刻人设”，而是把真实行为证据翻译成可以面对的自我认知
- 它不是只写一段好看的文案，而是同时产出 `JSON Profile + Markdown 报告`，让解释和数据能一起落地
- 它不是一次性占卜，而是支持追加、纠正、历史快照，让“人会变化”这件事有版本管理
- 它不是靠偷换概念制造震撼，而是用可验证的数字痕迹，把羞耻、表演、惯性和遗憾说清楚
- 它不是默认把隐私送上云，而是把真实用户输出默认排除出 Git 仓库

---

## 它怎么看人

- **先证据，后解释**：所有判断先回到发言、习惯、平台行为和时间跨度，不凭空编造深刻
- **先理解，后刺痛**：把表演、拖延、删帖、沉默先看作生存策略，再讨论代价
- **先行为，后意义**：哲思不是名词堆砌，而是把一个人长期重复的矛盾命名出来
- **先追问，后定论**：每份报告最后都留一个具体到行为的追问，而不是替用户把人生盖棺定论

---

## 5 个考古工具

按人生时间线排列：

| # | 工具 | 触发词 | 核心问题 | 哲学锚点 |
|---|------|--------|----------|----------|
| 1 | 👻 前世 | 前世、上辈子 | 你以为是性格的东西，只是惯性吗？ | 佛教：业力与因果 |
| 2 | 💀 社死考古 | 社死考古、黑历史 | 你从什么时候开始学会表演体面的？ | 阿伦特：公共/私人的边界 |
| 3 | 🤖 AI替身 | AI替身、克隆我 | 公开的你和私密的你，是同一个人吗？ | 图灵测试：什么是"你" |
| 4 | 📊 遗产清算 | 遗产清算、数字遗产 | 你留下了什么？ | 海德格尔：向死而生 |
| 5 | 🪦 墓志铭 | 墓志铭、墓碑 | 你想被记住的方式，和你正在过的生活，一致吗？ | 塞涅卡：论生命的短促 |

---

## 安装

对话安装：

```text
安装 digital-life
```

CLI 安装：

```bash
npx clawhub install digital-life
```

---

## 使用

说出触发词，agent 确认后进入引导模式：

```text
我想做遗产清算
```

每个 skill 的执行流程：

```text
① 引导语（告诉你这个 skill 要干什么）
② 问你要什么（2-4 个关键问题，不过度追问）
③ 拿数据（browser 代操作 / 口述 / 文件上传）
④ 分析 + 落地
⑤ 存在追问（逼你面对一个真实的问题）
```

**严酷但温暖**：不说鸡汤，不说"加油"。用你自己的数字痕迹，讲一个你一直在回避、但又已经写在行为里的故事。

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

```text
📊 数字生命审计
  - 数字生命：18 年，3 个平台
  - 总发言：~5000 条
  - 估算浪费时间：2847 小时 = 118 天 = 28 本书
  - 最大的谎言："明天开始早睡"
  - 存在追问：如果明天这些平台全部关闭，你最想留下哪一条？

🧭 你其实在购买什么
  - 不是单纯在刷，而是在反复购买“我还和世界连着”的感觉

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
- **叙事原则**：先证据，后张力，再追问；先理解防御，再谈代价
- **Browser 代操作**：用户已登录时，agent 直接抓个人页面数据（最准确）
- **隐私优先**：所有分析本地进行，不上传任何服务器
- **安全边界**：agent 确认触发，不会泛激活；数据获取分级降级
- **进化机制**：用户追加新信息或纠正错误时，Profile 增量更新
- **契约驱动**：`skill-contract.json` 统一定义 skill 路径和字段要求
- **可运维**：`profile-manager.py` 提供初始化、快照、回滚、删除、巡检

---

## 哲学背景

5 个 skill 的设计灵感，来自三个永恒的自我认知问题：

1. **我是谁？** → 前世（习惯 = 业力）+ AI替身（表演 = 面具）
2. **我留下了什么？** → 社死考古（黑历史 = 真相）+ 遗产清算（时间 = 生命）
3. **我想成为谁？** → 墓志铭（终点 = 起点）

参考：佛教业力论、阿伦特公共/私人理论、图灵测试、海德格尔向死而生、塞涅卡论生命短促。

---

## 产出

每次分析会生成一份**当前生效 profile**，并在后续追加、纠正时保存**历史快照**：

```text
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

- **JSON** — 结构化 Profile，供后续追加、纠正、版本管理
- **Markdown** — 人话解读，包含完整分析、关键洞察、数字墓碑（如果适用）
- **templates/** — 仓库内置模板；生成结果默认写在 `profiles/` 根目录
- **history/** — 每次追加、纠正前的快照，便于回滚
- **隐私默认优先** — 真实 profile 和历史快照已加入 `.gitignore`，避免把私人数据提交到 GitHub

---

## 技术细节

### 单人模式

- 保留单一契约源：`profiles/contracts/skill-contract.json`
- 保留核心运维脚本：`scripts/profile-manager.py`
- 保留一个校验入口：`scripts/validate-skill.py`
- 删除双脚本校验和重型架构文档，降低维护负担

### 管理命令

| 命令 | 说明 |
|------|------|
| `python scripts/profile-manager.py list` | 列出 `profiles/` 根目录中的当前 profile |
| `python scripts/profile-manager.py init --skill legacy_audit --slug demo` | 按模板初始化 profile |
| `python scripts/profile-manager.py snapshot --skill legacy_audit --slug demo` | 把当前 profile 保存到 `profiles/history/` |
| `python scripts/profile-manager.py rollback --skill legacy_audit --slug demo` | 回滚到最近快照（或 `--timestamp` 指定） |
| `python scripts/profile-manager.py delete --skill legacy_audit --slug demo --yes --with-history` | 删除当前 profile，并可选删除历史 |
| `python scripts/profile-manager.py doctor` | 批量校验当前所有 profile 的结构和关键字段 |

### 开发者自检

维护 prompt、模板或目录结构后，运行：

```bash
python scripts/validate-skill.py
```

补充运维校验：

```bash
python scripts/profile-manager.py doctor
```

自检会检查：

- 契约、模板、路径映射是否一致
- `prompts / layer0 / references / templates` 是否齐全
- 示例输出、图标资源和运维脚本是否完整
- `profiles/` 目录和 `.gitignore` 的隐私规则是否存在

### 核心设计

- **Persona 5 层结构**：Layer 0 硬规则 → Layer 1 身份 → Layer 2 表达 → Layer 3 思维 → Layer 4 边界
- **结构化 Profile**：JSON 存数据，Markdown 讲故事，可追加、可纠正、可回滚
- **叙事原则**：先证据，后张力，再追问；先理解防御，再谈代价
- **Browser 代操作**：用户已登录时，agent 直接抓个人页面数据（最准确）
- **隐私优先**：所有分析本地进行，不上传任何服务器
- **安全边界**：agent 确认触发，不会泛激活；数据获取分级降级
- **进化机制**：用户追加新信息或纠正错误时，Profile 增量更新
- **契约驱动**：`skill-contract.json` 统一定义 skill 路径和字段要求
- **可运维**：`profile-manager.py` 提供初始化、快照、回滚、删除、巡检

### 目录结构

```text
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
│   ├── profile-manager.py    # profile 生命周期管理（init/list/snapshot/rollback/delete/doctor）
│   └── validate-skill.py     # 单一自检入口
├── prompts/
│   ├── persona_builder.md    # 通用 5 层 Persona 生成模板
│   ├── evolution.md          # 追加/纠正流程模板
│   ├── past_life.md          # 👻 前世 prompt
│   ├── cringe_archaeology.md # 💀 社死考古 prompt
│   ├── ai_clone.md           # 🤖 AI替身 prompt
│   ├── legacy_audit.md       # 📊 遗产清算 prompt
│   └── epitaph.md            # 🪦 墓志铭 prompt
├── profiles/
│   ├── README.md             # 当前 profile / 模板 / 快照约定
│   ├── contracts/
│   │   └── skill-contract.json
│   ├── templates/            # 5 个 skill 的结构化输出模板
│   └── history/              # 追加 / 纠正前的历史快照
├── layer0/                   # 各 skill 的 Layer 0 硬规则
└── references/
    └── *.md                  # 各 skill 的方法论文档
```

### 版本

- v1.3.2-beta：强化人文与哲思表达层，为主文档、共享 Persona 模板和 5 个 prompts 增加“先证据、后张力、再追问”的统一写作原则
- 当前仓库仅保留这一条 beta 版本线，历史正式版标签和版本列表已清理

---

*你的数字生活不是素材库，而是一份正在发生的自传。*  
*这些 skill 不替你写结论，只把你已经写下的部分，读给你听。*
