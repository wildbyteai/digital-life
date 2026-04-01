# 🔧 Skill Box — 数字人格考古工具箱

> 你发了 3 万条朋友圈，收获 2 个真心朋友。
> 你十年前在QQ空间写的"莪の丗堺伱卜懂"，至今还在。
> 你的支付宝年度账单告诉你：你花了 47% 的钱在吃上面。

![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![CLI](https://img.shields.io/badge/CLI-Runnable-brightgreen)

---

## 为什么做这个项目

我们每天在网上留下痕迹。一条朋友圈，一次深夜搜索，一个凌晨三点的收藏。

这些痕迹散落在 7 个平台、14 年时间里，我们从来不回头看。不是因为忘了。**是因为不敢。**

苏格拉底说："未经审视的人生不值得过。"但审视自己的数字人生变成了不可能的任务——数据太多、平台太多、时间线太碎。

**Skill Box 做的事情很简单：帮你把碎片拼成一面镜子。**

不是为了好看，是为了看清。

---

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 列出所有工具
python -m skillbox list

# 运行某个工具（交互式输入）
python -m skillbox run epitaph

# 运行（从文件读取输入）
python -m skillbox run past-life my_profile.txt

# 运行（直接在命令行输入）
python -m skillbox run epitaph "我35岁，程序员，单身，养了两只猫，每天加班到11点"
```

### 配置 API（可选）

编辑 `skillbox/config.yaml`，填入你的 LLM API 信息：

```yaml
api:
  base_url: "https://api.openai.com/v1"  # 或任何 OpenAI 兼容 API
  api_key: "sk-xxx"
  model: "gpt-4o"
```

**不配也能用！** 没有 API 时会输出提示词，你可以手动粘贴到 ChatGPT / Claude / Kimi 等任何 AI 助手。

支持的 API：OpenAI / DeepSeek / Ollama / 任何 OpenAI 兼容格式。

---

## 🛠 内置工具

### 🪦 1. 遗产清算（legacy-audit）

> 哲学维度：海德格尔 — 向死而生

以"死者"的视角回看自己的数字生命。扫描全平台数字足迹，生成一份你不忍卒读的报告。

```bash
python -m skillbox run legacy-audit
# 输入：你在各平台的活跃情况、发帖量、使用年限等
```

**核心问题：** 你在数字世界留下的，是遗产还是垃圾？

---

### 💀 2. 社死考古（cringe-archaeology）

> 哲学维度：汉娜·阿伦特 — 公共领域与私人领域

挖出你十年前的QQ空间/人人网黑历史。不是为了嘲笑，是为了找回"还没学会表演"的自己。

```bash
python -m skillbox run cringe-archaeology
# 输入：你回忆的旧帖、说说、QQ空间日志等
```

**核心问题：** 你删掉的那些"社死"内容里，是不是恰恰藏着你最真实的表达？

---

### 🤖 3. AI替身（ai-clone）

> 哲学维度：图灵 — 什么是"你"？

分析你的沟通模式，拆分"公开人格"与"私密人格"，生成一个能替你说话的 AI。

```bash
python -m skillbox run ai-clone
# 输入：你对自己的社交习惯的描述
```

**核心问题：** 当你的社交行为可以被完全复制，"你"还剩什么？

---

### 👻 4. 前世（past-life）

> 哲学维度：佛教 — 业力与因果

从你的行为模式中推演"前世"。不是算命，是帮你看到你以为是"性格"的东西可能只是"惯性"。

```bash
python -m skillbox run past-life
# 输入：你的性格特征、行为习惯、童年经历
```

**核心问题：** 如果前世塑造了今生的行为模式，那今生有没有可能打破这个循环？

---

### 🪦 5. 墓志铭（epitaph）

> 哲学维度：塞涅卡 — 论生命的短促

在活着的时候，读到自己死后别人会怎么写你。五种风格：正经 / 毒舌 / 文艺 / 打工人 / 哲思。

```bash
python -m skillbox run epitaph
# 输入：你的生活状态、工作、经历、遗憾
```

**核心问题：** 你想被记住的方式，和你正在过的生活，一致吗？

---

## 📁 项目结构

```
skill-box/
├── SKILL.md                      # 工具箱定义
├── README.md                     # 你正在看的
├── LICENSE                       # MIT
├── requirements.txt              # Python 依赖
├── skillbox/                     # Python 包
│   ├── __main__.py               # CLI 入口
│   ├── api.py                    # API 调用层
│   ├── config.yaml               # API 配置
│   └── skills/                   # 5 个工具脚本
│       ├── legacy_audit.py       # 🪦 遗产清算
│       ├── cringe_archaeology.py # 💀 社死考古
│       ├── ai_clone.py           # 🤖 AI替身
│       ├── past_life.py          # 👻 前世
│       └── epitaph.py            # 🪦 墓志铭
├── skills/                       # 工具文档（SKILL.md 定义）
├── external/                     # 外部引用注册表
└── docs/                         # 扩展文档
```

---

## 设计哲学

### "考古"而非"分析"

你十年前在 QQ 空间写的"莪の丗堺伱卜懂"不是错误数据，是你某个时刻的真实。我们不应该用"黑历史"三个字抹杀过去的自己。

### "镜子"而非"报告"

报告告诉你数字。镜子让你看见自己。数字可以造假，镜子不能。

### "向死而生"而非"活得更好"

这些 skill 帮你预演死亡——不是为了恐惧，是为了重新理解活着这件事值多少钱。

---

## License

MIT

*你的数字生活是一部连续剧。这些 skill 帮你回看、预演、解构。*
*但最终，只有你自己能决定：这部剧的结局，值不值得。*
