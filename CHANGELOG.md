# Changelog

## 1.4.0-beta - 2026-04-07

### Features

- Restructure `prompts/past_life.md` to match the unified 怎么问/数据从哪来/产出什么 format used by all other prompts.
- Add 纠正机制 (correction mechanism) section to `ai_clone.md`, `legacy_audit.md`, and `epitaph.md` for consistent user feedback handling across all 5 skills.
- Add demo examples for `past_life`, `cringe_archaeology`, and `epitaph` — all 5 skills now have complete JSON + Markdown examples.

### Documentation

- Update `examples/README.md` to list all 5 demo example sets.
- Update `README.md` to link all 5 demo examples with skill labels.
- Expand `validate-skill.py` to check all 5 example files for structural completeness.

## 1.3.2-beta - 2026-04-02

### Features

- Upgrade the skill voice from "clever copy" to an evidence-first humanistic introspection workflow across the shared persona builder and all five prompts.
- Add explicit guardrails for writing about shame, performance, inertia, and mortality as human situations rather than diagnoses or empty philosophy.

### Documentation

- Refine `README.md` and `SKILL.md` to define the new narrative principle: evidence first, tension second, existential follow-up question last.
- Refresh `agents/openai.yaml` so the UI copy reflects the more grounded, reflective positioning.
