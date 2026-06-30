# Local Evidence Intake v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, read-only, deterministic privacy gate that scans user-provided digital-life input before it enters profile/package flows.

**Architecture:** Add `scripts/privacy-gate.py` as a focused CLI + importable API with deterministic scanners, report builders, and JSON output helpers. Keep v0 independent from the six existing skill execution flows, but add minimal documentation and hard-gate guidance so future browser/WebFetch intake can call `inspect_text()` before LLM analysis.

**Tech Stack:** Python 3.11-compatible standard library only (`argparse`, `hashlib`, `json`, `re`, `pathlib`, `dataclasses` optional), existing `unittest` suite in `scripts/test_scripts.py`, existing validation constants in `scripts/validation_rules.py`.

## Global Constraints

- Do not add third-party dependencies.
- Do not call LLMs from `privacy-gate.py`.
- Do not log or store raw user text in generated JSON outputs.
- Do not implement platform login, browser automation, WebFetch interception, WeChat database parsing, vault encryption, or cross-skill graph logic in v0.
- `evidence_bundle.sources[]` must use `id` / `type`, not `source_id` / `source_type`.
- Reuse existing enums from `validation_rules.py` where applicable: `PERMISSION_VALUES`, `AUDIENCE_VALUES`, `CONFIDENCE_VALUES`, `SEVERITY_VALUES`, `PACKAGE_EVIDENCE_STATUS_VALUES`, `PACKAGE_ID_RE`, `SHA256_RE`.
- Add a new `RISK_LEVEL_VALUES = ("none", "low", "medium", "high", "critical")`; do not confuse it with `SEVERITY_VALUES`.
- Do not commit unless the user explicitly asks; this plan intentionally omits commit steps.

---

## File Structure

### Create

- `scripts/privacy-gate.py`  
  Owns CLI, importable API, deterministic detection rules, report construction, output writing, and version display.

- `examples/evidence_fixtures/README.md`  
  Documents that fixtures are fictional, redacted, and safe for tests.

- `examples/evidence_fixtures/chat/wechat_redacted_sample.txt`  
  Fictional chat fixture covering speaker prefixes, third-party aliases, long quotes, and redacted private context.

- `examples/evidence_fixtures/work/feishu_meeting_note_sample.md`  
  Fictional work fixture covering meeting notes, work titles, project names, action items, and token-like strings.

- `examples/evidence_fixtures/generic/personal_journal_sample.md`  
  Fictional generic fixture covering address-like text, email, phone-like text, and personal reflection.

- `docs/local_evidence_intake.md`  
  User/developer documentation for privacy gate purpose, CLI, Python API, presets, risk levels, and v0 limits.

### Modify

- `scripts/validation_rules.py`  
  Add `RISK_LEVEL_VALUES`; optionally add focused validation helpers only if needed by tests.

- `scripts/test_scripts.py`  
  Import `privacy-gate.py` as `pg` and add `TestPrivacyGateDetectors`, `TestPrivacyGateReports`, and `TestPrivacyGateCli`.

- `README.md`  
  Add a minimal link from data/privacy sections to `docs/local_evidence_intake.md` without doing broad README redesign.

- `SKILL.md`  
  Add hard-gate privacy rule in `安全边界` and data collection flow: high-sensitive material from files/browser/WebFetch should pass privacy gate before analysis/profile write.

---

## Task 1: Add fictional evidence fixtures

**Files:**
- Create: `examples/evidence_fixtures/README.md`
- Create: `examples/evidence_fixtures/chat/wechat_redacted_sample.txt`
- Create: `examples/evidence_fixtures/work/feishu_meeting_note_sample.md`
- Create: `examples/evidence_fixtures/generic/personal_journal_sample.md`

**Interfaces:**
- Consumes: none.
- Produces: Stable fixture paths used by tests and CLI examples:
  - `examples/evidence_fixtures/chat/wechat_redacted_sample.txt`
  - `examples/evidence_fixtures/work/feishu_meeting_note_sample.md`
  - `examples/evidence_fixtures/generic/personal_journal_sample.md`

- [ ] **Step 1: Create fixture README**

Write `examples/evidence_fixtures/README.md`:

