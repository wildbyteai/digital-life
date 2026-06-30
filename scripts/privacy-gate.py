#!/usr/bin/env python3
"""Local deterministic privacy gate for digital-life evidence intake."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from validation_rules import (
    AUDIENCE_VALUES,
    CONFIDENCE_VALUES,
    PACKAGE_EVIDENCE_STATUS_VALUES,
    PACKAGE_ID_RE,
    PERMISSION_VALUES,
    RISK_LEVEL_VALUES,
    SEVERITY_VALUES,
    SHA256_RE,
)

PHONE_CANDIDATE_RE = re.compile(r"(?<!\d)(?:\+86\s*)?1[3-9](?:[\s-]?\d){9}(?!\d)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ID_CARD_RE = re.compile(r"(?<!\d)\d{17}[0-9Xx](?!\d)")
API_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])(?:sk-[A-Za-z0-9_-]{12,}|gh[opusr]_[A-Za-z0-9_]{12,}|xox[bp]-[A-Za-z0-9-]{12,}|AKIA[A-Z0-9]{12,})(?![A-Za-z0-9_])")
SPEAKER_PREFIX_RE = re.compile(r"^\s*(\[[^\]\n]{1,20}\]|[A-Za-z][A-Za-z0-9_ -]{0,20}|[一-鿿]{1,4})[:：]", re.MULTILINE)
WORK_TITLE_RE = re.compile(r"(?:[一-鿿A-Za-z]总|[一-鿿A-Za-z]经理|[一-鿿A-Za-z]工|[一-鿿A-Za-z]老师|客户[A-Za-z0-9一-鿿]{1,8}|供应商[A-Za-z0-9一-鿿]{1,8}|项目[A-Za-z0-9一-鿿]{1,12})")
LONG_QUOTE_THRESHOLD = 120
ID_CARD_CHECK_CODES = "10X98765432"
ID_CARD_WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
PRESET_VALUES = ("generic", "chat", "work")
RISK_COUNT_KEYS = (
    "phone",
    "id_card",
    "email",
    "address",
    "bank_card",
    "api_key_or_token",
    "third_party_name_or_alias",
    "company_or_project",
    "speaker_prefix",
    "work_title",
    "long_exact_quote",
)
ADDRESS_RE = re.compile(r"[一-鿿A-Za-z0-9]{1,20}(?:省|市|区|县|路|街|号|室|小区|大厦)")
BANK_CARD_RE = re.compile(r"(?<!\d)\d{16,19}(?!\d)")
THIRD_PARTY_RE = re.compile(r"\[(?:朋友|同事|合作方|客户|他人姓名|对方)[A-Za-z0-9一-鿿]*\]")
COMPANY_PROJECT_RE = re.compile(r"(?:公司|客户|项目|会议|行动项|内部系统|供应商|合作方)[A-Za-z0-9一-鿿_-]{0,16}")
RISK_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


def package_version(root: Path | None = None) -> str:
    """Read the package version from VERSION."""
    version_path = (root or repo_root()) / "VERSION"
    try:
        return version_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


def _compact_digits(value: str) -> str:
    return re.sub(r"[\s-]", "", value)


def detect_phone_numbers(text: str) -> list[str]:
    """Return China mainland phone-like strings with explicit separators preserved."""
    matches: list[str] = []
    for match in PHONE_CANDIDATE_RE.finditer(text):
        raw = match.group(0)
        compact = _compact_digits(raw)
        if compact.startswith("+86"):
            compact = compact[3:]
        if re.fullmatch(r"1[3-9]\d{9}", compact):
            matches.append(raw)
    return matches


def _valid_id_card(candidate: str) -> bool:
    upper = candidate.upper()
    if not re.fullmatch(r"\d{17}[0-9X]", upper):
        return False
    total = sum(int(digit) * weight for digit, weight in zip(upper[:17], ID_CARD_WEIGHTS))
    return ID_CARD_CHECK_CODES[total % 11] == upper[-1]


def detect_id_cards(text: str) -> list[str]:
    """Return 18-character China ID cards that pass checksum validation."""
    return [match.group(0) for match in ID_CARD_RE.finditer(text) if _valid_id_card(match.group(0))]


def detect_emails(text: str) -> list[str]:
    """Return email-like strings."""
    return [match.group(0) for match in EMAIL_RE.finditer(text)]


def detect_api_tokens(text: str) -> list[str]:
    """Return common token/key-like strings."""
    return [match.group(0) for match in API_TOKEN_RE.finditer(text)]


def detect_speaker_prefixes(text: str) -> list[str]:
    """Return line-start speaker labels such as [我], 张三, or User."""
    return [match.group(1).strip() for match in SPEAKER_PREFIX_RE.finditer(text)]


def detect_work_titles(text: str) -> list[str]:
    """Return simple work-title or stakeholder labels."""
    return [match.group(0) for match in WORK_TITLE_RE.finditer(text)]


def detect_long_exact_quotes(text: str) -> list[str]:
    """Return single lines or blockquote lines that exceed the long quote threshold."""
    findings: list[str] = []
    for line in text.splitlines() or [text]:
        stripped = line.strip()
        if len(stripped) > LONG_QUOTE_THRESHOLD:
            findings.append(stripped)
    return findings


def _validate_preset(preset: str) -> None:
    if preset not in PRESET_VALUES:
        raise ValueError(f"preset must be one of {PRESET_VALUES}, got: {preset!r}")


def sha256_text(text: str) -> str:
    """Return sha256 for the exact UTF-8 bytes of text, without normalization."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scan_text(text: str, *, preset: str) -> dict[str, list[str]]:
    """Run deterministic privacy detectors for a text blob."""
    _validate_preset(preset)
    return {
        "phone": detect_phone_numbers(text),
        "id_card": detect_id_cards(text),
        "email": detect_emails(text),
        "address": [match.group(0) for match in ADDRESS_RE.finditer(text)],
        "bank_card": [match.group(0) for match in BANK_CARD_RE.finditer(text)],
        "api_key_or_token": detect_api_tokens(text),
        "third_party_name_or_alias": [match.group(0) for match in THIRD_PARTY_RE.finditer(text)],
        "company_or_project": [match.group(0) for match in COMPANY_PROJECT_RE.finditer(text)],
        "speaker_prefix": detect_speaker_prefixes(text) if preset == "chat" else [],
        "work_title": detect_work_titles(text) if preset == "work" else [],
        "long_exact_quote": detect_long_exact_quotes(text),
    }


