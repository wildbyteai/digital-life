---
name: digital-persona
description: >
  数字人格考古工具箱 — 5 个 skill，用数字痕迹照见真实的自己。
  触发词：遗产清算、社死考古、AI替身、前世、墓志铭、数字人格、考古工具箱、digital persona
argument-hint: "[skill-name-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# Digital Persona — 数字人格考古工具箱

每一个工具都是一面镜子。你不想看的，才是你最需要看的。

---

## 触发规则

| Skill | 触发词 | Prompt 文件 |
|-------|--------|------------|
| 前世 | 前世、上辈子 | prompts/past_life.md |
| 社死考古 | 社死考古、黑历史 | prompts/cringe_archaeology.md |
| AI替身 | AI替身、克隆我 | prompts/ai_clone.md |
| 遗产清算 | 遗产清算、数字遗产 | prompts/legacy_audit.md |
| 墓志铭 | 墓志铭、墓碑 | prompts/epitaph.md |

用户说"digital-persona"或"考古工具箱"时，列出全部 skill 供选择。

**确认规则：** 触发词命中后，先问"要使用 **[工具名]** 吗？"等用户确认后再执行。

---

## Persona 5 层结构

每个 skill 输出一个结构化的 **数字人格 Profile**，采用 5 层结构：

| 层 | 名称 | 含义 |
|----|------|------|
| Layer 0 | 硬规则 | 不可违背的核心行为准则（读取 layer0/{skill}.md） |
| Layer 1 | 身份锚定 | 你是谁、数字生命跨度 |
| Layer 2 | 表达风格 | 口头禅、高频词、标点、说话方式 |
| Layer 3 | 思维/决策 | 优先级、回避、推进、判断方式 |
| Layer 4 | 边界与雷区 | 不接受、会回避、情绪触发器 |

Layer 0 质量标准：每条规则必须是"在什么情况下会怎么做"的完整表述，不能是形容词。

---

## 执行流程

1. **触发确认** → 一句话介绍，确认要用
2. **收集输入** → 问 2-3 个关键问题（不要一次全问）
3. **读取文件** → layer0/{skill}.md（硬规则）+ profiles/{skill}.json（输出模板）
4. **生成 Profile** → 读取 prompts/{skill}.md，按其中指令生成
5. **展示摘要** → 5-8 行摘要，确认后写入文件
6. **写入文件** → profiles/{skill}_{slug}.json + .md
7. **存在追问** → 以一个有力的存在论问题结束

---

## Profile 输出

```
profiles/{skill}_{slug}.json   # 结构化数据
profiles/{skill}_{slug}.md     # 可读版本
```

---

## 进化机制

- **追加**：用户说"补充""追加"→ 读取 prompts/evolution.md，增量合并
- **纠正**：用户说"不对""应该是"→ 识别纠正维度，生成 correction 记录
- **版本管理**：每次更新递增版本号，保留旧版备份

---

## 外部 Skill

| Skill | 安装方式 | 哲学维度 |
|-------|----------|----------|
| 同事.skill | `clawhub install colleague-skill` | 维特根斯坦：语言游戏 |
| 前任.skill | `clawhub install ex-skill` | 弗洛伊德：哀悼与忧郁 |