```markdown
# Evidence Fixtures

这些文件是 `privacy-gate.py` 的虚构测试样本，用于验证本地隐私预检规则。

约束：

- 所有姓名、地址、项目、联系方式和聊天内容均为虚构或占位。
- 不包含真实用户、真实公司、真实客户或真实聊天记录。
- fixture 只用于 deterministic tests，不代表完整隐私审计。
- 如需增加样本，必须使用虚构内容，并覆盖至少一个明确的风险规则。
```

- [ ] **Step 2: Create chat fixture**

Write `examples/evidence_fixtures/chat/wechat_redacted_sample.txt`:

```text
# FICTIONAL REDACTED CHAT SAMPLE
# 这是虚构脱敏样本，不来自真实聊天记录。

[我]: 最近和[朋友A]聊到那个合作，我还是有点犹豫。
[朋友A]: 你上次不是说先做一个小 demo 再决定吗？
[我]: 对，但[合作方B]一直催，说王总也在等结果。
[朋友A]: 那你别直接答应，先把边界写清楚。

[我]: 这里有一段很长的原话模拟，用来测试 long_exact_quote 检测。这个段落故意超过一百二十个字符，描述一个虚构聊天里的连续表达：我不是不想合作，而是担心需求边界不清、时间投入失控、最后变成谁都说不清楚的长期承诺。

[系统备注]: 以上内容全部虚构，姓名均为占位符。
```

- [ ] **Step 3: Create work fixture**

Write `examples/evidence_fixtures/work/feishu_meeting_note_sample.md`:

```markdown
# FICTIONAL FEISHU MEETING NOTE SAMPLE

> 这是虚构飞书会议纪要样本，不来自真实公司或真实会议。

## 会议：虚构项目 Alpha 边界确认

参会人：王总、李经理、张工、客户A、记录人

### 背景

虚构项目 Alpha 需要在两天内确认是否进入 demo 阶段。客户A 提到内部系统链接 `https://internal.example.invalid/project-alpha`，该链接为无效占位。

### 讨论

- 王总：先确认 demo 能验证什么，不要直接承诺长期合作。
- 李经理：行动项是整理 3 个最小场景。
- 张工：注意不要把 token-like 字符串 `sk-fictional-not-a-real-key-123456` 写入对外材料。

### 行动项

1. 张工整理 demo 范围。
2. 李经理确认客户A的反馈窗口。
3. 记录人下周复盘。
```

- [ ] **Step 4: Create generic fixture**

Write `examples/evidence_fixtures/generic/personal_journal_sample.md`:

```markdown
# FICTIONAL PERSONAL JOURNAL SAMPLE

这是虚构个人日记样本，不代表任何真实人物。

2026-06-01 晚上，我路过虚构市虚构区梧桐路 88 号附近，突然意识到自己最近总是在回避明确承诺。

如果需要联系这个虚构角色，可以使用占位邮箱 demo.person@example.invalid，或虚构手机号 138 0013 8000。以上均为测试占位，不可用于真实联系。

我写下这段话，是为了测试 privacy-gate 对地址、邮箱、手机号和个人叙述的检测，不用于心理诊断。
```

- [ ] **Step 5: Verify files exist**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
paths = [
    'examples/evidence_fixtures/README.md',
    'examples/evidence_fixtures/chat/wechat_redacted_sample.txt',
    'examples/evidence_fixtures/work/feishu_meeting_note_sample.md',
    'examples/evidence_fixtures/generic/personal_journal_sample.md',
]
for p in paths:
    path = Path(p)
    assert path.exists(), p
    assert path.read_text(encoding='utf-8').strip(), p
print('fixtures ok')
PY
```

Expected: prints `fixtures ok`.

---

## Task 2: Add validation constant and initial detector tests

**Files:**
- Modify: `scripts/validation_rules.py`
- Modify: `scripts/test_scripts.py`

**Interfaces:**
- Consumes: fixture files from Task 1.
- Produces:
  - `validation_rules.RISK_LEVEL_VALUES: tuple[str, ...]`
  - test expectations for future `privacy-gate.py` functions:
    - `pg.detect_phone_numbers(text: str) -> list[str]`
    - `pg.detect_id_cards(text: str) -> list[str]`
    - `pg.detect_emails(text: str) -> list[str]`
    - `pg.detect_api_tokens(text: str) -> list[str]`
    - `pg.detect_speaker_prefixes(text: str) -> list[str]`
    - `pg.detect_work_titles(text: str) -> list[str]`
    - `pg.detect_long_exact_quotes(text: str) -> list[str]`

