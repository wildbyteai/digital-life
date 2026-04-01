---
name: digital-life
description: >
  数字人生.skills — 5 个考古工具，用数字痕迹照见真实的自己。
  触发词：遗产清算、社死考古、AI替身、前世、墓志铭、数字人生、考古工具箱、digital life
argument-hint: "[skill-name-or-slug]"
version: 1.2.0
license: MIT
metadata:
  openclaw:
    homepage: https://github.com/wildbyteai/digital-life
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# 数字人生.skills

> 你发了 3 万条朋友圈，收获 2 个真心朋友。
> 你十年前在QQ空间写的"莪の丗堺伱卜懂"，至今还在。

每一个工具都是一面镜子。你不想看的，才是你最需要看的。

---

## 触发规则

按人生时间线排列：

| # | Skill | 触发词 | 引导语 |
|---|-------|--------|--------|
| 1 | 👻 前世 | 前世、上辈子 | "你现在的执念，可能只是上辈子没做完的事。" |
| 2 | 💀 社死考古 | 社死考古、黑历史 | "越尴尬的内容，往往越真实。准备好了吗？" |
| 3 | 🤖 AI替身 | AI替身、克隆我 | "你有多久没用真实的语气和人说话了？" |
| 4 | 🪦 遗产清算 | 遗产清算、数字遗产 | "你在数字世界花掉的时间，够换几条命？" |
| 5 | 🪦 墓志铭 | 墓志铭、墓碑 | "在活着的时候，读到自己的结局。" |

用户说"digital life"或"考古工具箱"时，列出全部 skill 并附引导语，让用户选择。

**确认规则：** 触发词命中后，显示引导语，等用户确认后再执行。

---

## 数据输入

用户可以通过以下方式提供数据（不强制全部提供，说 3 句话就能启动）：

| 方式 | 能力 | 说明 |
|------|------|------|
| 文字描述 | ✅ | 直接口述行为、习惯、经历——最低门槛 |
| 浏览器代操作 | ✅ **推荐** | 用户在自己浏览器登录后，agent 用 browser 工具直接抓取个人页面 |
| 文件/截图 | ✅ 读取 | 聊天记录导出、平台年度报告截图、照片等 |
| 公开 URL | ⚠️ 谨慎 | 公开页面存在同名风险，必须先确认是用户本人再抓取 |

### 浏览器代操作流程

```
1. 用户在自己的浏览器里打开目标平台并确认已登录
2. agent 用 browser(profile="user") 连接用户浏览器
3. agent 导航到用户主页/个人页面
4. agent 用 snapshot/screenshot 获取页面内容
5. agent 提取行为特征，不保存原始数据
```

**支持的平台：**

| 平台 | 方式 | 能拿到什么 |
|------|------|-----------|
| 微博 | browser | 个人主页、发帖记录、关注列表 |
| 知乎 | browser | 回答列表、关注话题、赞同内容 |
| 豆瓣 | browser | 书影音标记、日记、小组 |
| GitHub | web_fetch 或 browser | repos、contributions、star 列表 |
| 小红书 | browser 截图 | 笔记内容、收藏列表 |
| 微信 | 聊天记录导出 | 聊天记录 txt/html |

**操作铁律：** 只看不碰。浏览和截图可以，发表/修改/删除一律禁止。

---

## 安全边界

1. **隐私保护**：所有分析本地进行，不上传任何服务器
2. **不输出原始数据**：profile 只保留行为模式分析，不保留用户的原始文本
3. **不替代心理诊断**：本工具用于自我反思，不是心理咨询或精神科诊断
4. **不生成有害内容**：profile 不包含人身攻击、歧视性语言或鼓励自伤的内容
5. **Layer 0 硬规则**：每个 skill 有独立的不可违背的行为准则（读取 `layer0/{skill}.md`）

---

## 执行流程

每个 skill 执行以下 6 步：

### Step 1：触发确认

显示 skill 名称 + 引导语，等用户确认。

### Step 2：收集输入

读取 `prompts/{skill}.md`，按其中的「怎么问」执行——问 2-3 个关键问题，不要一次全问。

支持三种数据获取方式：
- 用户直接口述（最低门槛，3 句话启动）
- 用户给 URL → 确认是本人后 `web_fetch` 抓取
- 用户在浏览器登录 → `browser(profile="user")` 代操作

### Step 3：读取规则

读取以下文件：
- `layer0/{skill}.md` — 硬规则，不可违背
- `references/{skill}.md` — 方法论和分析框架
- `profiles/templates/{skill}.json` — 输出模板

### Step 4：分析生成

按 prompts/{skill}.md 的「产出什么」执行分析。

### Step 5：展示摘要

展示 5-8 行摘要，附一句「确认生成？还是需要调整？」

用户确认后写入文件。如果用户说「不对」→ 进入纠正流程。

### Step 6：写入文件 + 存在追问

输出到本地文件系统：

```
profiles/{skill}_{slug}.json                    # 当前生效的结构化数据
profiles/{skill}_{slug}.md                      # 当前生效的可读报告
profiles/history/{skill}_{slug}_{timestamp}.json  # 追加/纠正前的历史快照
profiles/history/{skill}_{slug}_{timestamp}.md    # 追加/纠正前的历史快照
```

最后以一个**存在追问**结束——必须具体到行为，不要鸡汤。

---

## 进化机制

- **追加**：用户说"补充""追加"→ 增量合并到已有 profile
- **纠正**：用户说"不对""应该是"→ 生成 correction 记录，更新 profile
- **版本管理**：每次更新先把旧版保存到 `profiles/history/`，文件名带时间戳，可回滚

---

## 管理命令

| 命令 | 说明 |
|------|------|
| `列出 profile` | 扫描 `profiles/` 根目录，列出当前生效的 profile |
| `回滚 profile {slug}` | 从 `profiles/history/` 选择一个快照恢复为当前版本 |
| `删除 profile {slug}` | 确认后删除指定 profile |

---

## 外部 Skill

| Skill | 安装方式 | 哲学维度 |
|-------|----------|---------|
| 同事.skill | `clawhub install colleague-skill` | 维特根斯坦：语言游戏 |
| 前任.skill | `clawhub install ex-skill` | 弗洛伊德：哀悼与忧郁 |
