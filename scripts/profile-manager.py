#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{6}[+-]\d{4}$")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H%M%S%z")


def load_contract(root: Path) -> Tuple[dict, Dict[str, dict]]:
    contract_path = root / "profiles" / "contracts" / "skill-contract.json"
    contract = load_json(contract_path)

    skills = contract.get("skills", [])
    skill_map: Dict[str, dict] = {}
    for item in skills:
        slug = item.get("slug")
        if not slug:
            raise ValueError("skill-contract.json contains skill item without slug")
        if slug in skill_map:
            raise ValueError(f"duplicate skill slug in contract: {slug}")
        skill_map[slug] = item
    return contract, skill_map


def profile_root(contract: dict, root: Path) -> Path:
    return root / contract.get("profile_root", "profiles")


def history_root(contract: dict, root: Path) -> Path:
    return root / contract.get("history_root", "profiles/history")


def current_paths(contract: dict, root: Path, skill: str, slug: str) -> Tuple[Path, Path]:
    p_root = profile_root(contract, root)
    return (
        p_root / f"{skill}_{slug}.json",
        p_root / f"{skill}_{slug}.md",
    )


def read_updated_at(path: Path) -> str:
    try:
        payload = load_json(path)
    except Exception:
        return "-"
    return str(payload.get("updated_at", "-"))


def discover_current_profiles(contract: dict, skill_map: Dict[str, dict], root: Path) -> List[Tuple[str, str, str, str]]:
    p_root = profile_root(contract, root)
    rows: List[Tuple[str, str, str, str]] = []

    for skill in sorted(skill_map.keys()):
        for json_path in sorted(p_root.glob(f"{skill}_*.json")):
            suffix = json_path.stem[len(skill) + 1 :]
            if not suffix:
                continue
            md_path = p_root / f"{skill}_{suffix}.md"
            status = "ok" if md_path.exists() else "missing_md"
            rows.append((skill, suffix, read_updated_at(json_path), status))
    return rows


def print_rows(rows: List[Tuple[str, str, str, str]]) -> None:
    if not rows:
        print("No current profile files found in profiles/ root.")
        return

    headers = ("skill", "slug", "updated_at", "status")
    widths = [
        max(len(headers[0]), max(len(r[0]) for r in rows)),
        max(len(headers[1]), max(len(r[1]) for r in rows)),
        max(len(headers[2]), max(len(r[2]) for r in rows)),
        max(len(headers[3]), max(len(r[3]) for r in rows)),
    ]
    fmt = f"{{:<{widths[0]}}}  {{:<{widths[1]}}}  {{:<{widths[2]}}}  {{:<{widths[3]}}}"

    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for row in rows:
        print(fmt.format(*row))


def list_profiles(contract: dict, skill_map: Dict[str, dict], root: Path, skill: str | None) -> int:
    rows = discover_current_profiles(contract, skill_map, root)
    if skill:
        rows = [r for r in rows if r[0] == skill]
    print_rows(rows)
    return 0


def init_profile(contract: dict, skill_map: Dict[str, dict], root: Path, skill: str, slug: str, force: bool) -> int:
    if skill not in skill_map:
        print(f"Unknown skill: {skill}")
        return 2

    json_path, md_path = current_paths(contract, root, skill, slug)
    if not force and (json_path.exists() or md_path.exists()):
        print(f"Profile already exists: {json_path.name} / {md_path.name}. Use --force to overwrite.")
        return 2

    template_path = root / skill_map[skill]["template_path"]
    template = load_json(template_path)
    template["skill"] = skill
    template["slug"] = slug
    template["updated_at"] = now_iso()
    if "version" not in template:
        template["version"] = 1
    if "corrections" not in template or not isinstance(template["corrections"], list):
        template["corrections"] = []

    dump_json(json_path, template)
    md_title = skill_map[skill].get("display_name", skill)
    md_payload = (
        f"# {md_title} Profile ({slug})\n\n"
        f"> skill: {skill}\n"
        f"> slug: {slug}\n"
        f"> updated_at: {template['updated_at']}\n\n"
        "在这里写入本次可读报告。\n"
    )
    md_path.write_text(md_payload, encoding="utf-8")

    print(f"Initialized profile: {json_path}")
    print(f"Initialized report:  {md_path}")
    return 0


