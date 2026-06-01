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
        for slug in ("demo", "test_user", "abc123", "a", "demo-xu", "past_life"):
            self.assertTrue(pm.is_valid_slug(slug))

    def test_invalid_slugs(self):
        for slug in ("", "Test", "test user", "test@user", "测试", ".hidden"):
            self.assertFalse(pm.is_valid_slug(slug))


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


class TestInitEdgeCases(unittest.TestCase):
    def test_init_invalid_skill(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.init_profile(contract, sm, tmp, "nonexistent", "test", False)
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_init_invalid_slug(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.init_profile(contract, sm, tmp, "past_life", "bad slug", False)
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_init_invalid_skill_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.init_profile(contract, sm, tmp, "nonexistent", "test", False, "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
        finally:
            shutil.rmtree(tmp)

    def test_init_cleans_placeholders(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "epitaph", "holder", False)
            json_path = tmp / "profiles" / "epitaph_holder.json"
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["slug"], "holder")
            self.assertIn(payload["confidence"], ("high", "medium", "low"))
            self.assertNotEqual(payload["updated_at"], "{ISO8601}")
        finally:
            shutil.rmtree(tmp)

    def test_init_invalid_slug_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.init_profile(contract, sm, tmp, "past_life", "bad slug", False, "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
        finally:
            shutil.rmtree(tmp)

    def test_init_existing_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "dup", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.init_profile(contract, sm, tmp, "past_life", "dup", False, "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
            self.assertIn("already exists", result["message"])
        finally:
            shutil.rmtree(tmp)


class TestSnapshotEdgeCases(unittest.TestCase):
    def test_snapshot_missing_profile(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.snapshot_profile(contract, tmp, "past_life", "ghost", None)
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_snapshot_invalid_timestamp(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "ts_test", False)
            code = pm.snapshot_profile(contract, tmp, "past_life", "ts_test", "bad-format")
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_snapshot_custom_timestamp(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "cts", False)
            code = pm.snapshot_profile(contract, tmp, "past_life", "cts", "2026-01-01T120000+0800")
            self.assertEqual(code, 0)
            history = list((tmp / "profiles" / "history").glob("past_life_cts_*.json"))
            self.assertEqual(len(history), 1)
            self.assertIn("2026-01-01T120000+0800", history[0].name)
        finally:
            shutil.rmtree(tmp)

    def test_snapshot_missing_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.snapshot_profile(contract, tmp, "past_life", "ghost", None, "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
        finally:
            shutil.rmtree(tmp)

    def test_snapshot_invalid_timestamp_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "tsj", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.snapshot_profile(contract, tmp, "past_life", "tsj", "bad", "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
        finally:
            shutil.rmtree(tmp)


class TestRollbackEdgeCases(unittest.TestCase):
    def test_rollback_no_history(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "nohist", False)
            code = pm.rollback_profile(contract, tmp, "past_life", "nohist", None)
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_rollback_specific_timestamp(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "rts", False)
            pm.snapshot_profile(contract, tmp, "past_life", "rts", "2026-01-01T100000+0800")

            json_path = tmp / "profiles" / "past_life_rts.json"
            payload = pm.load_json(json_path)
            payload["confidence"] = "high"
            pm.dump_json(json_path, payload)
            pm.snapshot_profile(contract, tmp, "past_life", "rts", "2026-02-01T100000+0800")

            # Rollback to first snapshot
            code = pm.rollback_profile(contract, tmp, "past_life", "rts", "2026-01-01T100000+0800")
            self.assertEqual(code, 0)
            restored = pm.load_json(json_path)
            self.assertEqual(restored["confidence"], "low")
        finally:
            shutil.rmtree(tmp)

    def test_rollback_nonexistent_timestamp(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "rbts", False)
            pm.snapshot_profile(contract, tmp, "past_life", "rbts", "2026-01-01T100000+0800")
            code = pm.rollback_profile(contract, tmp, "past_life", "rbts", "2099-01-01T000000+0000")
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_rollback_no_history_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "nhj", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.rollback_profile(contract, tmp, "past_life", "nhj", None, "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
        finally:
            shutil.rmtree(tmp)

    def test_rollback_nonexistent_timestamp_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "rbj", False)
            pm.snapshot_profile(contract, tmp, "past_life", "rbj", "2026-01-01T100000+0800")
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.rollback_profile(contract, tmp, "past_life", "rbj", "2099-01-01T000000+0000", "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
        finally:
            shutil.rmtree(tmp)


class TestDeleteEdgeCases(unittest.TestCase):
    def test_delete_with_history(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "dwh", False)
            pm.snapshot_profile(contract, tmp, "past_life", "dwh", "2026-01-01T100000+0800")
            pm.snapshot_profile(contract, tmp, "past_life", "dwh", "2026-02-01T100000+0800")

            code = pm.delete_profile(contract, tmp, "past_life", "dwh", True, True)
            self.assertEqual(code, 0)

            # Verify all files removed
            self.assertFalse((tmp / "profiles" / "past_life_dwh.json").exists())
            self.assertFalse((tmp / "profiles" / "past_life_dwh.md").exists())
            history = list((tmp / "profiles" / "history").glob("past_life_dwh_*"))
            self.assertEqual(len(history), 0)
        finally:
            shutil.rmtree(tmp)

    def test_delete_nonexistent(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.delete_profile(contract, tmp, "past_life", "ghost", False, True)
            self.assertEqual(code, 0)
        finally:
            shutil.rmtree(tmp)

    def test_delete_without_yes_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "dyj", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.delete_profile(contract, tmp, "past_life", "dyj", False, False, "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
            self.assertIn("--yes", result["message"])
        finally:
            shutil.rmtree(tmp)

    def test_delete_with_history_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "dhj", False)
            pm.snapshot_profile(contract, tmp, "past_life", "dhj", "2026-01-01T100000+0800")
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.delete_profile(contract, tmp, "past_life", "dhj", True, True, "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["with_history"], True)
            self.assertGreater(result["removed"], 0)
        finally:
            shutil.rmtree(tmp)


class TestValidateEdgeCases(unittest.TestCase):
    def test_validate_missing_profile(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.validate_profile(contract, sm, tmp, "past_life", "ghost")
            self.assertEqual(code, 1)
        finally:
            shutil.rmtree(tmp)

    def test_validate_invalid_skill(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            code = pm.validate_profile(contract, sm, tmp, "nonexistent", "test")
            self.assertEqual(code, 2)
        finally:
            shutil.rmtree(tmp)

    def test_validate_empty_markdown(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "empty_md", False)
            md_path = tmp / "profiles" / "past_life_empty_md.md"
            md_path.write_text("", encoding="utf-8")
            code = pm.validate_profile(contract, sm, tmp, "past_life", "empty_md")
            self.assertEqual(code, 1)
        finally:
            shutil.rmtree(tmp)

    def test_validate_invalid_skill_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.validate_profile(contract, sm, tmp, "nonexistent", "test", "json")
            self.assertEqual(code, 2)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "error")
        finally:
            shutil.rmtree(tmp)

    def test_validate_missing_profile_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.validate_profile(contract, sm, tmp, "past_life", "ghost", "json")
            self.assertEqual(code, 1)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "fail")
            self.assertTrue(len(result["errors"]) > 0)
        finally:
            shutil.rmtree(tmp)


class TestListEdgeCases(unittest.TestCase):
    def test_list_filtered_by_skill(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "a", False)
            pm.init_profile(contract, sm, tmp, "epitaph", "b", False)
            rows = pm.discover_current_profiles(contract, sm, tmp)
            rows = [r for r in rows if r[0] == "past_life"]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "past_life")
        finally:
            shutil.rmtree(tmp)


class TestHelperFunctions(unittest.TestCase):
    def test_now_iso_format(self):
        result = pm.now_iso()
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    def test_now_timestamp_format(self):
        result = pm.now_timestamp()
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2}T\d{6}[+-]\d{4}$")

    def test_current_paths(self):
        root = Path(__file__).resolve().parent.parent
        contract, _ = pm.load_contract(root)
        json_path, md_path = pm.current_paths(contract, root, "past_life", "test")
        self.assertEqual(json_path.name, "past_life_test.json")
        self.assertEqual(md_path.name, "past_life_test.md")

    def test_print_rows_empty(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            pm.print_rows([])
        output = buf.getvalue()
        self.assertIn("No current profile files found", output)

    def test_print_rows_with_data(self):
        import io
        from contextlib import redirect_stdout
        rows = [
            ("past_life", "test", "2026-01-01", "ok"),
            ("epitaph", "demo", "2026-02-01", "ok"),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            pm.print_rows(rows)
        output = buf.getvalue()
        self.assertIn("past_life", output)
        self.assertIn("epitaph", output)
        self.assertIn("test", output)
        self.assertIn("demo", output)

    def test_load_contract_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                pm.load_contract(Path(tmp))

    def test_load_contract_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            profiles_dir = Path(tmp) / "profiles" / "contracts"
            profiles_dir.mkdir(parents=True)
            (profiles_dir / "skill-contract.json").write_text("not json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                pm.load_contract(Path(tmp))

    def test_read_updated_at_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = pm.read_updated_at(Path(tmp) / "missing.json")
            self.assertEqual(result, "-")

    def test_read_updated_at_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("not json")
            f.flush()
            result = pm.read_updated_at(Path(f.name))
            self.assertEqual(result, "-")

    def test_read_updated_at_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            path.write_text(json.dumps({"updated_at": "2026-01-01T12:00:00+08:00"}), encoding="utf-8")
            result = pm.read_updated_at(path)
            self.assertEqual(result, "2026-01-01T12:00:00+08:00")

    def test_find_history_candidates_empty(self):
        root = Path(__file__).resolve().parent.parent
        contract, _ = pm.load_contract(root)
        with tempfile.TemporaryDirectory() as tmp:
            candidates = pm.find_history_candidates(contract, Path(tmp), "past_life", "ghost")
            self.assertEqual(candidates, [])

    def test_find_history_candidates_with_data(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "fhc", False)
            pm.snapshot_profile(contract, tmp, "past_life", "fhc", "2026-01-01T100000+0800")
            pm.snapshot_profile(contract, tmp, "past_life", "fhc", "2026-02-01T100000+0800")
            candidates = pm.find_history_candidates(contract, tmp, "past_life", "fhc")
            self.assertEqual(len(candidates), 2)
            self.assertEqual(candidates[0][0], "2026-01-01T100000+0800")
            self.assertEqual(candidates[1][0], "2026-02-01T100000+0800")
        finally:
            shutil.rmtree(tmp)


class TestDoctorEdgeCases(unittest.TestCase):
    def test_doctor_json_with_failures(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "bad", False)
            # Corrupt the json
            json_path = tmp / "profiles" / "past_life_bad.json"
            json_path.write_text("not json", encoding="utf-8")
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.doctor(contract, sm, tmp, "json")
            self.assertEqual(code, 1)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "fail")
            self.assertGreater(result["failures"], 0)
        finally:
            shutil.rmtree(tmp)

    def test_doctor_template_missing_persona_layer(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            # Corrupt a template by removing a persona layer
            template_path = tmp / "profiles" / "templates" / "past_life.json"
            template = json.loads(template_path.read_text(encoding="utf-8"))
            del template["persona"]["layer4_boundaries"]
            template_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.doctor(contract, sm, tmp, "json")
            self.assertEqual(code, 1)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("persona missing layer" in e for e in result.get("errors", [])))
        finally:
            shutil.rmtree(tmp)

    def test_doctor_template_missing_existential_question(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            template_path = tmp / "profiles" / "templates" / "past_life.json"
            template = json.loads(template_path.read_text(encoding="utf-8"))
            del template["existential_question"]
            template_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.doctor(contract, sm, tmp, "json")
            self.assertEqual(code, 1)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("existential_question" in e for e in result.get("errors", [])))
        finally:
            shutil.rmtree(tmp)


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

    def test_list_json_output(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "ljson", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.list_profiles(contract, sm, tmp, None, "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["skill"], "past_life")
            self.assertEqual(result[0]["slug"], "ljson")
        finally:
            shutil.rmtree(tmp)

    def test_list_filtered_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "a", False)
            pm.init_profile(contract, sm, tmp, "epitaph", "b", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.list_profiles(contract, sm, tmp, "past_life", "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["skill"], "past_life")
        finally:
            shutil.rmtree(tmp)

    def test_list_missing_md(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "nomd", False)
            # Remove the markdown file
            md_path = tmp / "profiles" / "past_life_nomd.md"
            md_path.unlink()
            rows = pm.discover_current_profiles(contract, sm, tmp)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][3], "missing_md")
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


class TestValidateJsonOutput(unittest.TestCase):
    """Test validate and doctor JSON output format."""

    def test_validate_json_ok(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "vjson", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.validate_profile(contract, sm, tmp, "past_life", "vjson", "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["profile"], "past_life_vjson")
        finally:
            shutil.rmtree(tmp)

    def test_doctor_json_empty(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.doctor(contract, sm, tmp, "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["templates_checked"], 5)
            self.assertEqual(result["profiles_checked"], 0)
        finally:
            shutil.rmtree(tmp)

    def test_doctor_json_with_profiles(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "djson", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.doctor(contract, sm, tmp, "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["templates_checked"], 5)
            self.assertEqual(result["profiles_checked"], 1)
        finally:
            shutil.rmtree(tmp)

    def test_snapshot_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "sjson", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.snapshot_profile(contract, tmp, "past_life", "sjson", None, "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "ok")
            self.assertIn("timestamp", result)
        finally:
            shutil.rmtree(tmp)

    def test_rollback_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "rjson", False)
            pm.snapshot_profile(contract, tmp, "past_life", "rjson", None)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.rollback_profile(contract, tmp, "past_life", "rjson", None, "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "ok")
            self.assertIn("timestamp", result)
        finally:
            shutil.rmtree(tmp)

    def test_delete_json(self):
        root = Path(__file__).resolve().parent.parent
        _, skill_map = pm.load_contract(root)
        tmp, contract, sm = setup_temp_repo(root, skill_map)
        try:
            pm.init_profile(contract, sm, tmp, "past_life", "djson2", False)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = pm.delete_profile(contract, tmp, "past_life", "djson2", False, True, "json")
            self.assertEqual(code, 0)
            result = json.loads(buf.getvalue())
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["removed"], 2)
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

    def test_naming_keys_defined(self):
        """REQUIRED_NAMING_KEYS should have exactly 4 keys."""
        vs = importlib.import_module("validate-skill")
        self.assertEqual(len(vs.REQUIRED_NAMING_KEYS), 4)

    def test_example_json_files_defined(self):
        """EXAMPLE_JSON_FILES should have exactly 5 files."""
        vs = importlib.import_module("validate-skill")
        self.assertEqual(len(vs.EXAMPLE_JSON_FILES), 5)

    def test_gitignore_rules_defined(self):
        """GITIGNORE_RULES should be non-empty."""
        vs = importlib.import_module("validate-skill")
        self.assertTrue(len(vs.GITIGNORE_RULES) > 0)

    def test_gitattributes_rules_defined(self):
        """GITATTRIBUTES_RULES should be non-empty."""
        vs = importlib.import_module("validate-skill")
        self.assertTrue(len(vs.GITATTRIBUTES_RULES) > 0)

    def test_slug_re_matches_valid(self):
        """SLUG_RE should match valid slugs."""
        vs = importlib.import_module("validate-skill")
        for slug in ("past_life", "demo-wei", "abc123"):
            self.assertRegex(slug, vs.SLUG_RE)

    def test_slug_re_rejects_invalid(self):
        """SLUG_RE should reject invalid slugs."""
        vs = importlib.import_module("validate-skill")
        for slug in ("", "Test", "test user", "test@user"):
            self.assertNotRegex(slug, vs.SLUG_RE)


if __name__ == "__main__":
    unittest.main()