def _risk_counts(findings: dict[str, list[str]]) -> dict[str, int]:
    return {key: len(findings.get(key, [])) for key in RISK_COUNT_KEYS}


def _risk_level(counts: dict[str, int]) -> str:
    if counts["id_card"] or counts["api_key_or_token"]:
        return "high"
    if counts["phone"] or counts["bank_card"] or counts["long_exact_quote"]:
        return "medium"
    if counts["email"] or counts["address"] or counts["third_party_name_or_alias"] or counts["speaker_prefix"] or counts["work_title"] or counts["company_or_project"]:
        return "low"
    return "none"


def _status_for_risk(risk_level: str) -> str:
    if risk_level == "none":
        return "pass"
    if risk_level in ("low", "medium"):
        return "warn"
    return "block"


def _warnings(counts: dict[str, int]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if counts["third_party_name_or_alias"] or counts["speaker_prefix"] or counts["work_title"]:
        warnings.append({
            "code": "third_party_present",
            "severity": "medium",
            "message": "检测到第三方称谓、发言人前缀或职场身份线索，后续输出不得公开引用原文。",
        })
    if counts["phone"]:
        warnings.append({
            "code": "phone",
            "severity": "medium",
            "message": "检测到手机号风险，建议先脱敏后再进入后续流程。",
        })
    if counts["bank_card"]:
        warnings.append({
            "code": "bank_card",
            "severity": "medium",
            "message": "检测到银行卡样式数字风险，建议先确认并脱敏后再进入后续流程。",
        })
    if counts["long_exact_quote"]:
        warnings.append({
            "code": "long_exact_quote",
            "severity": "medium",
            "message": "检测到长段原文引用，建议使用 do_not_quote 策略。",
        })
    if counts["api_key_or_token"]:
        warnings.append({
            "code": "api_key_or_token",
            "severity": "high",
            "message": "检测到 token 或 API key 风险，禁止进入公开 demo。",
        })
    if counts["id_card"]:
        warnings.append({
            "code": "id_card",
            "severity": "high",
            "message": "检测到身份证号风险，必须先脱敏后再进入后续流程。",
        })
    return warnings


def build_privacy_report(text: str, *, preset: str, source_path: str | None, sha256: str, size_bytes: int) -> dict[str, Any]:
    """Build the privacy report without storing raw text."""
    findings = scan_text(text, preset=preset)
    counts = _risk_counts(findings)
    risk_level = _risk_level(counts)
    return {
        "schema_version": "0.1.0",
        "input": {
            "path": source_path,
            "preset": preset,
            "size_bytes": size_bytes,
            "sha256": sha256,
        },
        "status": _status_for_risk(risk_level),
        "risk_level": risk_level,
        "risk_counts": counts,
        "warnings": _warnings(counts),
        "recommended_permission": "private_only" if risk_level != "none" else "desensitized_shareable",
        "recommended_audience": "owner_only" if risk_level in ("medium", "high", "critical") else "trusted_private",
        "recommended_quote_policy": "do_not_quote" if counts["long_exact_quote"] or risk_level in ("medium", "high", "critical") else "user_review_required",
        "redaction_status": "partially_redacted" if risk_level != "none" else "redacted",
        "allowed_for_profile": risk_level not in ("high", "critical"),
        "allowed_for_public_demo": risk_level == "none",
    }


def _safe_source_id(source_path: str | None, preset: str) -> str:
    base = Path(source_path).stem if source_path else f"inline_{preset}"
    slug = re.sub(r"[^a-z0-9_-]+", "_", base.lower()).strip("_") or f"inline_{preset}"
    candidate = f"src_{slug}"
    return candidate if PACKAGE_ID_RE.fullmatch(candidate) else f"src_inline_{preset}"


def _source_type_for_preset(preset: str) -> str:
    return {
        "generic": "generic_text_redacted",
        "chat": "chat_export_redacted",
        "work": "work_note_redacted",
    }[preset]


def _source_summary_for_preset(preset: str, counts: dict[str, int]) -> str:
    risk_names = [key for key, count in counts.items() if count]
    if not risk_names:
        return f"{preset} 输入样本未检测到 v0 静态规则覆盖的明显隐私风险。"
    return f"{preset} 输入样本触发 v0 静态隐私预检规则：" + "、".join(risk_names) + "。"


def build_evidence_bundle(text: str, *, preset: str, source_path: str | None, sha256: str, privacy_report: dict[str, Any]) -> dict[str, Any]:
    """Build an evidence bundle aligned with Skill Package id/type naming."""
    counts = privacy_report["risk_counts"]
    source_id = _safe_source_id(source_path, preset)
    permission = privacy_report["recommended_permission"]
    audience = privacy_report["recommended_audience"]
    confidence = "low" if privacy_report["risk_level"] != "none" else "medium"
    source = {
        "id": source_id,
        "type": _source_type_for_preset(preset),
        "path": source_path,
        "sha256": sha256,
        "permission": permission,
        "audience": audience,
        "confidence": confidence,
        "redaction_status": privacy_report["redaction_status"],
        "third_party_present": bool(counts["third_party_name_or_alias"] or counts["speaker_prefix"] or counts["work_title"]),
        "source_summary": _source_summary_for_preset(preset, counts),
        "time_range": {"start": None, "end": None},
        "risk_counts": counts,
    }
    evidence = {
        "id": "evidence_privacy_gate_result",
        "claim": "该输入已通过 Local Evidence Intake v0 静态预检并生成风险摘要；后续流程应遵守 permission、audience 和 quote policy。",
        "source_ids": [source_id],
        "confidence": "high",
        "status": "needs_review",
        "permission": permission,
    }
    return {
        "schema_version": "0.1.0",
        "bundle_id": f"evidence_bundle_{source_id.removeprefix('src_')}",
        "sources": [source],
        "evidence": [evidence],
    }


def inspect_text(text: str, *, preset: str, source_hint: str | None = None) -> dict[str, Any]:
    """Inspect text and return privacy_report plus evidence_bundle."""
    _validate_preset(preset)
    digest = sha256_text(text)
    report = build_privacy_report(
        text,
        preset=preset,
        source_path=source_hint,
        sha256=digest,
        size_bytes=len(text.encode("utf-8")),
    )
    bundle = build_evidence_bundle(
        text,
        preset=preset,
        source_path=source_hint,
        sha256=digest,
        privacy_report=report,
    )
    return {"privacy_report": report, "evidence_bundle": bundle}


def inspect_file(path: Path, *, preset: str) -> dict[str, Any]:
    """Inspect a local UTF-8 text file and return privacy_report plus evidence_bundle."""
    _validate_preset(preset)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Input path is a directory: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Input file is empty: {path}")
    return inspect_text(text, preset=preset, source_hint=str(path))


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    """Write deterministic pretty JSON."""
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="privacy-gate",
        description="Inspect local evidence input for deterministic privacy risks.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {package_version()}")
    subparsers = parser.add_subparsers(dest="command")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect one local UTF-8 text file")
    inspect_parser.add_argument("path", help="Local file path to inspect")
    inspect_parser.add_argument("--preset", required=True, choices=PRESET_VALUES, help="Input preset")
    inspect_parser.add_argument("--json", action="store_true", help="Print combined JSON result to stdout")
    inspect_parser.add_argument("--output-dir", default=None, help="Directory to write privacy_report.json and evidence_bundle.json")
    inspect_parser.add_argument("--fail-on", default=None, choices=RISK_LEVEL_VALUES, help="Exit non-zero when risk_level reaches this level")
    return parser


def _should_fail(risk_level: str, fail_on: str | None) -> bool:
    return fail_on is not None and RISK_ORDER[risk_level] >= RISK_ORDER[fail_on]


def run_inspect(args: argparse.Namespace) -> int:
    try:
        result = inspect_file(Path(args.path), preset=args.preset)
    except (FileNotFoundError, IsADirectoryError, ValueError, UnicodeDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        dump_json(output_dir / "privacy_report.json", result["privacy_report"])
        dump_json(output_dir / "evidence_bundle.json", result["evidence_bundle"])

    if args.json or not args.output_dir:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    risk_level = result["privacy_report"]["risk_level"]
    return 1 if _should_fail(risk_level, args.fail_on) else 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "inspect":
        return run_inspect(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