def snapshot_profile(contract: dict, root: Path, skill: str, slug: str, timestamp: str | None) -> int:
    json_path, md_path = current_paths(contract, root, skill, slug)
    if not json_path.exists() or not md_path.exists():
        print("Current profile files not found. Snapshot aborted.")
        return 2

    ts = timestamp or now_timestamp()
    if not TIMESTAMP_RE.match(ts):
        print("Invalid timestamp format. Expected: YYYY-MM-DDTHHMMSS+0800")
        return 2

    h_root = history_root(contract, root)
    h_root.mkdir(parents=True, exist_ok=True)

    history_json = h_root / f"{skill}_{slug}_{ts}.json"
    history_md = h_root / f"{skill}_{slug}_{ts}.md"
    shutil.copy2(json_path, history_json)
    shutil.copy2(md_path, history_md)

    print(f"Snapshot created: {history_json.name}")
    print(f"Snapshot created: {history_md.name}")
    return 0


def find_history_candidates(contract: dict, root: Path, skill: str, slug: str) -> List[Tuple[str, Path, Path]]:
    h_root = history_root(contract, root)
    candidates: List[Tuple[str, Path, Path]] = []

    for json_path in sorted(h_root.glob(f"{skill}_{slug}_*.json")):
        stem = json_path.stem
        prefix = f"{skill}_{slug}_"
        if not stem.startswith(prefix):
            continue
        ts = stem[len(prefix) :]
        md_path = h_root / f"{skill}_{slug}_{ts}.md"
        candidates.append((ts, json_path, md_path))
    return sorted(candidates, key=lambda x: x[0])


def rollback_profile(contract: dict, root: Path, skill: str, slug: str, timestamp: str | None) -> int:
    candidates = find_history_candidates(contract, root, skill, slug)
    if not candidates:
        print("No history snapshots found for this profile.")
        return 2

    chosen = None
    if timestamp:
        for item in candidates:
            if item[0] == timestamp:
                chosen = item
                break
        if not chosen:
            print(f"Snapshot timestamp not found: {timestamp}")
            return 2
    else:
        chosen = candidates[-1]

    ts, history_json, history_md = chosen
    if not history_md.exists():
        print(f"History markdown missing for snapshot: {ts}")
        return 2

    current_json, current_md = current_paths(contract, root, skill, slug)
    shutil.copy2(history_json, current_json)
    shutil.copy2(history_md, current_md)

    print(f"Rolled back profile to snapshot: {ts}")
    return 0


def delete_profile(contract: dict, root: Path, skill: str, slug: str, with_history: bool, yes: bool) -> int:
    if not yes:
        print("Refused to delete without --yes.")
        return 2

    removed = 0
    current_json, current_md = current_paths(contract, root, skill, slug)
    for path in (current_json, current_md):
        if path.exists():
            path.unlink()
            removed += 1

    if with_history:
        for _, history_json, history_md in find_history_candidates(contract, root, skill, slug):
            if history_json.exists():
                history_json.unlink()
                removed += 1
            if history_md.exists():
                history_md.unlink()
                removed += 1

    print(f"Removed files: {removed}")
    return 0


