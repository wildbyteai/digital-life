# Changelog

## 1.3.3-beta - 2026-04-07

### Fixes

- Add missing `纠正机制` (correction mechanism) and `参考` (references) sections to `past_life.md` prompt, aligning it with the other four prompts.
- Add `纠正机制` sections to `ai_clone.md`, `legacy_audit.md`, and `epitaph.md` prompts for structural consistency with `cringe_archaeology.md`.
- Fix emoji inconsistency: 遗产清算 now uses 📊 instead of 🪦 to differentiate from 墓志铭.

### Features

- Enhance `validate-skill.py` to verify shared prompts (`persona_builder.md`, `evolution.md`), prompt cross-references to `layer0/` and `references/`, and example key coverage against contract.
- Add three missing example outputs (past_life, cringe_archaeology, epitaph) so all 5 skills now have demo files.

## 1.3.2-beta - 2026-04-02

### Features

- Upgrade the skill voice from "clever copy" to an evidence-first humanistic introspection workflow across the shared persona builder and all five prompts.
- Add explicit guardrails for writing about shame, performance, inertia, and mortality as human situations rather than diagnoses or empty philosophy.

### Documentation

- Refine `README.md` and `SKILL.md` to define the new narrative principle: evidence first, tension second, existential follow-up question last.
- Refresh `agents/openai.yaml` so the UI copy reflects the more grounded, reflective positioning.
