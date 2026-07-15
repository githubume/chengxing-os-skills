from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "shared" / "scripts" / "local_store.py"
PROFILE = ROOT / "shared" / "profile-schema" / "example.profile.json"
CASE = ROOT / "shared" / "case-schema" / "example.case.json"


class LocalStoreTests(unittest.TestCase):
    def run_store(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_profile_requires_confirmation_and_supports_show_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = str(Path(tmp) / "data")
            refused = self.run_store("profile", "write", "--plugin", "habit-rebuild", "--base-dir", base, "--input", str(PROFILE))
            self.assertEqual(refused.returncode, 2)
            self.assertIn("write refused", refused.stderr)

            written = self.run_store("profile", "write", "--plugin", "habit-rebuild", "--base-dir", base, "--input", str(PROFILE), "--confirm-write")
            self.assertEqual(written.returncode, 0, written.stderr)
            target = Path(base) / "habit-rebuild" / "profile.json"
            self.assertTrue(target.is_file())
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)

            shown = self.run_store("profile", "show", "--plugin", "habit-rebuild", "--base-dir", base)
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertEqual(json.loads(shown.stdout)["plugin"], "habit-rebuild")

            preview = self.run_store("profile", "delete", "--plugin", "habit-rebuild", "--base-dir", base)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertTrue(target.exists())
            self.assertFalse(json.loads(preview.stdout)["will_delete"])

            deleted = self.run_store("profile", "delete", "--plugin", "habit-rebuild", "--base-dir", base, "--confirm-delete")
            self.assertEqual(deleted.returncode, 0, deleted.stderr)
            self.assertFalse(target.exists())

    def test_plugin_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_store("profile", "write", "--plugin", "parent-learning", "--base-dir", str(Path(tmp) / "data"), "--input", str(PROFILE), "--confirm-write")
            self.assertEqual(result.returncode, 2)
            self.assertIn("plugin mismatch", result.stderr)

    def test_case_write_and_b3_invariant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = str(Path(tmp) / "data")
            written = self.run_store("case", "write", "--plugin", "habit-rebuild", "--base-dir", base, "--input", str(CASE), "--confirm-write")
            self.assertEqual(written.returncode, 0, written.stderr)
            target = Path(base) / "cases" / "demo-habit-001" / "case.json"
            self.assertTrue(target.is_file())

            unsafe = json.loads(CASE.read_text(encoding="utf-8"))
            unsafe["route"] = "B3"
            unsafe_path = Path(tmp) / "unsafe.json"
            unsafe_path.write_text(json.dumps(unsafe, ensure_ascii=False), encoding="utf-8")
            rejected = self.run_store("case", "write", "--plugin", "habit-rebuild", "--base-dir", base, "--input", str(unsafe_path), "--confirm-write")
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("B3 must stop ordinary plans", rejected.stderr)

    def test_case_export_requires_consent_and_preview(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = str(Path(tmp) / "data")
            case = json.loads(CASE.read_text(encoding="utf-8"))
            source = Path(tmp) / "case.json"
            source.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
            written = self.run_store("case", "write", "--plugin", "habit-rebuild", "--base-dir", base, "--input", str(source), "--confirm-write")
            self.assertEqual(written.returncode, 0, written.stderr)
            refused = self.run_store("case", "export", "--plugin", "habit-rebuild", "--base-dir", base, "--case-id", case["case_id"], "--format", "markdown")
            self.assertEqual(refused.returncode, 2)
            self.assertIn("consent.export=true", refused.stderr)

            case["consent"]["export"] = True
            source.write_text(json.dumps(case, ensure_ascii=False), encoding="utf-8")
            updated = self.run_store("case", "write", "--plugin", "habit-rebuild", "--base-dir", base, "--input", str(source), "--confirm-write")
            self.assertEqual(updated.returncode, 0, updated.stderr)
            preview = self.run_store("case", "export", "--plugin", "habit-rebuild", "--base-dir", base, "--case-id", case["case_id"], "--format", "markdown")
            self.assertEqual(preview.returncode, 0, preview.stderr)
            preview_data = json.loads(preview.stdout)
            self.assertFalse(preview_data["will_write"])
            self.assertIn("# 成行 OS 案例", preview_data["preview"])
            output = Path(preview_data["path"])
            self.assertFalse(output.exists())

            exported = self.run_store("case", "export", "--plugin", "habit-rebuild", "--base-dir", base, "--case-id", case["case_id"], "--format", "markdown", "--confirm-write")
            self.assertEqual(exported.returncode, 0, exported.stderr)
            self.assertTrue(output.is_file())
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)

    def test_symlink_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "data"
            outside = Path(tmp) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            plugin_dir = base / "habit-rebuild"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "profile.json").symlink_to(outside)
            result = self.run_store("profile", "write", "--plugin", "habit-rebuild", "--base-dir", str(base), "--input", str(PROFILE), "--confirm-write")
            self.assertEqual(result.returncode, 2)
            self.assertIn("target must not be a symlink", result.stderr)
            self.assertEqual(outside.read_text(encoding="utf-8"), "{}")


if __name__ == "__main__":
    unittest.main()
