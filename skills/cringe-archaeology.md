# 社死考古.skill

> 自动翻遍你的QQ空间、人人网、贴吧老帖，把十年前的中二发言全部挖出来。

## 功能

考古你的互联网黑历史，生成一条"社死时间线"。

## 输入

| 平台 | 格式 | 说明 |
|------|------|------|
| QQ空间 | 导出 xml/html | 包含日志、说说、留言板 |
| 人人网 | 导出 html | 包含状态、日志、相册 |
| 百度贴吧 | 账号页面 | 帖子和回复 |
| 新浪博客 | 导出 xml | 博客文章 |
| 校内网 | 导出 html | 人人网前身 |

## 输出

```json
{
  "timeline": [
    {
      "date": "2009-03-14",
      "platform": "qqzone",
      "type": "说说",
      "content": "今天的心情：💔 莪卜知道该说什么...",
      "cringe_score": 95,
      "tags": ["非主流", "伤感", "火星文"],
      "screenshot_available": true
    }
  ],
  "stats": {
    "total_cringe_posts": 347,
    "peak_cringe_year": 2010,
    "mars_text_ratio": 0.43,
    "45_degree_selfies": 23,
    "shared_emo_songs": 67,
    "biggest_cringe": "莪の丗堺伱卜懂"
  },
  "verdict": {
    "cringe_index": 87,
    "recommendation": "趁早删了吧，或者勇敢面对",
    "survival_tip": "你的同龄人也一样黑历史遍地"
  }
}
```

## 执行流程

1. 解析导出文件（XML/HTML/JSON）
2. 按时间排序所有内容
3. 识别火星文、非主流用语、emoji 滥用
4. 计算"社死指数"（0-100）
5. 生成时间线 + 统计报告

## 社死指数算法

```
cringe_score = base_score
  + mars_text_detected * 15
  + selfie_45_degree * 10
  + emo_song_shared * 8
  + broken_heart_emoji * 5
  + "莪"替代"我" * 12
  + 3_days_no_wash_selfie * 20
```

## 隐私

- 全部本地分析
- 输出报告可选择性脱敏
- 支持只生成统计不保留原文
