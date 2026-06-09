# Skill Package Examples

This directory contains public-safe, fictional `distilled_life` skill packages.

A package is a portable artifact distilled from evidence into reusable skills. It is not a digital clone and must not claim to be a real person.

Current demo:

- [`writing_style_demo`](writing_style_demo/manifest.json) — fictional evidence-first writing style package with local sources, source hashes, exports, and static tests.
- [`decision_principles_demo`](decision_principles_demo/manifest.json) — generated fictional decision-principles package built from `examples/distilled_life_demo.json`.

Validate and inspect it with:

```bash
python3 scripts/package-manager.py validate examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py test examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py export-prompt examples/skill_packages/writing_style_demo
python3 scripts/package-manager.py build-from-profile examples/distilled_life_demo.json --output /tmp/decision_principles_demo --package-id decision_principles_demo_tmp --name "Decision Principles Demo" --force
```

All source files in this directory are fictional/desensitized demo material and are safe for public GitHub publication.
