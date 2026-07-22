from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_release_contract", ROOT / "scripts" / "validate_release_contract.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseContractTest(unittest.TestCase):
    def test_current_candidate_is_consistent_but_blocked(self) -> None:
        errors, blockers = MODULE.validate(require_ready=False)
        self.assertEqual(errors, [])
        self.assertIn("feishu_guides", blockers)
        self.assertIn("day3_day7_forms", blockers)

    def test_release_mode_fails_closed_while_external_gates_are_missing(self) -> None:
        errors, blockers = MODULE.validate(require_ready=True)
        self.assertTrue(blockers)
        self.assertTrue(any("release is blocked by" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