def validate_profile(contract: dict, skill_map: Dict[str, dict], root: Path, skill: str, slug: str) -> int:
    if skill not in skill_map:
        print(f"Unknown skill: {skill}")
        return 2

    json_path, md_path = current_paths(contract, root, skill, slug)
    errors: List[str] = []

    if not json_path.exists():
        errors.append(f"Missing profile json: {json_path}")
    if not md_path.exists():
        errors.append(f"Missing profile markdown: {md_path}")

    payload = {}
    if json_path.exists():
        try:
            payload = load_json(json_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Invalid JSON profile: {exc}")

    template = {}
    template_path = root / skill_map[skill]["template_path"]
    if template_path.exists():
        try:
            template = load_json(template_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Invalid template JSON: {exc}")
    else:
        errors.append(f"Missing template file: {template_path}")

    required_keys = skill_map[skill].get("required_top_level_keys") or list(template.keys())
    if payload:
        for key in required_keys:
            if key not in payload:
                errors.append(f"Missing required key: {key}")

        if payload.get("skill") != skill:
            errors.append(f"'skill' mismatch: expected {skill}, got {payload.get('skill')}")

        if payload.get("slug") not in (None, slug):
            errors.append(f"'slug' mismatch: expected {slug}, got {payload.get('slug')}")

        if "corrections" in payload and not isinstance(payload["corrections"], list):
            errors.append("'corrections' must be a list")

        if "source_summary" in payload and not isinstance(payload["source_summary"], dict):
            errors.append("'source_summary' must be an object")

    if md_path.exists() and md_path.stat().st_size == 0:
        errors.append("Markdown report is empty")

    if errors:
        print("Validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Validation passed: {skill}_{slug}")
    return 0


def doctor(contract: dict, skill_map: Dict[str, dict], root: Path) -> int:
    rows = discover_current_profiles(contract, skill_map, root)
    if not rows:
        print("No current profiles found. Nothing to validate.")
        return 0

    failed = 0
    for skill, slug, _, _ in rows:
        code = validate_profile(contract, skill_map, root, skill, slug)
        if code != 0:
            failed += 1
    if failed:
        print(f"Doctor finished with failures: {failed}")
        return 1
    print(f"Doctor finished successfully. Profiles checked: {len(rows)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage digital-life profiles.")
    parser.add_argument("--root", default=None, help="Repository root path. Defaults to script parent.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List current profiles.")
    p_list.add_argument("--skill", help="Filter by skill slug.")

    p_init = sub.add_parser("init", help="Initialize a profile from template.")
    p_init.add_argument("--skill", required=True)
    p_init.add_argument("--slug", required=True)
    p_init.add_argument("--force", action="store_true")

    p_snapshot = sub.add_parser("snapshot", help="Create a history snapshot from current profile.")
    p_snapshot.add_argument("--skill", required=True)
    p_snapshot.add_argument("--slug", required=True)
    p_snapshot.add_argument("--timestamp", help="Override timestamp with YYYY-MM-DDTHHMMSS+0800.")

    p_rollback = sub.add_parser("rollback", help="Rollback current profile from history snapshot.")
    p_rollback.add_argument("--skill", required=True)
    p_rollback.add_argument("--slug", required=True)
    p_rollback.add_argument("--timestamp", help="Snapshot timestamp. Default: latest.")

    p_delete = sub.add_parser("delete", help="Delete current profile and optionally history.")
    p_delete.add_argument("--skill", required=True)
    p_delete.add_argument("--slug", required=True)
    p_delete.add_argument("--with-history", action="store_true")
    p_delete.add_argument("--yes", action="store_true")

    p_validate = sub.add_parser("validate", help="Validate one current profile.")
    p_validate.add_argument("--skill", required=True)
    p_validate.add_argument("--slug", required=True)

    sub.add_parser("doctor", help="Validate all current profiles in profiles/ root.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else repo_root()
    contract, skill_map = load_contract(root)

    if args.command == "list":
        return list_profiles(contract, skill_map, root, args.skill)
    if args.command == "init":
        return init_profile(contract, skill_map, root, args.skill, args.slug, args.force)
    if args.command == "snapshot":
        return snapshot_profile(contract, root, args.skill, args.slug, args.timestamp)
    if args.command == "rollback":
        return rollback_profile(contract, root, args.skill, args.slug, args.timestamp)
    if args.command == "delete":
        return delete_profile(contract, root, args.skill, args.slug, args.with_history, args.yes)
    if args.command == "validate":
        return validate_profile(contract, skill_map, root, args.skill, args.slug)
    if args.command == "doctor":
        return doctor(contract, skill_map, root)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
