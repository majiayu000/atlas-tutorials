"""Offline tests for the tutorial helper, not tests of Atlas APIs."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "receipt_id.py"
spec = importlib.util.spec_from_file_location("receipt_id", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReceiptTests(unittest.TestCase):
    def test_submission(self):
        self.assertEqual(module.extract_id({"id": "pred_demo", "status": "processing"}), "pred_demo")

    def test_wait_response(self):
        self.assertEqual(module.extract_id({"prediction_id": "pred_demo"}), "pred_demo")

    def test_agreeing_fields(self):
        self.assertEqual(module.extract_id({"id": "pred_demo", "prediction_id": "pred_demo"}), "pred_demo")

    def test_conflicting_fields(self):
        with self.assertRaises(ValueError):
            module.extract_id({"id": "a", "prediction_id": "b"})

    def test_invalid_payloads(self):
        for payload in ([], None, {}, {"id": ""}, {"id": 123}, {"data": {"id": "hidden"}}, {"id": "a\nb"}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                module.extract_id(payload)

    def test_cli_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text('{"id":"pred_demo"}', encoding="utf-8")
            proc = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(proc.stdout.strip(), "pred_demo")

    def test_cli_malformed_and_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            for body in ("", '{"id":'):
                path.write_text(body, encoding="utf-8")
                proc = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 2)
                self.assertEqual(proc.stdout, "")
                self.assertIn("不要因此自动重新生成", proc.stderr)

    def test_cli_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            proc = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
