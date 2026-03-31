---
name: skill-box
description: >
  社交人格工具箱 —— 用你的数字痕迹生成各种"社交人格镜像"。
  内置5个工具，支持扩展和引用外部 skill。
  不是工具，是镜子。
metadata:
  openclaw:
    kind: skill
    platform: claude-code
    standard: agentskills
    version: "0.1.0"
---

# 🔧 Skill Box — 社交人格工具箱

> 你的数字生活是一部连续剧。这些 skill 帮你回看、预演、解构。

## 内置工具

| # | 工具 | 一句话 | 状态 |
|---|------|--------|------|
| 1 | 🪦 遗产清算 | 扫描全平台数字足迹，生成一份你不敢看的报告 | ✅ |
| 2 | 💀 社死考古 | 挖出你十年前的QQ空间/人人网黑历史 | ✅ |
| 3 | 🤖 AI替身 | 学会你说话方式，帮你自动回消息 | ✅ |
| 4 | 👻 前世 | 根据你的行为数据推演你的前世是什么 | ✅ |
| 5 | 🪦 墓志铭 | 根据你的人生轨迹自动生成墓志铭 | ✅ |

## 外部引用

| 工具 | 来源 | 说明 |
|------|------|------|
| 同事.skill | 社区 | 翻译同事的职场暗语 |
| 前任.skill | 社区 | 用聊天记录复刻前任人格 |

## 使用方式

```bash
# 安装
clawhub install skill-box

# 列出所有工具
skill-box list

# 运行某个工具
skill-box run legacy-audit      # 遗产清算
skill-box run cringe-archaeology # 社死考古
skill-box run ai-clone           # AI替身
skill-box run past-life          # 前世
skill-box run epitaph            # 墓志铭

# 添加自定义工具
skill-box add my-custom-tool

# 引用外部 skill
skill-box link colleague-skill
skill-box link ex-skill
```

## 扩展指南

详见 [扩展文档](docs/extend.md)

## License

MIT