- [ ] **Step 1: Add `RISK_LEVEL_VALUES` test**

In `scripts/test_scripts.py`, near imports, add:

```python
pg = importlib.import_module("privacy-gate")
vr = importlib.import_module("validation_rules")
```

Then add this test class near other validation helper tests:

```python
class TestPrivacyGateValidationConstants(unittest.TestCase):
    def test_risk_level_values_are_distinct_from_severity_values(self):
        self.assertEqual(vr.RISK_LEVEL_VALUES, ("none", "low", "medium", "high", "critical"))
        self.assertEqual(vr.SEVERITY_VALUES, ("high", "medium", "low"))
```

- [ ] **Step 2: Add detector tests**

Append this class to `scripts/test_scripts.py`:

```python
class TestPrivacyGateDetectors(unittest.TestCase):
    def test_detect_phone_numbers_supports_china_formats(self):
        text = "手机号 13800138000，也可能写成 +86 139 0013 8000 或 137-0013-8000。"
        self.assertEqual(
            pg.detect_phone_numbers(text),
            ["13800138000", "+86 139 0013 8000", "137-0013-8000"],
        )

    def test_detect_phone_numbers_avoids_plain_86_prefixed_order_id(self):
        text = "订单号 8613800138000 不应直接当作手机号。"
        self.assertEqual(pg.detect_phone_numbers(text), [])

    def test_detect_id_cards_uses_checksum(self):
        text = "有效测试身份证 11010519491231002X，无效长号 110105194912310021。"
        self.assertEqual(pg.detect_id_cards(text), ["11010519491231002X"])

    def test_detect_emails(self):
        self.assertEqual(pg.detect_emails("联系 demo.person@example.invalid"), ["demo.person@example.invalid"])

    def test_detect_api_tokens(self):
        text = "不要泄露 sk-fictional-not-a-real-key-123456 或 ghp_fictionalToken123456。"
        self.assertEqual(
            pg.detect_api_tokens(text),
            ["sk-fictional-not-a-real-key-123456", "ghp_fictionalToken123456"],
        )

    def test_detect_speaker_prefixes(self):
        text = "[我]: 你好\n张三: 收到\nUser: ok\n普通句子没有前缀"
        self.assertEqual(pg.detect_speaker_prefixes(text), ["[我]", "张三", "User"])

    def test_detect_work_titles(self):
        text = "王总和李经理请张工同步给陈老师。客户A 也要看。"
        self.assertEqual(pg.detect_work_titles(text), ["王总", "李经理", "张工", "陈老师", "客户A"])

    def test_detect_long_exact_quotes(self):
        long_line = "这是一段" + "非常长" * 70
        self.assertEqual(pg.detect_long_exact_quotes(long_line), [long_line])
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateValidationConstants scripts.test_scripts.TestPrivacyGateDetectors
```

Expected: FAIL because `privacy-gate.py` and/or `RISK_LEVEL_VALUES` do not exist yet.

- [ ] **Step 4: Add risk level constant**

In `scripts/validation_rules.py`, after `SEVERITY_VALUES`, add:

```python
RISK_LEVEL_VALUES = ("none", "low", "medium", "high", "critical")
```

- [ ] **Step 5: Do not implement detectors yet**

Stop after adding the failing tests and constant. Detector implementation is Task 3.

---

## Task 3: Implement detector functions in `privacy-gate.py`

**Files:**
- Create: `scripts/privacy-gate.py`
- Modify: `scripts/test_scripts.py` only if import ordering needs adjustment

**Interfaces:**
- Consumes:
  - `validation_rules.RISK_LEVEL_VALUES`
- Produces:
  - `detect_phone_numbers(text: str) -> list[str]`
  - `detect_id_cards(text: str) -> list[str]`
  - `detect_emails(text: str) -> list[str]`
  - `detect_api_tokens(text: str) -> list[str]`
  - `detect_speaker_prefixes(text: str) -> list[str]`
  - `detect_work_titles(text: str) -> list[str]`
  - `detect_long_exact_quotes(text: str) -> list[str]`
  - `package_version(root: Path | None = None) -> str`

- [ ] **Step 1: Create `scripts/privacy-gate.py` skeleton**

Write this initial file:

