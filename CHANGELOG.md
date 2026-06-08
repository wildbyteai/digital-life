# Changelog

## 1.5.2-beta - 2026-06-09

### Improvements

- Fixed stale published agent metadata so `agents/openai.yaml` no longer describes only five archaeology modes.
- Made `profile-manager.py --version` and `validate-skill.py --version` read the package `VERSION` dynamically.
- Added release consistency checks for `VERSION`, `SKILL.md`, README badge/version section, CHANGELOG latest heading, and CLI version output.
- Hardened profile validation for slug, updated_at, version, confidence, and source_summary fields across all skills.
- Hardened GitHub Actions validation with Python compilation, unittest discovery, concurrency cancellation, and a job timeout.
- Added `.yml` line-ending rule validation for workflow files.

### Testing

- Updated profile validation tests so malformed slug, updated_at, version, confidence readiness, and empty source_summary cases now fail instead of being documented as acceptable.

## 1.5.1-beta - 2026-06-08

### Improvements

- Added shared `validation_rules.py` helpers for source summary, persona, and `distilled_life` nested structures.
- Added strict nested validation for `distilled_life` decision models, expression models, life stories, skill assets, boundary rules, evidence trace, eval cases, and medium/high confidence readiness.
- Added GitHub Actions CI to run repository validation, profile doctor, and Python unit tests on pushes and pull requests.
- Added 3 分钟启动 examples, Can/Cannot guidance, pre-write privacy checklist, confidence/permission definitions, and a correction-turn demo for 蒸馏人生.
- Reframed privacy docs around local profile storage, `.gitignore`, cloud-model caveats, minimal necessary data, and third-party redaction.

### Testing

- Expanded unit coverage from 265 to 281 tests, including malformed `distilled_life` profile structures and safety-critical nested fields.

## 1.5.0-beta - 2026-06-08

### Features

- Added `distilled_life` / 蒸馏人生 as the 6th digital-life skill.
- Added decision replay, expression drafting, evidence trace, boundary rules, eval cases, and reusable Skill Asset concepts for experience distillation.
- Added `prompts/distilled_life.md`, `layer0/distilled_life.md`, `references/distilled_life.md`, and `profiles/templates/distilled_life.json`.
- Added fictional/desensitized `distilled_life_demo.json` and `distilled_life_demo.md` examples.

### Documentation

- Updated README, SKILL metadata, examples README, and version files for the new mode.
- Clarified that 蒸馏人生 helps users reuse themselves through evidence-backed judgment and expression models, not impersonate themselves.

### Testing

- Updated validation/test fixtures to include the 6th skill and example set.

## 1.4.1-beta - 2026-06-02

### Improvements

- Expanded `layer0/` hard rules for all 5 skills with counter-examples and gray area guidance (previously only `past_life.md` had this depth).
- Added `--version` flag to both `profile-manager.py` and `validate-skill.py`.
- Added `--format json` to `profile-manager.py validate` for machine-readable output.
- Improved CLI help text with per-argument descriptions for all subcommands.
- `profile-manager.py init` now validates template existence and cleans placeholder values before writing.
- `profile-manager.py doctor` now reports template count alongside profile count.
- `profile-manager.py validate` now checks persona layer completeness (layer0-layer4).
- `validate-skill.py` now validates example JSON persona layers and confidence values.
- Extracted module-level constants in `validate-skill.py` for contract keys, template fields, persona layers, and naming keys.
- Unified error handling in `profile-manager.py main()` to catch `json.JSONDecodeError`.
- Added `ai_clone.json` template sub-fields for `public_persona` and `private_persona`.
- Added `legacy_audit.json` template sub-fields for `regret_patterns`.

### Testing

- Added `scripts/test_scripts.py` with 24 unit tests covering slug validation, JSON helpers, contract loading, init/validate/snapshot/rollback/delete/list/doctor workflows, and JSON output format.

## 1.4.0-beta - 2026-04-07

### Features

- Restructure `prompts/past_life.md` to match the unified 怎么问/数据从哪来/产出什么 format used by all other prompts.
- Add 纠正机制 (correction mechanism) section to `ai_clone.md`, `legacy_audit.md`, and `epitaph.md` for consistent user feedback handling across all 5 skills.
- Add demo examples for `past_life`, `cringe_archaeology`, and `epitaph` — all 5 skills now have complete JSON + Markdown examples.

### Maintenance

- Unify `references/` filenames from hyphens to underscores, matching all other directories.
- Wire `prompts/evolution.md` into SKILL.md Step 5 so the append/correct workflow is reachable by agents.
- Update `README.md` directory tree to list all 10 example files.

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
