#!/usr/bin/env python3
"""Tests for profile-manager.py and validate-skill.py."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
import importlib
pm = importlib.import_module("profile-manager")


def setup_temp_repo(root: Path, skill_map: dict) -> tuple[Path, dict]:
    """Create a temporary repo with contract and templates."""
    tmp = Path(tempfile.mkdtemp())
    profiles_dir = tmp / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "templates").mkdir()
    (profiles_dir / "contracts").mkdir()
    (profiles_dir / "history").mkdir()

    contract_src = root / "profiles" / "contracts" / "skill-contract.json"
    shutil.copy2(contract_src, profiles_dir / "contracts" / "skill-contract.json")

    for slug in skill_map:
        template_src = root / skill_map[slug]["template_path"]
        shutil.copy2(template_src, profiles_dir / "templates" / template_src.name)

    tmp_contract = json.loads((profiles_dir / "contracts" / "skill-contract.json").read_text(encoding="utf-8"))
    tmp_contract["profile_root"] = "profiles"
    tmp_contract["history_root"] = "profiles/history"
    tmp_contract["templates_root"] = "profiles/templates"
    (profiles_dir / "contracts" / "skill-contract.json").write_text(
        json.dumps(tmp_contract, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    contract, sm = pm.load_contract(tmp)
    return tmp, contract, sm


class TestSlugValidation(unittest.TestCase):
    def test_valid_slugs(self):
        for slug in ("demo", "test_user", "abc123", "a"):
            self.assertTrue(pm.validate_slug(slug))

    def test_invalid_slugs(self):
        for slug in ("", "test-user", "Test", "test user", "test@user", "测试"):
            self.assertFalse(pm.validate_slug(slug))


class TestTimestampRegex(unittest.TestCase):
    def test_valid_timestamps(self):
        for ts in ("2026-04-01T120000+0800", "2026-01-01T000000-0500"):
            self.assertIsNotNone(pm.TIMESTAMP_RE.match(ts))

    def test_invalid_timestamps(self):
        for ts in ("", "2026-04-01", "120000+0800", "not-a-timestamp"):
            self.assertIsNone(pm.TIMESTAMP_RE.match(ts))


class TestJsonHelpers(unittest.TestCase):
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
            self.assertEqual(pm.load_json(path), data)


class TestLoadContract(unittest.TestCase):
    def test_load_contract(self):
        root = Path(__file__).resolve().parent.parent
        contract, skill_map = pm.load_contract(root)
        self.assertEqual(len(skill_map), 5)
        for slug in ("past_life", "cringe_archaeology", "ai_clone", "legacy_audit", "epitaph"):
            self.assertIn(slug, skill_map)


class TestInitAndValidate(unittest.TestCase):
    def test_init_and_validate(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.init_profile(contract, sm, tmp, "past_life", "test_user", False)
            self.assertEqual(code, 0)

            json_path = tmp / "profiles" / "past_life_test_user.json"
            md_path = tmp / "profiles" / "past_life_test_user.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["skill"], "past_life")
            self.assertEqual(payload["slug"], "test_user")
            self.assertEqual(payload["confidence"], "low")

            code = pm.validate_profile(contract, sm, tmp, "past_life", "test_user")
            self.assertEqual(code, 0)
        finally:
            shutil.rmtree(tmp)

    def test_init_rejects_existing(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "dup", False)
            code = pm.init_profile(contract, sm, tmp, "past_life", "dup", False)
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_init_force_overwrites(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "dup", False)
            code = pm.init_profile(contract, sm, tmp, "past_life", "dup", True)
            self.assertEqual(code, 0)
        finally:
            shutil.rmtree(tmp)


class TestSnapshotAndRollback(unittest.TestCase):
    def test_snapshot_and_rollback(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "snap_test", False)

            # Modify the profile
            json_path = tmp / "profiles" / "past_life_snap_test.json"
            payload = pm.load_json(json_path)
            payload["confidence"] = "high"
            pm.dump_json(json_path, payload)

            # Snapshot
            code = pm.snapshot_profile(contract, tmp, "past_life", "snap_test", None)
            self.assertEqual(code, 0)

            # Verify snapshot exists
            history = list((tmp / "profiles" / "history").glob("past_life_snap_test_*.json"))
            self.assertEqual(len(history), 1)

            # Modify again
            payload["confidence"] = "medium"
            pm.dump_json(json_path, payload)

            # Rollback
            code = pm.rollback_profile(contract, tmp, "past_life", "snap_test", None)
            self.assertEqual(code, 0)

            # Verify rollback
            restored = pm.load_json(json_path)
            self.assertEqual(restored["confidence"], "high")
        finally:
            shutil.rmtree(tmp)


class TestDelete(unittest.TestCase):
    def test_delete_without_yes(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "del_test", False)
            code = pm.delete_profile(contract, tmp, "past_life", "del_test", False, False)
            self.assertEqual(code, 2)
            # Files should still exist
            self.assertTrue((tmp / "profiles" / "past_life_del_test.json").exists())
        finally:
            shutil.rmtree(tmp)

    def test_delete_with_yes(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "del_test", False)
            code = pm.delete_profile(contract, tmp, "past_life", "del_test", False, True)
            self.assertEqual(code, 0)
            self.assertFalse((tmp / "profiles" / "past_life_del_test.json").exists())
        finally:
            shutil.rmtree(tmp)


class TestListProfiles(unittest.TestCase):
    def test_list_empty(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            rows = pm.discover_current_profiles(contract, sm, tmp)
            self.assertEqual(rows, [])
        finally:
            shutil.rmtree(tmp)

    def test_list_after_init(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "list_test", False)
            rows = pm.discover_current_profiles(contract, sm, tmp)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "past_life")
            self.assertEqual(rows[0][1], "list_test")
        finally:
            shutil.rmtree(tmp)


class TestDoctor(unittest.TestCase):
    def test_doctor_empty(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.doctor(contract, sm, tmp)
            self.assertEqual(code, 0)
        finally:
            shutil.rmtree(tmp)

    def test_doctor_with_profiles(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "doc_test", False)
            code = pm.doctor(contract, sm, tmp)
            self.assertEqual(code, 0)
        finally:
            shutil.rmtree(tmp)


class TestValidateSkill(unittest.TestCase):
    """Test validate-skill.py against the real repo."""

    def test_validate_real_repo(self):
        """validate-skill.py should pass on the real repo."""
        root = Path(__file__).resolve().parent.parent
        vs = importlib.import_module("validate-skill")
        code = vs.main.__code__
        # Run with the real root
        import unittest.mock
        with unittest.mock.patch("sys.argv", ["validate-skill", str(root)]):
            result = vs.main()
        self.assertEqual(result, 0)

    def test_required_root_files_exist(self):
        """All REQUIRED_ROOT_FILES should exist."""
        root = Path(__file__).resolve().parent.parent
        vs = importlib.import_module("validate-skill")
        for rel_path in vs.REQUIRED_ROOT_FILES:
            self.assertTrue((root / rel_path).exists(), f"Missing: {rel_path}")

    def test_contract_keys_defined(self):
        """REQUIRED_CONTRACT_KEYS should be non-empty."""
        vs = importlib.import_module("validate-skill")
        self.assertTrue(len(vs.REQUIRED_CONTRACT_KEYS) > 0)

    def test_template_fields_defined(self):
        """REQUIRED_TEMPLATE_FIELDS should be non-empty."""
        vs = importlib.import_module("validate-skill")
        self.assertTrue(len(vs.REQUIRED_TEMPLATE_FIELDS) > 0)

    def test_persona_layers_defined(self):
        """REQUIRED_PERSONA_LAYERS should have exactly 5 layers."""
        vs = importlib.import_module("validate-skill")
        self.assertEqual(len(vs.REQUIRED_PERSONA_LAYERS), 5)


if __name__ == "__main__":
    unittest.main()
