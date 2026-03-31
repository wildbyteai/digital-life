#!/usr/bin/env python3
"""
Skill Box — 社交人格工具箱管理器
Usage: skill-box <command> [options]
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path


__version__ = "0.1.0"


class SkillBox:
    """社交人格工具箱"""

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.config_path = self.base_dir / "config.yaml"
        self.skills_dir = self.base_dir / "skills"
        self.external_dir = self.base_dir / "external"
        self.registry_path = self.external_dir / "registry.yaml"

        self.config = self._load_yaml(self.config_path)
        self.registry = self._load_yaml(self.registry_path)

    def _load_yaml(self, path: Path) -> dict:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def list(self):
        """列出所有可用工具"""
        print("🔧 Skill Box — 社交人格工具箱")
        print("=" * 50)

        # 内置工具
        skills = self.config.get("skills", {})
        if skills:
            print("\n📦 内置工具:")
            for key, info in skills.items():
                icon = info.get("icon", "🛠")
                name = info.get("name", key)
                desc = info.get("description", "")
                enabled = info.get("enabled", True)
                status = "✅" if enabled else "❌"
                print(f"  {status} {icon} {name} ({key})")
                print(f"     {desc}")

        # 外部引用
        registry = self.registry.get("registry", [])
        if registry:
            print(f"\n🔗 外部引用 (共 {len(registry)} 个可用):")
            for item in registry:
                name = item.get("display_name", item.get("name", ""))
                desc = item.get("description", "")
                enabled = item.get("enabled", False)
                status = "🟢" if enabled else "⚪"
                print(f"  {status} {name}")
                print(f"     {desc}")

        print()

    def run(self, tool_name: str):
        """运行指定工具"""
        skills = self.config.get("skills", {})

        if tool_name in skills:
            info = skills[tool_name]
            module_path = self.base_dir / info.get("module", "")

            print(f"\n{info.get('icon', '🛠')} 运行: {info.get('name', tool_name)}")
            print("=" * 50)

            if module_path.exists():
                with open(module_path, "r", encoding="utf-8") as f:
                    content = f.read()
                print(f"\n📖 工具定义: {module_path}")
                print(f"\n{content[:500]}...")
                print(f"\n💡 完整功能请参考: {module_path}")
            else:
                print(f"❌ 工具定义文件不存在: {module_path}")
            return

        # 检查外部引用
        registry = self.registry.get("registry", [])
        for item in registry:
            if item.get("name") == tool_name:
                print(f"\n🔗 外部工具: {item.get('display_name', tool_name)}")
                print(f"   {item.get('description', '')}")
                print(f"   安装: {item.get('install', 'N/A')}")
                if not item.get("enabled", False):
                    print(f"   ⚠️  未启用，运行: skill-box link {tool_name}")
                return

        print(f"❌ 未找到工具: {tool_name}")
        print("   运行 skill-box list 查看所有可用工具")

    def link(self, tool_name: str):
        """链接外部工具"""
        registry = self.registry.get("registry", [])
        for item in registry:
            if item.get("name") == tool_name:
                item["enabled"] = True

                # 保存
                with open(self.registry_path, "w", encoding="utf-8") as f:
                    yaml.dump(self.registry, f, allow_unicode=True, default_flow_style=False)

                print(f"✅ 已链接: {item.get('display_name', tool_name)}")
                print(f"   {item.get('description', '')}")
                print(f"   运行 skill-box run {tool_name} 来使用")
                return

        print(f"❌ 未找到外部工具: {tool_name}")
        print("   在 external/registry.yaml 中注册后再链接")

    def unlink(self, tool_name: str):
        """取消链接外部工具"""
        registry = self.registry.get("registry", [])
        for item in registry:
            if item.get("name") == tool_name:
                item["enabled"] = False

                with open(self.registry_path, "w", encoding="utf-8") as f:
                    yaml.dump(self.registry, f, allow_unicode=True, default_flow_style=False)

                print(f"⚪ 已取消链接: {item.get('display_name', tool_name)}")
                return

        print(f"❌ 未找到: {tool_name}")

    def add(self, tool_name: str):
        """添加自定义工具"""
        tool_path = self.skills_dir / f"{tool_name}.md"

        template = f"""# {tool_name}.skill

> 一句话描述你的工具。

## 功能
描述工具功能...

## 输入
- 数据类型：...

## 输出
- 输出格式：...

## 执行流程
1. ...
2. ...
3. ...
"""

        with open(tool_path, "w", encoding="utf-8") as f:
            f.write(template)

        # 更新 config
        skills = self.config.get("skills", {})
        skills[tool_name] = {
            "name": tool_name,
            "icon": "🛠",
            "description": "自定义工具（待编辑）",
            "enabled": True,
            "module": f"skills/{tool_name}.md",
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

        print(f"✅ 已添加自定义工具: {tool_name}")
        print(f"   编辑: {tool_path}")
        print(f"   运行: skill-box run {tool_name}")

    def remove(self, tool_name: str):
        """移除自定义工具"""
        skills = self.config.get("skills", {})

        if tool_name not in skills:
            print(f"❌ 未找到内置工具: {tool_name}")
            return

        tool_path = self.base_dir / skills[tool_name].get("module", "")
        if tool_path.exists():
            tool_path.unlink()

        del skills[tool_name]

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

        print(f"✅ 已移除: {tool_name}")


def main():
    parser = argparse.ArgumentParser(
        prog="skill-box",
        description="🔧 Skill Box — 社交人格工具箱"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    subparsers.add_parser("list", help="列出所有可用工具")

    run_parser = subparsers.add_parser("run", help="运行指定工具")
    run_parser.add_argument("tool", help="工具名称")

    link_parser = subparsers.add_parser("link", help="链接外部工具")
    link_parser.add_argument("tool", help="外部工具名称")

    unlink_parser = subparsers.add_parser("unlink", help="取消链接")
    unlink_parser.add_argument("tool", help="工具名称")

    add_parser = subparsers.add_parser("add", help="添加自定义工具")
    add_parser.add_argument("tool", help="工具名称")

    rm_parser = subparsers.add_parser("remove", help="移除工具")
    rm_parser.add_argument("tool", help="工具名称")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    box = SkillBox()

    if args.command == "list":
        box.list()
    elif args.command == "run":
        box.run(args.tool)
    elif args.command == "link":
        box.link(args.tool)
    elif args.command == "unlink":
        box.unlink(args.tool)
    elif args.command == "add":
        box.add(args.tool)
    elif args.command == "remove":
        box.remove(args.tool)


if __name__ == "__main__":
    main()
