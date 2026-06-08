"""Shared validation helpers for digital-life scripts."""
from __future__ import annotations

from typing import Any

CONFIDENCE_VALUES = ("high", "medium", "low")
SEVERITY_VALUES = ("high", "medium", "low")

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


def _validate_string_list_section(payload: dict[str, Any], field: str, context: str, errors: list[str]) -> None:
    if field in payload:
        validate_list_of_strings(payload[field], f"{context} {field}", errors)


def validate_distilled_life(
    payload: dict[str, Any],
    context: str,
    errors: list[str],
    *,
    template_mode: bool = False,
) -> None:
    """Validate distilled_life nested structures used by templates, examples, and profiles."""
    validate_source_summary(payload, context, errors, template_mode=template_mode)

    if "persona" in payload:
        validate_persona(payload["persona"], context, errors, strict_nested=True)

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
                    validate_non_empty_string(item[field], f"{item_path}.{field}", errors, allow_empty=True)
            for field in ("actions", "options", "reasoning", "quotes"):
                if field not in item:
                    errors.append(f"{item_path}.{field} is required")
                else:
                    validate_list_of_strings(item[field], f"{item_path}.{field}", errors)

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
                    validate_non_empty_string(item[field], f"{item_path}.{field}", errors, allow_empty=(field != "source_id"))
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