```python
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
WORK_TITLE_RE = re.compile(r"[一-鿿A-Za-z][一-鿿A-Za-z0-9]{0,8}(?:总|经理|工|老师)|客户[A-Za-z0-9一-鿿]{1,8}|供应商[A-Za-z0-9一-鿿]{1,8}|项目[A-Za-z0-9一-鿿]{1,12}")
LONG_QUOTE_THRESHOLD = 120
ID_CARD_CHECK_CODES = "10X98765432"
ID_CARD_WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)


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
```

- [ ] **Step 2: Run detector tests**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateValidationConstants scripts.test_scripts.TestPrivacyGateDetectors
```

Expected: PASS. If a detector test fails, adjust only the detector implementation, not the test intent.

---

## Task 4: Implement scanner core and `privacy_report`

**Files:**
- Modify: `scripts/privacy-gate.py`
- Modify: `scripts/test_scripts.py`

**Interfaces:**
- Consumes detector functions from Task 3.
- Produces:
  - `inspect_text(text: str, *, preset: str, source_hint: str | None = None) -> dict[str, Any]`
  - `inspect_file(path: Path, *, preset: str) -> dict[str, Any]`
  - `scan_text(text: str, *, preset: str) -> dict[str, list[str]]`
  - `build_privacy_report(text: str, *, preset: str, source_path: str | None, sha256: str, size_bytes: int) -> dict[str, Any]`

- [ ] **Step 1: Add failing report tests**

Append to `scripts/test_scripts.py`:

```python
class TestPrivacyGateReports(unittest.TestCase):
    def test_inspect_text_returns_privacy_report_without_raw_text(self):
        text = "[朋友A]: 联系 demo.person@example.invalid，手机号 13800138000。"
        result = pg.inspect_text(text, preset="chat", source_hint="inline_chat")
        report = result["privacy_report"]
        self.assertEqual(report["schema_version"], "0.1.0")
        self.assertEqual(report["input"]["preset"], "chat")
        self.assertEqual(report["input"]["path"], "inline_chat")
        self.assertEqual(report["risk_counts"]["email"], 1)
        self.assertEqual(report["risk_counts"]["phone"], 1)
        self.assertEqual(report["risk_counts"]["speaker_prefix"], 1)
        self.assertNotIn(text, json.dumps(result, ensure_ascii=False))

    def test_inspect_file_hashes_utf8_bytes(self):
        path = Path("examples/evidence_fixtures/generic/personal_journal_sample.md")
        result = pg.inspect_file(path, preset="generic")
        expected = hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        self.assertEqual(result["privacy_report"]["input"]["sha256"], expected)
        self.assertEqual(result["privacy_report"]["input"]["path"], str(path))

    def test_risk_level_is_high_for_token(self):
        result = pg.inspect_text("密钥 sk-fictional-not-a-real-key-123456", preset="work")
        self.assertEqual(result["privacy_report"]["risk_level"], "high")
        self.assertFalse(result["privacy_report"]["allowed_for_public_demo"])

    def test_invalid_preset_raises_value_error(self):
        with self.assertRaises(ValueError):
            pg.inspect_text("hello", preset="unknown")
```

- [ ] **Step 2: Run report tests and verify failure**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateReports
```

Expected: FAIL because `inspect_text` / `inspect_file` are not implemented.

- [ ] **Step 3: Add scanner/report implementation**

Append to `scripts/privacy-gate.py` after detector functions:

```python
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


def _validate_preset(preset: str) -> None:
    if preset not in PRESET_VALUES:
        raise ValueError(f"preset must be one of {PRESET_VALUES}, got: {preset!r}")


def sha256_text(text: str) -> str:
    """Return sha256 for the exact UTF-8 bytes of text, without normalization."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scan_text(text: str, *, preset: str) -> dict[str, list[str]]:
    """Run deterministic privacy detectors for a text blob."""
    _validate_preset(preset)
    findings = {
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
    return findings


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
    report = {
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
        "allowed_for_profile": risk_level not in ("critical",),
        "allowed_for_public_demo": risk_level == "none",
    }
    return report
```

