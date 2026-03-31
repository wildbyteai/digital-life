# AI替身.skill

> 训练一个你的"社交替身"，自动帮你回消息。

## 功能

从你的聊天记录中学习说话方式，生成一个能替你回消息的 AI。

## 输入

| 数据 | 格式 | 说明 |
|------|------|------|
| 微信聊天记录 | txt/csv | 和不同人的对话 |
| 朋友圈文案 | json | 你的公开发言 |
| 微博发言 | json | 更随意的表达 |
| 短信记录 | xml/csv | 正式/紧急场景 |

## 输出

```json
{
  "persona": {
    "reply_speed": "slow (avg 3.2min)",
    "top_words": ["哈哈", "好的", "随便", "没事"],
    "emoji_preference": ["🐱", "🐶", "😂"],
    "passive_index": 0.92,
    "initiate_ratio": 0.08,
    "response_patterns": {
      "when_asked_to_eat": "你定我都行",
      "when_asked_if_angry": "没有啊",
      "when_tired": "还好吧",
      "when_happy": "哈哈哈哈哈哈"
    }
  },
  "clone": {
    "model": "claude-sonnet-4-20250514",
    "system_prompt": "...",
    "test_results": {
      "spouse_test": "✅ 通过",
      "friend_test": "⚠️ 偶尔穿帮",
      "boss_test": "❌ 太随意了"
    }
  }
}
```

## 执行流程

1. 解析聊天记录，提取对话模式
2. 分析高频词、回复速度、emoji 使用
3. 构建 persona profile
4. 生成 system prompt
5. 测试 clone 质量（和真实回复对比）
6. 输出可部署的 clone

## ⚠️ 警告

- 如果被发现对面不是你本人，后果自负
- 对老婆/女朋友不要用（被抓概率 99%）
- 对老板可以用（反正他也分不出来）
- 本工具仅供娱乐，不承担任何社交事故责任

## 隐私

- 全部本地训练
- clone 模型仅存本地
- 支持随时删除
