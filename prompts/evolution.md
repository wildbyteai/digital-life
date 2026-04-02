# 进化模板：追加与纠正

## 追加模式（用户提供了新的数字痕迹）

### 流程

1. 读取用户提供的新内容（文件/文本/截图）
2. 读取现有的 profile 文件（`profiles/{skill}_{slug}.json` 和 `.md`）
   - 先执行：`python scripts/profile-manager.py validate --skill {skill} --slug {slug}`
3. 分析新内容与现有 profile 的关系：
   - **新增**：是否有之前没覆盖的维度？
   - **修正**：是否有与现有结论矛盾的证据？
   - **深化**：是否让某个已有维度更详细？
4. 生成增量更新摘要，向用户展示：

```text
新材料发现了：
- 新增：{新维度/新证据}
- 修正：{与之前矛盾的地方}
- 深化：{让哪个部分更详细了}

要更新 profile 吗？还是保持之前的结论？
```

5. 用户确认后，执行增量合并：
   - 新增 → 追加到对应字段
   - 修正 → 覆盖旧值，记录修正原因
   - 深化 → 扩充已有字段
6. 在写入新版本前，执行 snapshot：
   - `python scripts/profile-manager.py snapshot --skill {skill} --slug {slug}`
7. 更新当前 profile 中的 `updated_at` 和 `version`
8. 更新后再次校验：
   - `python scripts/profile-manager.py validate --skill {skill} --slug {slug}`

### 版本管理

每次追加自动递增版本号（v1 → v2 → v3）。  
保留历史版本的快照，路径：`profiles/history/{skill}_{slug}_{timestamp}.json`  
需要回滚时使用：`python scripts/profile-manager.py rollback --skill {skill} --slug {slug} --timestamp {timestamp}`

---

## 纠正模式（用户说"不对"/"应该是这样"）

### 流程

1. 识别纠正内容属于哪个维度（Layer 0-4）
2. 生成 correction 记录：

```json
{
  "timestamp": "{ISO时间}",
  "target_layer": "{layer编号}",
  "target_field": "{被纠正的字段}",
  "old_value": "{旧值}",
  "new_value": "{新值}",
  "user_reason": "{用户给的原因}",
  "applied": true
}
```

3. 应用修正到 profile 文件
4. 在 profile 末尾追加 correction 记录
5. 向用户确认：

```text
已修正：
- {字段}：{旧值} → {新值}
- 原因：{用户给的原因}

还有其他需要改的吗？
```

6. 修正后执行：
   - `python scripts/profile-manager.py validate --skill {skill} --slug {slug}`

---

## 通用规则

1. **不丢失已有信息**：追加和修正都不能删除已有字段，只能新增或覆盖
2. **保留修正历史**：每次修正都记录，用户可以回滚到任意版本
3. **修正优先级高于初始生成**：如果用户纠正了 Layer 0 的规则，新规则优先级最高
4. **追加文件的格式兼容**：支持 JSON、Markdown、纯文本、图片截图
5. **让新证据改变判断，而不是硬塞进旧结论**：如果新增材料明显推翻之前的理解，就重写结论，不要维持表面一致
6. **保持同一份报告的叙事气质**：不为了显得体面而弱化真相，也不为了扎心而夸张用户的问题