- [ ] **Step 4: Run report tests**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateReports
```

Expected: PASS.

---

## Task 5: Implement `evidence_bundle`

**Files:**
- Modify: `scripts/privacy-gate.py`
- Modify: `scripts/test_scripts.py`

**Interfaces:**
- Consumes:
  - `build_privacy_report(...) -> dict[str, Any]`
  - `sha256_text(text: str) -> str`
- Produces:
  - `build_evidence_bundle(text: str, *, preset: str, source_path: str | None, sha256: str, privacy_report: dict[str, Any]) -> dict[str, Any]`
  - `inspect_text(...)` and `inspect_file(...)` now return both report and bundle

- [ ] **Step 1: Add failing bundle tests**

Append to `scripts/test_scripts.py`:

```python
class TestPrivacyGateEvidenceBundle(unittest.TestCase):
    def test_evidence_bundle_sources_use_id_and_type(self):
        result = pg.inspect_text("[朋友A]: 这是一段聊天。", preset="chat", source_hint="inline_chat")
        bundle = result["evidence_bundle"]
        source = bundle["sources"][0]
        self.assertIn("id", source)
        self.assertIn("type", source)
        self.assertNotIn("source_id", source)
        self.assertNotIn("source_type", source)
        self.assertIn(source["permission"], vr.PERMISSION_VALUES)
        self.assertIn(source["audience"], vr.AUDIENCE_VALUES)
        self.assertIn(source["confidence"], vr.CONFIDENCE_VALUES)

    def test_evidence_bundle_has_evidence_linking_source_ids(self):
        result = pg.inspect_text("sk-fictional-not-a-real-key-123456", preset="work", source_hint="inline_work")
        bundle = result["evidence_bundle"]
        self.assertEqual(bundle["evidence"][0]["source_ids"], [bundle["sources"][0]["id"]])
        self.assertIn(bundle["evidence"][0]["status"], vr.PACKAGE_EVIDENCE_STATUS_VALUES)

    def test_inspect_file_returns_bundle_without_raw_text(self):
        path = Path("examples/evidence_fixtures/chat/wechat_redacted_sample.txt")
        text = path.read_text(encoding="utf-8")
        result = pg.inspect_file(path, preset="chat")
        self.assertNotIn(text, json.dumps(result, ensure_ascii=False))
        self.assertEqual(result["evidence_bundle"]["sources"][0]["path"], str(path))
```

- [ ] **Step 2: Run bundle tests and verify failure**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateEvidenceBundle
```

Expected: FAIL because `evidence_bundle` is not implemented yet.

- [ ] **Step 3: Add bundle implementation and complete inspect APIs**

Append to `scripts/privacy-gate.py`:

```python
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
```

