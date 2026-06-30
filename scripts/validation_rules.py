"""Shared validation helpers for digital-life scripts."""
from __future__ import annotations

from pathlib import Path, PureWindowsPath
from typing import Any
import hashlib
import re

CONFIDENCE_VALUES = ("high", "medium", "low")
SEVERITY_VALUES = ("high", "medium", "low")
RISK_LEVEL_VALUES = ("none", "low", "medium", "high", "critical")
PERMISSION_VALUES = (
    "private_only",
    "user_review_required",
    "desensitized_shareable",
    "public_source",
    "do_not_quote",
)
AUDIENCE_VALUES = ("owner_only", "trusted_private", "desensitized_public", "public")
MARKDOWN_VISIBILITY_VALUES = ("private", "shareable_after_review", "public")
PUBLIC_MARKDOWN_FORBIDDEN_PERMISSIONS = ("private_only", "user_review_required", "do_not_quote")
PACKAGE_VISIBILITY_VALUES = ("private", "shareable_after_review", "public")
PACKAGE_EXPORT_FORMATS = ("system_prompt", "markdown", "json")
PACKAGE_EVIDENCE_STATUS_VALUES = ("human_confirmed", "demo_author_confirmed", "needs_review")
PACKAGE_ID_RE = re.compile(r"^[a-z0-9_-]+$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

PERSONA_LAYERS = (
    "layer0_rules",
    "layer1_identity",
    "layer2_expression",
    "layer3_decision_model",
    "layer4_boundaries",
)


def _type_name(value: Any) -> str:
    return type(value).__name__


def validate_non_empty_string(value: Any, path: str, errors: list[str], *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        errors.append(f"{path} must be a string")
        return
    if not allow_empty and not value.strip():
        errors.append(f"{path} must be a non-empty string")


def validate_enum(value: Any, allowed: tuple[str, ...], path: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{path} must be one of {allowed}, got: {value!r}")


def validate_list_of_strings(value: Any, path: str, errors: list[str], *, allow_empty_items: bool = False) -> None:
    if not isinstance(value, list):
        errors.append(f"{path} must be a list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str):
            errors.append(f"{path}[{index}] must be a string")
        elif not allow_empty_items and not item.strip():
            errors.append(f"{path}[{index}] must be a non-empty string")


def _validate_relative_package_path(value: Any, path: str, errors: list[str]) -> None:
    validate_non_empty_string(value, path, errors)
    if not isinstance(value, str):
        return
    candidate = Path(value)
    windows_candidate = PureWindowsPath(value)
    if (
        candidate.is_absolute()
        or windows_candidate.is_absolute()
        or windows_candidate.drive
        or ".." in candidate.parts
        or ".." in windows_candidate.parts
        or "\\" in value
    ):
        errors.append(f"{path} must be a relative package path without '..', drive letters, or backslashes")


def _validate_allowed_keys(obj: Any, allowed: set[str], path: str, errors: list[str]) -> None:
    if not isinstance(obj, dict):
        return
    extra = sorted(set(obj) - allowed)
    if extra:
        errors.append(f"{path} contains unknown keys: {', '.join(extra)}")


def _resolve_package_path(package_dir: Path, value: str, path: str, errors: list[str]) -> Path | None:
    """Resolve a package-relative path and ensure it stays inside package_dir."""
    try:
        package_root = package_dir.resolve()
        resolved = (package_dir / value).resolve()
        resolved.relative_to(package_root)
    except (OSError, ValueError):
        errors.append(f"{path} must resolve inside the package directory")
        return None
    return resolved


def _validate_id(value: Any, path: str, errors: list[str]) -> None:
    validate_non_empty_string(value, path, errors)
    if isinstance(value, str) and not PACKAGE_ID_RE.match(value):
        errors.append(f"{path} must match {PACKAGE_ID_RE.pattern}, got: {value!r}")


def _validate_semver(value: Any, path: str, errors: list[str]) -> None:
    validate_non_empty_string(value, path, errors)
    if isinstance(value, str) and not SEMVER_RE.match(value):
        errors.append(f"{path} must be semver x.y.z, got: {value!r}")


def _validate_sha256(value: Any, path: str, errors: list[str]) -> None:
    validate_non_empty_string(value, path, errors)
    if isinstance(value, str) and not SHA256_RE.match(value):
        errors.append(f"{path} must be a lowercase sha256 hex digest")


def validate_required_object_fields(
    obj: Any,
    spec: dict[str, type | tuple[type, ...]],
    path: str,
    errors: list[str],
) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{path} must be an object")
        return
    for field, expected_type in spec.items():
        field_path = f"{path}.{field}"
        if field not in obj:
            errors.append(f"{field_path} is required")
            continue
        if not isinstance(obj[field], expected_type):
            if isinstance(expected_type, tuple):
                expected = " or ".join(t.__name__ for t in expected_type)
            else:
                expected = expected_type.__name__
            errors.append(f"{field_path} must be a {expected}")


def validate_source_summary(
    payload: dict[str, Any],
    context: str,
    errors: list[str],
    *,
    template_mode: bool = False,
) -> None:
    ss = payload.get("source_summary")
    if not isinstance(ss, dict):
        errors.append(f"{context} source_summary must be an object")
        return

    for field in ("input_modes", "evidence_count", "notes"):
        if field not in ss:
            errors.append(f"{context} source_summary missing {field}")

    if "input_modes" in ss:
        validate_list_of_strings(ss["input_modes"], f"{context} source_summary.input_modes", errors)

    if "evidence_count" in ss:
        if not isinstance(ss["evidence_count"], int):
            errors.append(f"{context} source_summary.evidence_count must be an int")
        elif ss["evidence_count"] < 0:
            errors.append(f"{context} source_summary.evidence_count must be non-negative")

    if "notes" in ss:
        validate_non_empty_string(
            ss["notes"],
            f"{context} source_summary.notes",
            errors,
            allow_empty=template_mode,
        )


def validate_persona(
    persona: Any,
    context: str,
    errors: list[str],
    *,
    strict_nested: bool = False,
) -> None:
    if not isinstance(persona, dict):
        errors.append(f"{context} persona must be an object")
        return

    for layer in PERSONA_LAYERS:
        if layer not in persona:
            errors.append(f"{context} persona missing layer: {layer}")

    if not strict_nested:
        return

    if "layer0_rules" in persona:
        validate_list_of_strings(persona["layer0_rules"], f"{context} persona.layer0_rules", errors)

    layer1 = persona.get("layer1_identity")
    if isinstance(layer1, dict):
        validate_non_empty_string(layer1.get("self_description", ""), f"{context} persona.layer1_identity.self_description", errors, allow_empty=True)
        for field in ("roles", "stable_facts"):
            validate_list_of_strings(layer1.get(field), f"{context} persona.layer1_identity.{field}", errors)
        current_state = layer1.get("current_state")
        if not isinstance(current_state, dict):
            errors.append(f"{context} persona.layer1_identity.current_state must be an object")
        else:
            for field in ("summary", "last_verified_at", "freshness"):
                validate_non_empty_string(current_state.get(field, ""), f"{context} persona.layer1_identity.current_state.{field}", errors, allow_empty=True)
    elif "layer1_identity" in persona:
        errors.append(f"{context} persona.layer1_identity must be an object")

    layer2 = persona.get("layer2_expression")
    if isinstance(layer2, dict):
        for field in ("tone", "signature_phrases", "drafting_rules", "not_like_me"):
            validate_list_of_strings(layer2.get(field), f"{context} persona.layer2_expression.{field}", errors)
    elif "layer2_expression" in persona:
        errors.append(f"{context} persona.layer2_expression must be an object")

    layer3 = persona.get("layer3_decision_model")
    if isinstance(layer3, dict):
        for field in ("default_sequence", "priority_order", "people_to_consult", "decision_blind_spots"):
            validate_list_of_strings(layer3.get(field), f"{context} persona.layer3_decision_model.{field}", errors)
        validate_non_empty_string(layer3.get("risk_posture", ""), f"{context} persona.layer3_decision_model.risk_posture", errors, allow_empty=True)
    elif "layer3_decision_model" in persona:
        errors.append(f"{context} persona.layer3_decision_model must be an object")

    layer4 = persona.get("layer4_boundaries")
    if isinstance(layer4, dict):
        for field in ("owner_only", "shareable", "requires_confirmation", "never_answer"):
            validate_list_of_strings(layer4.get(field), f"{context} persona.layer4_boundaries.{field}", errors)
    elif "layer4_boundaries" in persona:
        errors.append(f"{context} persona.layer4_boundaries must be an object")


def validate_publication_policy(payload: dict[str, Any], context: str, errors: list[str], *, template_mode: bool = False) -> str | None:
    policy = payload.get("publication_policy")
    if not isinstance(policy, dict):
        errors.append(f"{context} publication_policy must be an object")
        return None

    required_fields = ("allowed_audience", "markdown_visibility", "exact_quote_policy")
    for field in required_fields:
        if field not in policy:
            errors.append(f"{context} publication_policy.{field} is required")

    if "allowed_audience" in policy:
        validate_enum(policy["allowed_audience"], AUDIENCE_VALUES, f"{context} publication_policy.allowed_audience", errors)
    if "markdown_visibility" in policy:
        validate_enum(policy["markdown_visibility"], MARKDOWN_VISIBILITY_VALUES, f"{context} publication_policy.markdown_visibility", errors)
    if "exact_quote_policy" in policy:
        validate_non_empty_string(
            policy["exact_quote_policy"],
            f"{context} publication_policy.exact_quote_policy",
            errors,
            allow_empty=template_mode,
        )

    allowed_audience = policy.get("allowed_audience")
    markdown_visibility = policy.get("markdown_visibility")
    if markdown_visibility == "public" and allowed_audience in ("owner_only", "trusted_private"):
        errors.append(
            f"{context} publication_policy.markdown_visibility cannot be public "
            f"when allowed_audience is {allowed_audience}"
        )
    return markdown_visibility if isinstance(markdown_visibility, str) else None


def _validate_string_list_section(payload: dict[str, Any], field: str, context: str, errors: list[str]) -> None:
    if field in payload:
        validate_list_of_strings(payload[field], f"{context} {field}", errors)


def validate_skill_package(
    payload: dict[str, Any],
    context: str,
    errors: list[str],
    *,
    package_dir: Path | None = None,
) -> None:
    """Validate a portable distilled_life skill package manifest."""
    if not isinstance(payload, dict):
        errors.append(f"{context} must be an object")
        return

    _validate_allowed_keys(payload, {"schema_version", "package", "scope", "persona", "skills", "sources", "evidence", "exports", "tests"}, context, errors)

    for field in ("schema_version", "package", "scope", "persona", "skills", "sources", "evidence", "exports", "tests"):
        if field not in payload:
            errors.append(f"{context}.{field} is required")

    _validate_semver(payload.get("schema_version", ""), f"{context}.schema_version", errors)

    package = payload.get("package")
    package_visibility = None
    if not isinstance(package, dict):
        errors.append(f"{context}.package must be an object")
    else:
        _validate_allowed_keys(package, {"id", "name", "description", "version", "license", "visibility", "language"}, f"{context}.package", errors)
        _validate_id(package.get("id", ""), f"{context}.package.id", errors)
        for field in ("name", "description", "license", "language"):
            validate_non_empty_string(package.get(field, ""), f"{context}.package.{field}", errors)
        _validate_semver(package.get("version", ""), f"{context}.package.version", errors)
        package_visibility = package.get("visibility")
        validate_enum(package_visibility, PACKAGE_VISIBILITY_VALUES, f"{context}.package.visibility", errors)

    scope = payload.get("scope")
    if not isinstance(scope, dict):
        errors.append(f"{context}.scope must be an object")
    else:
        _validate_allowed_keys(scope, {"domain", "use_cases", "limitations"}, f"{context}.scope", errors)
        validate_non_empty_string(scope.get("domain", ""), f"{context}.scope.domain", errors)
        for field in ("use_cases", "limitations"):
            validate_list_of_strings(scope.get(field), f"{context}.scope.{field}", errors)

    persona = payload.get("persona")
    if not isinstance(persona, dict):
        errors.append(f"{context}.persona must be an object")
    else:
        _validate_allowed_keys(persona, {"role", "tone", "preferences", "boundaries"}, f"{context}.persona", errors)
        validate_non_empty_string(persona.get("role", ""), f"{context}.persona.role", errors)
        for field in ("tone", "preferences", "boundaries"):
            validate_list_of_strings(persona.get(field), f"{context}.persona.{field}", errors)

    skill_ids: set[str] = set()
    skills = payload.get("skills")
    if not isinstance(skills, list) or not skills:
        errors.append(f"{context}.skills must be a non-empty list")
    else:
        for index, item in enumerate(skills):
            item_path = f"{context}.skills[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            _validate_allowed_keys(item, {"id", "name", "use_when", "method", "counterexamples", "eval_prompts"}, item_path, errors)
            skill_id = item.get("id")
            _validate_id(skill_id, f"{item_path}.id", errors)
            if isinstance(skill_id, str):
                if skill_id in skill_ids:
                    errors.append(f"{item_path}.id duplicates skill id: {skill_id}")
                skill_ids.add(skill_id)
            validate_non_empty_string(item.get("name", ""), f"{item_path}.name", errors)
            for field in ("use_when", "method", "counterexamples", "eval_prompts"):
                validate_list_of_strings(item.get(field), f"{item_path}.{field}", errors)

    source_ids: set[str] = set()
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"{context}.sources must be a non-empty list")
    else:
        for index, item in enumerate(sources):
            item_path = f"{context}.sources[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            _validate_allowed_keys(item, {"id", "type", "path", "sha256", "permission", "audience"}, item_path, errors)
            source_id = item.get("id")
            _validate_id(source_id, f"{item_path}.id", errors)
            if isinstance(source_id, str):
                if source_id in source_ids:
                    errors.append(f"{item_path}.id duplicates source id: {source_id}")
                source_ids.add(source_id)
            validate_non_empty_string(item.get("type", ""), f"{item_path}.type", errors)
            _validate_relative_package_path(item.get("path", ""), f"{item_path}.path", errors)
            _validate_sha256(item.get("sha256", ""), f"{item_path}.sha256", errors)
            validate_enum(item.get("permission"), PERMISSION_VALUES, f"{item_path}.permission", errors)
            validate_enum(item.get("audience"), AUDIENCE_VALUES, f"{item_path}.audience", errors)
            if package_visibility == "public" and item.get("permission") in PUBLIC_MARKDOWN_FORBIDDEN_PERMISSIONS:
                errors.append(f"{item_path}.permission cannot be {item.get('permission')!r} when package.visibility is public")
            if package_dir is not None and isinstance(item.get("path"), str) and isinstance(item.get("sha256"), str):
                source_path = _resolve_package_path(package_dir, item["path"], f"{item_path}.path", errors)
                if source_path is None:
                    continue
                if not source_path.exists():
                    errors.append(f"{item_path}.path does not exist: {item['path']}")
                elif source_path.is_file():
                    actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
                    if actual_hash != item["sha256"]:
                        errors.append(f"{item_path}.sha256 mismatch for {item['path']}: expected {item['sha256']}, got {actual_hash}")

    evidence_ids: set[str] = set()
    evidence = payload.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{context}.evidence must be a non-empty list")
    else:
        for index, item in enumerate(evidence):
            item_path = f"{context}.evidence[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            _validate_allowed_keys(item, {"id", "claim", "source_ids", "confidence", "status", "permission"}, item_path, errors)
            evidence_id = item.get("id")
            _validate_id(evidence_id, f"{item_path}.id", errors)
            if isinstance(evidence_id, str):
                if evidence_id in evidence_ids:
                    errors.append(f"{item_path}.id duplicates evidence id: {evidence_id}")
                evidence_ids.add(evidence_id)
            validate_non_empty_string(item.get("claim", ""), f"{item_path}.claim", errors)
            validate_list_of_strings(item.get("source_ids"), f"{item_path}.source_ids", errors)
            if isinstance(item.get("source_ids"), list):
                for source_id in item["source_ids"]:
                    if isinstance(source_id, str) and source_id not in source_ids:
                        errors.append(f"{item_path}.source_ids references unknown source id: {source_id}")
            validate_enum(item.get("confidence"), CONFIDENCE_VALUES, f"{item_path}.confidence", errors)
            validate_enum(item.get("status"), PACKAGE_EVIDENCE_STATUS_VALUES, f"{item_path}.status", errors)
            validate_enum(item.get("permission"), PERMISSION_VALUES, f"{item_path}.permission", errors)
            if package_visibility == "public" and item.get("permission") in PUBLIC_MARKDOWN_FORBIDDEN_PERMISSIONS:
                errors.append(f"{item_path}.permission cannot be {item.get('permission')!r} when package.visibility is public")

    exports = payload.get("exports")
    if not isinstance(exports, list) or not exports:
        errors.append(f"{context}.exports must be a non-empty list")
    else:
        seen_formats: set[str] = set()
        for index, item in enumerate(exports):
            item_path = f"{context}.exports[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            _validate_allowed_keys(item, {"format", "path"}, item_path, errors)
            export_format = item.get("format")
            validate_enum(export_format, PACKAGE_EXPORT_FORMATS, f"{item_path}.format", errors)
            if isinstance(export_format, str):
                seen_formats.add(export_format)
            _validate_relative_package_path(item.get("path", ""), f"{item_path}.path", errors)
            if package_dir is not None and isinstance(item.get("path"), str):
                export_path = _resolve_package_path(package_dir, item["path"], f"{item_path}.path", errors)
                if export_path is None:
                    continue
                if not export_path.exists():
                    errors.append(f"{item_path}.path does not exist: {item['path']}")
        if "system_prompt" not in seen_formats:
            errors.append(f"{context}.exports must include a system_prompt export")

    tests = payload.get("tests")
    if not isinstance(tests, dict):
        errors.append(f"{context}.tests must be an object")
    else:
        _validate_allowed_keys(tests, {"path", "positive", "negative"}, f"{context}.tests", errors)
        _validate_relative_package_path(tests.get("path", ""), f"{context}.tests.path", errors)
        for field in ("positive", "negative"):
            validate_list_of_strings(tests.get(field), f"{context}.tests.{field}", errors)
        if package_dir is not None and isinstance(tests.get("path"), str):
            tests_path = _resolve_package_path(package_dir, tests["path"], f"{context}.tests.path", errors)
            if tests_path is None:
                return
            if not tests_path.exists():
                errors.append(f"{context}.tests.path does not exist: {tests['path']}")


def validate_skill_package_tests(payload: dict[str, Any], manifest: dict[str, Any], context: str, errors: list[str]) -> None:
    """Validate static tests for a distilled_life skill package."""
    if not isinstance(payload, dict):
        errors.append(f"{context} must be an object")
        return

    manifest_tests = manifest.get("tests") if isinstance(manifest.get("tests"), dict) else {}
    expected_positive = set(manifest_tests.get("positive", [])) if isinstance(manifest_tests.get("positive"), list) else set()
    expected_negative = set(manifest_tests.get("negative", [])) if isinstance(manifest_tests.get("negative"), list) else set()

    for section, expected_ids in (("positive", expected_positive), ("negative", expected_negative)):
        cases = payload.get(section)
        if not isinstance(cases, list) or not cases:
            errors.append(f"{context}.{section} must be a non-empty list")
            continue
        seen_ids: set[str] = set()
        for index, item in enumerate(cases):
            item_path = f"{context}.{section}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            if section == "positive":
                _validate_allowed_keys(item, {"id", "input", "expected_traits", "forbidden_traits"}, item_path, errors)
            else:
                _validate_allowed_keys(item, {"id", "input", "expected_behavior", "forbidden_behavior"}, item_path, errors)
            case_id = item.get("id")
            _validate_id(case_id, f"{item_path}.id", errors)
            if isinstance(case_id, str):
                if case_id in seen_ids:
                    errors.append(f"{item_path}.id duplicates test id: {case_id}")
                seen_ids.add(case_id)
            validate_non_empty_string(item.get("input", ""), f"{item_path}.input", errors)
            if section == "positive":
                validate_list_of_strings(item.get("expected_traits"), f"{item_path}.expected_traits", errors)
                validate_list_of_strings(item.get("forbidden_traits"), f"{item_path}.forbidden_traits", errors)
            else:
                validate_non_empty_string(item.get("expected_behavior", ""), f"{item_path}.expected_behavior", errors)
                validate_non_empty_string(item.get("forbidden_behavior", ""), f"{item_path}.forbidden_behavior", errors)
        missing = sorted(expected_ids - seen_ids)
        if missing:
            errors.append(f"{context}.{section} missing manifest test ids: {', '.join(missing)}")
        extra = sorted(seen_ids - expected_ids)
        if extra:
            errors.append(f"{context}.{section} contains test ids not listed in manifest: {', '.join(extra)}")


def validate_distilled_life(
    payload: dict[str, Any],
    context: str,
    errors: list[str],
    *,
    template_mode: bool = False,
) -> None:
    """Validate distilled_life nested structures used by templates, examples, and profiles."""
    validate_source_summary(payload, context, errors, template_mode=template_mode)

    markdown_visibility = validate_publication_policy(payload, context, errors, template_mode=template_mode)
    publication_policy = payload.get("publication_policy") if isinstance(payload.get("publication_policy"), dict) else {}
    exact_quote_policy = publication_policy.get("exact_quote_policy", "")
    public_quote_policy_is_safe = isinstance(exact_quote_policy, str) and any(
        marker in exact_quote_policy for marker in ("demo_only", "public_source_only")
    )

    decision_model = payload.get("decision_model")
    if not isinstance(decision_model, dict):
        errors.append(f"{context} decision_model must be an object")
    else:
        for field in ("core_pattern", "uncertainty_behavior", "smallest_next_action"):
            validate_non_empty_string(decision_model.get(field, ""), f"{context} decision_model.{field}", errors, allow_empty=True)
        for field in ("decision_sequence", "tradeoff_style"):
            validate_list_of_strings(decision_model.get(field), f"{context} decision_model.{field}", errors)

    expression_model = payload.get("expression_model")
    if not isinstance(expression_model, dict):
        errors.append(f"{context} expression_model must be an object")
    else:
        validate_non_empty_string(expression_model.get("summary", ""), f"{context} expression_model.summary", errors, allow_empty=True)
        for field in ("preferred_formats", "draft_only_rules"):
            validate_list_of_strings(expression_model.get(field), f"{context} expression_model.{field}", errors)
        variants = expression_model.get("audience_variants")
        if not isinstance(variants, list):
            errors.append(f"{context} expression_model.audience_variants must be a list")
        else:
            for index, item in enumerate(variants):
                item_path = f"{context} expression_model.audience_variants[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{item_path} must be an object")
                    continue
                for field in ("audience", "style"):
                    if field not in item:
                        errors.append(f"{item_path}.{field} is required")
                    else:
                        validate_non_empty_string(item[field], f"{item_path}.{field}", errors)

    stories = payload.get("life_stories")
    if not isinstance(stories, list):
        errors.append(f"{context} life_stories must be a list")
    else:
        for index, item in enumerate(stories):
            item_path = f"{context} life_stories[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            for field in ("id", "title", "context", "stakes", "lesson", "permission", "outcome"):
                if field not in item:
                    errors.append(f"{item_path}.{field} is required")
                else:
                    validate_non_empty_string(item[field], f"{item_path}.{field}", errors, allow_empty=template_mode)
                    if field == "permission" and isinstance(item[field], str):
                        if item[field]:
                            validate_enum(item[field], PERMISSION_VALUES, f"{item_path}.permission", errors)
                            if markdown_visibility == "public" and item[field] in PUBLIC_MARKDOWN_FORBIDDEN_PERMISSIONS:
                                errors.append(f"{item_path}.permission cannot be {item[field]!r} when publication_policy.markdown_visibility is public")
                        elif not template_mode:
                            errors.append(f"{item_path}.permission must be a non-empty string")
            for field in ("actions", "options", "reasoning", "quotes"):
                if field not in item:
                    errors.append(f"{item_path}.{field} is required")
                else:
                    validate_list_of_strings(item[field], f"{item_path}.{field}", errors)
            quotes = item.get("quotes")
            has_exact_quotes = isinstance(quotes, list) and any(isinstance(quote, str) and quote.strip() for quote in quotes)
            if (
                markdown_visibility == "public"
                and has_exact_quotes
                and item.get("permission") != "public_source"
                and not public_quote_policy_is_safe
            ):
                errors.append(
                    f"{item_path}.quotes cannot be non-empty when publication_policy.markdown_visibility is public "
                    "unless permission is 'public_source' or exact_quote_policy explicitly allows demo/public-source quotes"
                )

    assets = payload.get("skill_assets")
    if not isinstance(assets, list):
        errors.append(f"{context} skill_assets must be a list")
    else:
        for index, item in enumerate(assets):
            item_path = f"{context} skill_assets[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            for field in ("id", "name"):
                if field not in item:
                    errors.append(f"{item_path}.{field} is required")
                else:
                    validate_non_empty_string(item[field], f"{item_path}.{field}", errors, allow_empty=True)
            for field in ("use_when", "method", "counterexamples", "eval_prompts"):
                if field not in item:
                    errors.append(f"{item_path}.{field} is required")
                else:
                    validate_list_of_strings(item[field], f"{item_path}.{field}", errors)

    boundary_rules = payload.get("boundary_rules")
    if not isinstance(boundary_rules, list):
        errors.append(f"{context} boundary_rules must be a list")
    else:
        for index, item in enumerate(boundary_rules):
            item_path = f"{context} boundary_rules[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            if "rule" not in item:
                errors.append(f"{item_path}.rule is required")
            else:
                validate_non_empty_string(item["rule"], f"{item_path}.rule", errors, allow_empty=True)
            if "severity" not in item:
                errors.append(f"{item_path}.severity is required")
            else:
                validate_enum(item["severity"], SEVERITY_VALUES, f"{item_path}.severity", errors)

    evidence = payload.get("evidence_trace")
    if not isinstance(evidence, list):
        errors.append(f"{context} evidence_trace must be a list")
    else:
        for index, item in enumerate(evidence):
            item_path = f"{context} evidence_trace[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            for field in ("claim", "source_type", "source_id", "permission"):
                if field not in item:
                    errors.append(f"{item_path}.{field} is required")
                else:
                    validate_non_empty_string(item[field], f"{item_path}.{field}", errors, allow_empty=template_mode)
                    if field == "permission" and isinstance(item[field], str):
                        if item[field]:
                            validate_enum(item[field], PERMISSION_VALUES, f"{item_path}.permission", errors)
                            if markdown_visibility == "public" and item[field] in PUBLIC_MARKDOWN_FORBIDDEN_PERMISSIONS:
                                errors.append(f"{item_path}.permission cannot be {item[field]!r} when publication_policy.markdown_visibility is public")
                        elif not template_mode:
                            errors.append(f"{item_path}.permission must be a non-empty string")
            if "confidence" not in item:
                errors.append(f"{item_path}.confidence is required")
            else:
                validate_enum(item["confidence"], CONFIDENCE_VALUES, f"{item_path}.confidence", errors)

    eval_cases = payload.get("eval_cases")
    if not isinstance(eval_cases, list):
        errors.append(f"{context} eval_cases must be a list")
    else:
        for index, item in enumerate(eval_cases):
            item_path = f"{context} eval_cases[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_path} must be an object")
                continue
            for field in ("question", "expected_behavior"):
                if field not in item:
                    errors.append(f"{item_path}.{field} is required")
                else:
                    validate_non_empty_string(item[field], f"{item_path}.{field}", errors, allow_empty=True)

    for field in ("next_questions", "existential_questions"):
        _validate_string_list_section(payload, field, context, errors)

    confidence = payload.get("confidence")
    ss = payload.get("source_summary") if isinstance(payload.get("source_summary"), dict) else {}
    if not template_mode and confidence in ("high", "medium"):
        if isinstance(evidence, list) and not evidence:
            errors.append(f"{context} evidence_trace must be non-empty for {confidence} confidence")
        if isinstance(ss.get("evidence_count"), int) and ss["evidence_count"] <= 0:
            errors.append(f"{context} source_summary.evidence_count must be > 0 for {confidence} confidence")
