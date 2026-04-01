---
name: digital-life
description: >
  数字人生.skill — 5 个考古工具，用数字痕迹照见真实的自己。
  触发词：遗产清算、社死考古、AI替身、前世、墓志铭、数字人生、考古工具箱、digital life
argument-hint: "[skill-name-or-slug]"
version: "1.0.2"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# 数字人生.skill

> 你发了 3 万条朋友圈，收获 2 个真心朋友。
> 你十年前在QQ空间写的"莪の丗堺伱卜懂"，至今还在。

每一个工具都是一面镜子。你不想看的，才是你最需要看的。

---

## 触发规则

按人生时间线排列：

| # | Skill | 触发词 | Prompt 文件 |
|---|-------|--------|------------|
| 1 | 👻 前世 | 前世、上辈子 | prompts/past_life.md |
| 2 | 💀 社死考古 | 社死考古、黑历史 | prompts/cringe_archaeology.md |
| 3 | 🤖 AI替身 | AI替身、克隆我 | prompts/ai_clone.md |
| 4 | 🪦 遗产清算 | 遗产清算、数字遗产 | prompts/legacy_audit.md |
| 5 | 🪦 墓志铭 | 墓志铭、墓碑 | prompts/epitaph.md |

用户说"digital life"或"考古工具箱"时，列出全部 skill 供选择。

**确认规则：** 触发词命中后，先问"要使用 **[工具名]** 吗？"等用户确认后再执行。

---

## 数据输入

用户可以通过以下方式提供数据（不强制全部提供，说 3 句话就能启动）：

| 方式 | 能力 | 说明 |
|------|------|------|
| 文字描述 | ✅ | 直接口述行为、习惯、经历 |
| 公开 URL | ✅ 自动抓取 | 知乎、GitHub、个人博客、公众号等公开页面，agent 用 web_fetch 自动获取 |
| 浏览器代操作 | ✅ 自动获取 | 用户在自己浏览器登录社交平台后，agent 用 browser 工具直接访问和抓取 |
| 文件/截图 | ✅ 读取 | 聊天记录导出、平台年度报告截图、照片等 |

### 浏览器代操作流程

针对需要登录的平台（微博、豆瓣、小红书等），agent 可以通过浏览器代操作获取数据：

```
1. 用户在自己的浏览器里打开目标平台并确认已登录
2. agent 用 browser(profile="user") 连接用户浏览器
3. agent 导航到用户主页/个人页面
4. agent 用 snapshot/screenshot 获取页面内容
5. agent 提取行为特征用于推演
```

**支持的平台和获取方式：**

| 平台 | 方式 | 能拿到什么 |
|------|------|-----------|
| 微博 | browser + bb-browser skill | 个人主页、发帖记录、关注列表 |
| 知乎 | browser + bb-browser skill | 回答列表、关注话题、赞同内容 |
| 豆瓣 | browser + bb-browser skill | 书影音标记、日记、小组 |
| GitHub | web_fetch 或 browser | repos、contributions、star 列表 |
| 小红书 | browser 截图 | 笔记内容、收藏列表 |
| 微信 | 聊天记录导出 | 聊天记录 txt/html（不可 browser 代操作） |
| 支付宝/网易云 | 用户截图 | 年度报告、账单截图 |

**agent 操作规则：**
- 只浏览和截图，不发表任何内容
- 不修改任何设置或账号信息
- 获取完数据后退出浏览器
- 原始数据不保存，只保留分析结果

---

## 安全边界

1. **隐私保护**：所有分析本地进行，不上传任何服务器
2. **不输出原始数据**：profile 只保留行为模式分析，不保留用户的原始文本
3. **不替代心理诊断**：本工具用于自我反思，不是心理咨询或精神科诊断
4. **不生成有害内容**：profile 不包含人身攻击、歧视性语言或鼓励自伤的内容

---

## Persona 5 层结构

每个 skill 输出一个结构化的 **数字人生 Profile**，采用 5 层结构：

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
2. **收集输入** → 问 2-3 个关键问题（不要一次全问）。**支持三种数据获取方式**：
   - 用户直接口述行为/习惯
   - 用户给 URL → `web_fetch` 自动抓取
   - 用户在浏览器里登录社交平台 → `browser(profile="user")` 代操作获取
3. **读取文件** → layer0/{skill}.md（硬规则）+ profiles/{skill}.json（输出模板）+ prompts/{skill}.md（生成指令）
4. **生成 Profile** → 按 persona 5 层结构 + 对应 profile 模板
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

用户可以对已有的 profile 进行追加或纠正：

- **追加**：用户说"补充""追加"→ 读取 prompts/evolution.md，增量合并
- **纠正**：用户说"不对""应该是"→ 识别纠正维度，生成 correction 记录
- **版本管理**：每次更新递增版本号，保留旧版备份，可回滚

---

## 管理命令

| 命令 | 说明 |
|------|------|
| `列出 profile` | 扫描 profiles/ 目录，列出所有已生成的 profile |
| `回滚 profile {slug}` | 将 profile 回滚到指定版本 |
| `删除 profile {slug}` | 确认后删除指定 profile |

---

## 外部 Skill

| Skill | 安装方式 | 哲学维度 |
|-------|----------|----------|
| 同事.skill | `clawhub install colleague-skill` | 维特根斯坦：语言游戏 |
| 前任.skill | `clawhub install ex-skill` | 弗洛伊德：哀悼与忧郁 |