- [ ] **Step 4: Run report and bundle tests**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateReports scripts.test_scripts.TestPrivacyGateEvidenceBundle
```

Expected: PASS.

---

## Task 6: Implement CLI and output writing

**Files:**
- Modify: `scripts/privacy-gate.py`
- Modify: `scripts/test_scripts.py`

**Interfaces:**
- Consumes:
  - `inspect_file(path: Path, *, preset: str) -> dict[str, Any]`
- Produces CLI:
  - `python3 scripts/privacy-gate.py --version`
  - `python3 scripts/privacy-gate.py inspect <path> --preset generic|chat|work --json`
  - `python3 scripts/privacy-gate.py inspect <path> --preset ... --output-dir <dir>`
  - `--fail-on none|low|medium|high|critical`

- [ ] **Step 1: Add CLI tests**

Append to `scripts/test_scripts.py`:

```python
class TestPrivacyGateCli(unittest.TestCase):
    def test_privacy_gate_version(self):
        result = subprocess.run(
            [sys.executable, "scripts/privacy-gate.py", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn(vs.package_version(), result.stdout)

    def test_privacy_gate_inspect_json(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/privacy-gate.py",
                "inspect",
                "examples/evidence_fixtures/chat/wechat_redacted_sample.txt",
                "--preset",
                "chat",
                "--json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn("privacy_report", payload)
        self.assertIn("evidence_bundle", payload)

    def test_privacy_gate_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [
                    sys.executable,
                    "scripts/privacy-gate.py",
                    "inspect",
                    "examples/evidence_fixtures/work/feishu_meeting_note_sample.md",
                    "--preset",
                    "work",
                    "--output-dir",
                    tmp,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue((Path(tmp) / "privacy_report.json").exists())
            self.assertTrue((Path(tmp) / "evidence_bundle.json").exists())

    def test_privacy_gate_fail_on_high(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/privacy-gate.py",
                "inspect",
                "examples/evidence_fixtures/work/feishu_meeting_note_sample.md",
                "--preset",
                "work",
                "--json",
                "--fail-on",
                "high",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("privacy_report", result.stdout)

    def test_privacy_gate_missing_file_fails(self):
        result = subprocess.run(
            [sys.executable, "scripts/privacy-gate.py", "inspect", "missing.txt", "--preset", "generic", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Input file not found", result.stderr)
```

- [ ] **Step 2: Run CLI tests and verify failure**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateCli
```

Expected: FAIL because CLI parser is not implemented yet.

- [ ] **Step 3: Add CLI implementation**

Append to `scripts/privacy-gate.py`:

```python
RISK_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


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
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
python3 -m unittest scripts.test_scripts.TestPrivacyGateCli
```

Expected: PASS.

---

## Task 7: Add docs and hard-gate guidance

**Files:**
- Create: `docs/local_evidence_intake.md`
- Modify: `README.md`
- Modify: `SKILL.md`

**Interfaces:**
- Consumes:
  - CLI commands from Task 6
  - fixture paths from Task 1
- Produces:
  - documentation for users/developers
  - minimal README link
  - SKILL.md hard-gate rule

- [ ] **Step 1: Create docs page**

Write `docs/local_evidence_intake.md`:

```markdown
# Local Evidence Intake

Local Evidence Intake 是 `digital-life` 的本地隐私预检入口。它在 LLM 分析、profile 写入或 skill package 生成之前，用确定性规则扫描用户主动提供的文本材料。

## 目标

```text
本地材料 → privacy-gate → privacy_report + evidence_bundle → 后续 profile/package 流程
```

它解决的是第一层问题：材料里是否有明显隐私风险，以及后续流程应该用什么权限和引用策略处理。

## 非目标

v0 不做：

- 不登录微信、飞书、小红书、知乎、豆瓣或 B 站。
- 不破解微信数据库。
- 不调用 LLM。
- 不自动脱敏或改写原文。
- 不替代法律、安全或心理风险审查。

## CLI

```bash
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/chat/wechat_redacted_sample.txt --preset chat --json
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/work/feishu_meeting_note_sample.md --preset work --output-dir /tmp/digital-life-evidence
```

Preset：

- `generic`：普通 Markdown / TXT / JSONL。
- `chat`：聊天式文本，额外检测发言人前缀和第三方称谓。
- `work`：会议纪要、工作群、文档评论，额外检测职场称谓和项目线索。

## Python API

```python
import importlib
pg = importlib.import_module("privacy-gate")

result = pg.inspect_text("[朋友A]: 这是一段虚构聊天", preset="chat", source_hint="inline_chat")
```

后续 browser / WebFetch 获取到的文本，在进入 LLM 分析或写入 profile 前，应先调用 `inspect_text()`。

## 输出

`privacy_report` 描述风险、建议权限和准入判断。

`evidence_bundle` 描述可被后续流程引用的证据摘要。它不保存原文，只保存路径、哈希、风险计数、权限、audience、confidence 和摘要。

## 风险规则

v0 覆盖：

- 大陆手机号。
- 18 位身份证号校验码。
- 邮箱。
- token / API key 常见前缀。
- 聊天发言人前缀。
- 职场称谓。
- 地址线索。
- 长段 exact quote。

v0 是 Level 1 静态预检。没有被检测到不代表材料完全安全。
```

- [ ] **Step 2: Add README link**

In `README.md`, after line 102 in the “数据获取” section, add:

```markdown

如果你要使用聊天记录、会议纪要、工作群文本或其他高敏材料，建议先通过本地隐私预检入口扫描：[`Local Evidence Intake`](docs/local_evidence_intake.md)。它只做本地静态检查，不登录平台、不调用 LLM，也不保存原文。
```

- [ ] **Step 3: Add SKILL.md hard-gate rule**

In `SKILL.md`, after the existing safety boundary list item 8, add item 9:

```markdown
9. **隐私硬门槛**：聊天记录、会议纪要、工作群文本、browser / WebFetch 获取的页面文本等高敏材料，在分析、总结或写入 profile 前，应先经过本地 privacy gate；未通过或风险过高时，不得引用原文、不得写入公开 demo、不得继续扩散
```

Then in Step 2 data collection, after the three bullet points, add:

```markdown
高敏材料进入分析前，优先使用 `python3 scripts/privacy-gate.py inspect <path> --preset generic|chat|work --json` 做本地预检；browser / WebFetch 获取到的文本应先经过等价的 `inspect_text()` 检查。
```

- [ ] **Step 4: Verify docs mention key commands**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path('docs/local_evidence_intake.md').read_text(encoding='utf-8')
assert 'python3 scripts/privacy-gate.py inspect' in text
assert 'inspect_text()' in text
readme = Path('README.md').read_text(encoding='utf-8')
assert 'docs/local_evidence_intake.md' in readme
skill = Path('SKILL.md').read_text(encoding='utf-8')
assert '隐私硬门槛' in skill
print('docs ok')
PY
```

Expected: prints `docs ok`.

---

## Task 8: Full verification and cleanup

**Files:**
- Potentially modify: `scripts/privacy-gate.py`, `scripts/test_scripts.py`, docs if verification finds issues.

**Interfaces:**
- Consumes all previous tasks.
- Produces verified working feature.

- [ ] **Step 1: Run focused privacy gate tests**

Run:

```bash
python3 -m unittest \
  scripts.test_scripts.TestPrivacyGateValidationConstants \
  scripts.test_scripts.TestPrivacyGateDetectors \
  scripts.test_scripts.TestPrivacyGateReports \
  scripts.test_scripts.TestPrivacyGateEvidenceBundle \
  scripts.test_scripts.TestPrivacyGateCli
```

Expected: all tests PASS.

- [ ] **Step 2: Run existing full unit suite**

Run:

```bash
python3 -m unittest discover -s scripts -p 'test_scripts.py'
```

Expected: all tests PASS.

- [ ] **Step 3: Run script compile check**

Run:

```bash
python3 -m py_compile scripts/*.py
```

Expected: no output and exit code 0.

- [ ] **Step 4: Run repository validation**

Run:

```bash
python3 scripts/validate-skill.py
```

Expected: validation passes. If it fails because `REQUIRED_ROOT_FILES` now needs `scripts/privacy-gate.py`, decide whether to add that script to `REQUIRED_ROOT_FILES`. Only add it if the validation style requires all shipped root scripts to be pinned.

- [ ] **Step 5: Run package validation/tests**

Run:

```bash
python3 scripts/package-manager.py validate examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py validate examples/skill_packages/decision_principles_demo
python3 scripts/package-manager.py test examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py test examples/skill_packages/decision_principles_demo
```

Expected: all commands PASS.

- [ ] **Step 6: Run profile doctor**

Run:

```bash
python3 scripts/profile-manager.py doctor
```

Expected: PASS.

- [ ] **Step 7: Run privacy gate smoke tests**

Run:

```bash
python3 scripts/privacy-gate.py --version
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/chat/wechat_redacted_sample.txt --preset chat --json
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/work/feishu_meeting_note_sample.md --preset work --json --fail-on critical
python3 scripts/privacy-gate.py inspect examples/evidence_fixtures/generic/personal_journal_sample.md --preset generic --output-dir /tmp/digital-life-evidence
```

Expected:

- `--version` prints current repo version.
- inspect commands print valid JSON or write `/tmp/digital-life-evidence/privacy_report.json` and `/tmp/digital-life-evidence/evidence_bundle.json`.
- no command prints raw fixture text as a field value.

- [ ] **Step 8: Inspect git diff**

Run:

```bash
git diff -- README.md SKILL.md docs/local_evidence_intake.md examples/evidence_fixtures scripts/privacy-gate.py scripts/test_scripts.py scripts/validation_rules.py
```

Expected: diff only contains Local Evidence Intake v0 changes.

---

## Self-Review Notes

- Spec coverage: covered CLI, Python API, presets, privacy report, evidence bundle, hard gate guidance, dynamic intake bypass mitigation, China-specific rules, fixtures, tests, docs, and verification.
- Placeholder scan: no TBD/TODO/fill-in placeholders are present. Fixture “占位” is intentional fictional sample content.
- Type consistency: `inspect_text`, `inspect_file`, `build_privacy_report`, `build_evidence_bundle`, `sources[].id/type`, and validation enum names are consistent across tasks.
- Developer constraint: plan omits commit steps because commits require explicit user request in this environment.
