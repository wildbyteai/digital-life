# profiles 目录说明

这个目录分成两类内容：

- `profiles/contracts/`：机器可读契约（skill 路径、命名规则、必填字段）
- `profiles/templates/`：仓库内置的输出模板，供 agent 生成 profile 时读取
- `profiles/history/`：历史快照目录，保存每次追加/纠正前的备份

## 当前文件约定

### 1. 当前生效的 profile

写在 `profiles/` 根目录，命名统一为：

```text
profiles/{skill}_{slug}.json
profiles/{skill}_{slug}.md
```

例如：

```text
profiles/legacy_audit_zhangsan.json
profiles/legacy_audit_zhangsan.md
```

### 2. 历史快照

写在 `profiles/history/`，命名统一为：

```text
profiles/history/{skill}_{slug}_{timestamp}.json
profiles/history/{skill}_{slug}_{timestamp}.md
```

例如：

```text
profiles/history/legacy_audit_zhangsan_2026-04-01T120000+0800.json
profiles/history/legacy_audit_zhangsan_2026-04-01T120000+0800.md
```

## Git 约定

- 真实用户 profile 和历史快照默认被 `.gitignore` 忽略，避免把私人数据提交到仓库
- `templates/` 下的模板文件会被保留在仓库中

## 运维命令

```bash
python scripts/profile-manager.py list
python scripts/profile-manager.py init --skill legacy_audit --slug demo
python scripts/profile-manager.py snapshot --skill legacy_audit --slug demo
python scripts/profile-manager.py rollback --skill legacy_audit --slug demo
python scripts/profile-manager.py doctor
```
