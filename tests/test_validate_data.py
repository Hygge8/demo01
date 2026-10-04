"""Integrity checks use synthetic CSV records and never touch customer data."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


VALIDATOR = Path(__file__).resolve().parents[1] / "scripts" / "validate_data.py"


class ValidateDataTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.csv = self.directory / "example.csv"
        self.manifest = self.directory / "manifest.json"
        self.content = b'id,note\r\n1,"first line\r\nsecond line"\r\n2,"a,b"\r\n'
        self.csv.write_bytes(self.content)
        self.entry = {
            "path": "data/raw/example.csv",
            "rows": 2,
            "bytes": len(self.content),
            "sha256": hashlib.sha256(self.content).hexdigest(),
            "columns": ["id", "note"],
        }
        self.save_manifest()

    def save_manifest(self):
        self.manifest.write_text(
            json.dumps({"schema_version": 1, "files": [self.entry]}), encoding="utf-8"
        )

    def run_validator(self, *options):
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--manifest", str(self.manifest),
             "--data-dir", str(self.directory), *options],
            capture_output=True, text=True, check=False, cwd=self.directory,
        )

    def assert_failure(self, expected_message, *options):
        result = self.run_validator(*options)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected_message, result.stderr)

    def replace_and_accept_checksum(self, content, rows):
        """Isolate CSV structure checks from expected byte and hash differences."""
        self.csv.write_bytes(content)
        self.entry.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest(), rows=rows)
        self.save_manifest()

    def test_quoted_newlines_and_commas_are_two_records(self):
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: 1 file(s) (full)", result.stdout)
        self.assertNotIn("first line", result.stdout + result.stderr)

    def test_missing_file_fails_full_and_quick(self):
        self.csv.unlink()
        for options in ((), ("--quick",)):
            with self.subTest(options=options):
                self.assert_failure("missing file", *options)

    def test_wrong_header_fails_full_and_quick(self):
        self.csv.write_bytes(self.content.replace(b"id,note", b"id,text"))
        for options in ((), ("--quick",)):
            with self.subTest(options=options):
                self.assert_failure("header mismatch", *options)

    def test_truncated_quoted_record_is_invalid_csv(self):
        self.replace_and_accept_checksum(b'id,note\n1,"unfinished', 1)
        self.assert_failure("invalid CSV")

    def test_row_width_is_checked_even_with_matching_checksum(self):
        self.replace_and_accept_checksum(b"id,note\n1\n2,ok,extra\n", 2)
        self.assert_failure("row width mismatch in 2 record(s)")

    def test_blank_record_is_not_silently_skipped(self):
        self.replace_and_accept_checksum(b"id,note\n\n", 1)
        self.assert_failure("row width mismatch")

    def test_hash_detects_same_size_change(self):
        self.csv.write_bytes(self.content.replace(b"first", b"other"))
        self.assert_failure("SHA-256 mismatch")

    def test_row_count_is_checked_independently_of_hash(self):
        self.entry["rows"] = 3
        self.save_manifest()
        self.assert_failure("row count mismatch (expected 3, got 2)")

    def test_quick_intentionally_skips_records_and_hash(self):
        self.replace_and_accept_checksum(b'id,note\n1,"unfinished', 999)
        self.entry["sha256"] = "0" * 64
        self.save_manifest()
        result = self.run_validator("--quick")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(quick)", result.stdout)

    def test_size_is_checked_in_quick_mode(self):
        self.csv.write_bytes(self.content + b"3,extra\r\n")
        self.assert_failure("size mismatch", "--quick")

    def test_quick_does_not_check_body_encoding(self):
        self.replace_and_accept_checksum(b"id,note\n1,\xff\n", 1)
        result = self.run_validator("--quick")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_utf8_fails_without_printing_record(self):
        self.replace_and_accept_checksum(b"id,note\n1,\xff\n", 1)
        self.assert_failure("invalid UTF-8 encoding")

    def test_invalid_manifest_is_a_configuration_error(self):
        self.entry["path"] = "../example.csv"
        self.save_manifest()
        result = self.run_validator()
        self.assertEqual(result.returncode, 2)
        self.assertIn("paths must stay within", result.stderr)

    def test_default_paths_are_relative_to_repository_not_cwd(self):
        repository = self.directory / "repository"
        (repository / "scripts").mkdir(parents=True)
        (repository / "data" / "raw").mkdir(parents=True)
        copied_script = repository / "scripts" / "validate_data.py"
        shutil.copyfile(VALIDATOR, copied_script)
        shutil.copyfile(self.csv, repository / "data" / "raw" / "example.csv")
        shutil.copyfile(self.manifest, repository / "data" / "manifest.json")
        result = subprocess.run(
            [sys.executable, str(copied_script)], cwd=self.directory,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
