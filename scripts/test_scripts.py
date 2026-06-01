#!/usr/bin/env python3
"""Tests for profile-manager.py and validate-skill.py."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

# Import functions from profile-manager
import sys
sys.path.insert(0, str(Path(__file__).parent))
import importlib
pm = importlib.import_module("profile-manager")


class TestSlugValidation(unittest.TestCase):
    """Test slug validation."""

    def test_valid_slugs(self):
        for slug in ("demo", "test_user", "abc123", "a"):
            self.assertTrue(pm.validate_slug(slug), f"Expected valid: {slug}")

    def test_invalid_slugs(self):
        for slug in ("", "test-user", "Test", "test user", "test@user", "测试"):
            self.assertFalse(pm.validate_slug(slug), f"Expected invalid: {slug}")


class TestTimestampRegex(unittest.TestCase):
    """Test timestamp regex."""

    def test_valid_timestamps(self):
        for ts in ("2026-04-01T120000+0800", "2026-01-01T000000-0500"):
            self.assertIsNotNone(pm.TIMESTAMP_RE.match(ts), f"Expected valid: {ts}")

    def test_invalid_timestamps(self):
        for ts in ("", "2026-04-01", "120000+0800", "not-a-timestamp"):
            self.assertIsNone(pm.TIMESTAMP_RE.match(ts), f"Expected invalid: {ts}")


class TestJsonHelpers(unittest.TestCase):
    """Test JSON load/dump helpers."""

    def test_load_json_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                pm.load_json(Path(tmp) / "missing.json")

    def test_load_json_invalid(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("not json")
            f.flush()
            with self.assertRaises(json.JSONDecodeError):
                pm.load_json(Path(f.name))

    def test_dump_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            data = {"key": "value", "number": 42}
            pm.dump_json(path, data)
            loaded = pm.load_json(path)
            self.assertEqual(loaded, data)


class TestLoadContract(unittest.TestCase):
    """Test contract loading."""

    def test_load_contract(self):
        root = Path(__file__).resolve().parent.parent
        contract, skill_map = pm.load_contract(root)
        self.assertIn("skills", contract)
        self.assertEqual(len(skill_map), 5)
        for slug in ("past_life", "cringe_archaeology", "ai_clone", "legacy_audit", "epitaph"):
            self.assertIn(slug, skill_map)


class TestInitAndValidate(unittest.TestCase):
    """Test init and validate workflow."""

    def test_init_and_validate(self):
        root = Path(__file__).resolve().parent.parent
        contract, skill_map = pm.load_contract(root)

        with tempfile.TemporaryDirectory() as tmp:
            # Copy templates to temp dir
            tmp_path = Path(tmp)
            profiles_dir = tmp_path / "profiles"
            profiles_dir.mkdir()
            templates_dir = profiles_dir / "templates"
            templates_dir.mkdir()
            contracts_dir = profiles_dir / "contracts"
            contracts_dir.mkdir()
            history_dir = profiles_dir / "history"
            history_dir.mkdir()

            # Copy contract
            import shutil
            contract_src = root / "profiles" / "contracts" / "skill-contract.json"
            shutil.copy2(contract_src, contracts_dir / "skill-contract.json")

            # Copy templates
            for slug in skill_map:
                template_src = root / skill_map[slug]["template_path"]
                shutil.copy2(template_src, templates_dir / template_src.name)

            # Update contract paths for temp dir
            tmp_contract = json.loads((contracts_dir / "skill-contract.json").read_text(encoding="utf-8"))
            tmp_contract["profile_root"] = "profiles"
            tmp_contract["history_root"] = "profiles/history"
            tmp_contract["templates_root"] = "profiles/templates"
            (contracts_dir / "skill-contract.json").write_text(
                json.dumps(tmp_contract, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            # Reload contract from temp dir
            tmp_contract, tmp_skill_map = pm.load_contract(tmp_path)

            # Test init
            code = pm.init_profile(tmp_contract, tmp_skill_map, tmp_path, "past_life", "test_user", False)
            self.assertEqual(code, 0)

            # Verify files exist
            json_path = profiles_dir / "past_life_test_user.json"
            md_path = profiles_dir / "past_life_test_user.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())

            # Verify JSON content
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["skill"], "past_life")
            self.assertEqual(payload["slug"], "test_user")
            self.assertIn("updated_at", payload)
            self.assertEqual(payload["confidence"], "low")

            # Test validate
            code = pm.validate_profile(tmp_contract, tmp_skill_map, tmp_path, "past_life", "test_user")
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
