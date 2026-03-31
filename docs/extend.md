# 扩展指南

## 如何添加自定义工具

### 方式一：命令行

```bash
skill-box add my-tool
```

会自动在 `skills/` 目录创建 `my-tool.md` 模板文件，并更新 `config.yaml`。

### 方式二：手动创建

1. 在 `skills/` 目录下创建 `your-tool.md`
2. 按以下模板编写：

```markdown
# your-tool.skill

> 一句话描述。

## 功能
...

## 输入
| 数据 | 格式 | 说明 |
|------|------|------|
| xxx | json | ... |

## 输出
```json
{
  "result": "..."
}
```

## 执行流程
1. ...
2. ...
```

3. 在 `config.yaml` 中注册：

```yaml
skills:
  your-tool:
    name: "你的工具"
    icon: "🛠"
    description: "一句话描述"
    enabled: true
    module: "skills/your-tool.md"
```

---

## 如何引用外部 Skill

### 方式一：从 ClawHub 安装

```bash
clawhub install colleague-skill
skill-box link colleague-skill
```

### 方式二：手动注册

在 `external/registry.yaml` 中添加：

```yaml
registry:
  - name: my-external-skill
    display_name: "我的外部工具"
    description: "一句话描述"
    source: github
    install: "git clone https://github.com/xxx/skill.git"
    enabled: true
```

---

## 工具定义规范

每个工具至少包含：

- **name**: 工具名称
- **description**: 一句话描述
- **功能**: 具体功能说明
- **输入**: 需要什么数据
- **输出**: 产生什么结果
- **执行流程**: 步骤说明

可选：

- **隐私说明**: 数据处理方式
- **警告**: 使用注意事项
- **示例**: 效果展示
