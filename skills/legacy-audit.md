# 遗产清算.skill

> 扫描你所有社交账号，生成一份"数字遗产报告"。

## 功能

扫描全平台数字足迹，生成一份你不忍卒读的报告。

## 输入

| 平台 | 格式 | 获取方式 |
|------|------|----------|
| 微信朋友圈 | 导出 json | 微信数据导出工具 |
| 微博 | API / 爬虫 | 微博开放平台 |
| 小红书 | 导出 json | 手动导出 |
| QQ空间 | 导出 xml | QQ空间备份工具 |
| 知乎 | 导出 json | 知乎数据导出 |
| 抖音 | 导出 json | 抖音数据导出 |
| B站 | 导出 json | B站数据导出 |

## 输出

```json
{
  "summary": {
    "total_posts": 5482,
    "total_platforms": 7,
    "years_active": 14,
    "wasted_hours": 2847,
    "regret_ratio": 0.73
  },
  "platforms": {
    "wechat_moments": {
      "total": 1247,
      "earliest": "2013-06-15",
      "deleted_ratio": 0.23,
      "most_liked": "今天辞职了",
      "most_forwarded": "摔倒视频",
      "regret_posts": ["2016年一定要脱单！"]
    }
  },
  "highlights": {
    "cringe_peak_year": 2012,
    "most_active_day": "2012-08-20 (14 posts)",
    "biggest_lie": "从明天开始健身",
    "longest_silence": "127 days (2020 pandemic)"
  }
}
```

## 执行流程

1. 收集各平台数据（本地文件或 API）
2. 统计总量、时间分布、高频词
3. 识别"后悔帖"（删除比例高的时期）
4. 计算"浪费时间指数"
5. 生成报告

## 隐私

- 全部本地分析
- 不上传任何数据
- 报告仅存本地
