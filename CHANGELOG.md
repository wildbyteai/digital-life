# Changelog

## 1.3.2 - 2026-04-02

### Features

- Upgrade the skill voice from "clever copy" to an evidence-first humanistic introspection workflow across the shared persona builder and all five prompts.
- Add explicit guardrails for writing about shame, performance, inertia, and mortality as human situations rather than diagnoses or empty philosophy.

### Documentation

- Refine `README.md` and `SKILL.md` to define the new narrative principle: evidence first, tension second, existential follow-up question last.
- Refresh `agents/openai.yaml` so the UI copy reflects the more grounded, reflective positioning.

## 1.3.1 - 2026-04-02

### Maintenance

- Switch to single-developer minimal mode: keep `skill-contract.json`, `profile-manager.py`, and `validate-skill.py` as the core maintenance toolchain.
- Remove duplicate PowerShell validator and remove heavy architecture reference document to reduce maintenance overhead.
- Simplify README self-check and directory guidance around the single validation entrypoint.

## 1.3.0 - 2026-04-02

### Features

- Add production architecture contract at `profiles/contracts/skill-contract.json` and make validation contract-driven.
- Add `scripts/profile-manager.py` for profile lifecycle operations: list, init, snapshot, rollback, delete, validate, and doctor.
- Add architecture reference `references/architecture.md` to define layered responsibilities, failure fallback, and readiness checklist.

### Documentation

- Upgrade `README.md`, `SKILL.md`, `prompts/evolution.md`, and `profiles/README.md` with executable management commands and production workflow details.

### Maintenance

- Enhance `validate-skill.py` and `validate-skill.ps1` to verify contract integrity, path consistency, required keys, and ops assets.

## 1.2.0 - 2026-04-01

### Features

- Complete the skill packaging for `digital-life` with UI metadata, SVG icons, profile templates, privacy-safe output layout, and built-in validation scripts.
- Add desensitized example outputs so GitHub visitors can see the actual report shape without exposing personal data.

### Documentation

- Rewrite `README.md` and `SKILL.md` to align trigger flow, output conventions, history snapshots, and repository structure.
- Document local profile storage, rollback strategy, and developer validation commands.

### Maintenance

- Add `.gitattributes`, `VERSION`, and cross-platform validation so the repository is easier to release and maintain over time.
