#!/usr/bin/env python3
"""
Skill Box — 数字人格考古工具箱 CLI
Usage: python -m skillbox <skill> [input_file]
"""

import argparse
import sys
import os
import io

# Fix Windows console encoding for emoji/Chinese output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skillbox.api import SkillBoxAPI
from skillbox.skills import legacy_audit, cringe_archaeology, ai_clone, past_life, epitaph


__version__ = "0.2.0"

SKILLS = {
    "legacy-audit": {
        "name": "遗产清算",
        "icon": "🪦",
        "desc": "以死者视角回看自己的数字生命",
        "handler": legacy_audit.run,
    },
    "cringe-archaeology": {
        "name": "社死考古",
        "icon": "💀",
        "desc": "找回还没学会表演的自己",
        "handler": cringe_archaeology.run,
    },
    "ai-clone": {
        "name": "AI替身",
        "icon": "🤖",
        "desc": "当你的社交行为可以被完全复制，'你'还剩什么",
        "handler": ai_clone.run,
    },
    "past-life": {
        "name": "前世",
        "icon": "👻",
        "desc": "你以为是'性格'的东西，可能只是惯性",
        "handler": past_life.run,
    },
    "epitaph": {
        "name": "墓志铭",
        "icon": "🪦",
        "desc": "在活着的时候，看到自己的结局",
        "handler": epitaph.run,
    },
}


def cmd_list(args):
    """列出所有可用工具"""
    print(f"\n🔧 Skill Box v{__version__} — 数字人格考古工具箱")
    print("   你不想看的，才是你最需要看的。")
    print("=" * 50)

    for key, info in SKILLS.items():
        print(f"\n  {info['icon']}  {info['name']} ({key})")
        print(f"     {info['desc']}")

    print(f"\n{'=' * 50}")
    print("  用法: python -m skillbox run <skill> [input_file]")
    print("  示例: python -m skillbox run epitaph my_life.txt")
    print()


def cmd_run(args):
    """运行指定工具"""
    skill_key = args.skill

    if skill_key not in SKILLS:
        print(f"❌ 未找到工具: {skill_key}")
        print("   运行 python -m skillbox list 查看所有可用工具")
        sys.exit(1)

    info = SKILLS[skill_key]
    print(f"\n{info['icon']} {info['name']} — {info['desc']}")
    print("=" * 50)

    # 读取输入
    if args.input:
        if os.path.isfile(args.input):
            with open(args.input, "r", encoding="utf-8") as f:
                user_input = f.read()
            print(f"📄 已读取输入文件: {args.input}")
        else:
            user_input = args.input
            print(f"📝 使用命令行输入")
    else:
        print("\n请输入你的描述（Ctrl+D / Ctrl+Z 结束）：\n")
        if sys.platform == "win32":
            sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
        user_input = sys.stdin.read()

    if not user_input.strip():
        print("❌ 输入为空，请提供内容。")
        sys.exit(1)

    # 运行
    api = SkillBoxAPI()
    result = info["handler"](api, user_input)
    print(f"\n{'=' * 50}")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="skillbox",
        description="🔧 Skill Box — 数字人格考古工具箱",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="列出所有可用工具")

    run_p = sub.add_parser("run", help="运行指定工具")
    run_p.add_argument("skill", help="工具名称 (legacy-audit / cringe-archaeology / ai-clone / past-life / epitaph)")
    run_p.add_argument("input", nargs="?", help="输入文件路径或文本")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
