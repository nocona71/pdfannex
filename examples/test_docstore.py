#!/usr/bin/env python3
"""Module tests of the docstore example adapter, independent of the CLI.

Run these first when changing the adapter (or a fork of it): they call the
executable directly with Resolver Protocol 1 requests and cover the store being
tampered with or emptied. Hashing and locking belong to the CLI and are covered
by testfiles/test_cli.py.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "testfiles"))
from resolver_conformance import conform  # noqa: E402

ADAPTER = ROOT / "examples" / "pdfannex-resolver-docstore"
NEEDS = shutil.which("texlua")
PDF = b"%PDF-1.4\n% fake but PDF-shaped\n"


def sha(data):
    return hashlib.sha256(data).hexdigest()


@unittest.skipUnless(NEEDS, "texlua missing")
class DocstoreAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.store = self.d / "store"
        self.rev("memo", 1, PDF + b"one")
        self.rev("memo", 2, PDF + b"two")

    def tearDown(self):
        self.tmp.cleanup()

    def rev(self, doc, n, data):
        (self.store / doc).mkdir(parents=True, exist_ok=True)
        (self.store / doc / f"{n}.pdf").write_bytes(data)

    def call(self, op, *reqs, **extra):
        payload = {"protocolVersion": 1, "operation": op,
                   "requests": [dict(id=str(i), **r) for i, r in enumerate(reqs)]}
        payload.update(extra)
        env = dict(os.environ, PDFANNEX_DOCSTORE_DIR=str(self.store))
        proc = subprocess.run(["texlua", str(ADAPTER)], input=json.dumps(payload), cwd=self.d,
                              env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return [r for r in json.loads(proc.stdout)["results"]]

    def one(self, op, source, **extra):
        return self.call(op, dict(source=source, **extra))[0]

    def assertError(self, result, code):
        self.assertEqual(result.get("error", {}).get("code"), code, result)

    # --- protocol conformance -------------------------------------------------
    def test_conforms(self):
        env = os.environ.copy()
        os.environ["PDFANNEX_DOCSTORE_DIR"] = str(self.store)
        try:
            conform(str(ADAPTER), "docstore", "pdfannex://docstore/memo", "pdfannex://docstore/none")
        finally:
            os.environ.clear()
            os.environ.update(env)

    # --- resolve ---------------------------------------------------------------
    def test_latest_is_pinned_in_resolved_locator(self):
        r = self.one("resolve", "pdfannex://docstore/memo")
        self.assertEqual(r["resolved"], "pdfannex://docstore/memo?rev=2")
        self.assertEqual(Path(r["artifact"]["path"]).read_bytes(), PDF + b"two")

    def test_explicit_revision(self):
        r = self.one("resolve", "pdfannex://docstore/memo?rev=1")
        self.assertEqual(r["resolved"], "pdfannex://docstore/memo?rev=1")
        self.assertEqual(Path(r["artifact"]["path"]).read_bytes(), PDF + b"one")

    def test_revisions_are_numeric_not_lexicographic(self):
        self.rev("memo", 10, PDF + b"ten")
        self.assertEqual(self.one("resolve", "pdfannex://docstore/memo")["resolved"],
                         "pdfannex://docstore/memo?rev=10")

    def test_non_canonical_revision_files_are_ignored(self):
        for name in ("03.pdf", "x.pdf", "3.pdf.bak", "3.PDF", "0.pdf"):
            (self.store / "memo" / name).write_bytes(PDF)
        self.assertEqual(self.one("resolve", "pdfannex://docstore/memo")["resolved"],
                         "pdfannex://docstore/memo?rev=2")

    def test_invalid_sources(self):
        for src in ("pdfannex://docstore/", "pdfannex://docstore/../memo", "pdfannex://docstore/a/b",
                    "pdfannex://docstore/me mo", "pdfannex://docstore/memo/", "pdfannex://file/memo",
                    "memo", "", "pdfannex://docstore/%2e%2e"):
            self.assertError(self.one("resolve", src), "invalid-source")

    def test_bad_options(self):
        for q in ("rev=0", "rev=", "rev=-1", "rev=01", "rev=1.5", "rev=1&rev=2", "rev=1234567890",
                  "x=1", "rev=1&x=2", "REV=1", "latest"):
            self.assertError(self.one("resolve", "pdfannex://docstore/memo?" + q),
                             "unsupported-source-option")

    def test_missing_document_revision_and_empty_document(self):
        self.assertError(self.one("resolve", "pdfannex://docstore/none"), "resource-not-found")
        self.assertError(self.one("resolve", "pdfannex://docstore/memo?rev=9"), "resource-not-found")
        (self.store / "empty").mkdir()
        self.assertError(self.one("resolve", "pdfannex://docstore/empty"), "resource-not-found")

    def test_deleted_store_and_deleted_latest(self):
        (self.store / "memo" / "2.pdf").unlink()
        self.assertEqual(self.one("resolve", "pdfannex://docstore/memo")["resolved"],
                         "pdfannex://docstore/memo?rev=1")
        shutil.rmtree(self.store)
        self.assertError(self.one("resolve", "pdfannex://docstore/memo"), "resource-not-found")

    def test_tampered_revisions_are_refused_or_passed_through_unchanged(self):
        # Not PDF-shaped, empty, truncated header: refused by the adapter.
        for data in (b"", b"%PD", b"MZ\x90\x00", b"<html>", b"\x00" * 10):
            self.rev("memo", 2, data)
            self.assertError(self.one("resolve", "pdfannex://docstore/memo"), "resource-not-found")
        # PDF-shaped replacement: the adapter hands it over unchanged; the CLI
        # hash check against the lock is what rejects it.
        self.rev("memo", 2, PDF + b"evil")
        r = self.one("resolve", "pdfannex://docstore/memo")
        self.assertEqual(Path(r["artifact"]["path"]).read_bytes(), PDF + b"evil")

    def test_symlinks_and_directories_are_refused(self):
        secret = self.d / "secret.pdf"
        secret.write_bytes(PDF + b"secret")
        (self.store / "memo" / "2.pdf").unlink()
        os.symlink(secret, self.store / "memo" / "2.pdf")
        self.assertError(self.one("resolve", "pdfannex://docstore/memo?rev=2"), "resource-not-found")
        os.symlink(self.store / "memo", self.store / "alias")
        self.assertError(self.one("resolve", "pdfannex://docstore/alias"), "resource-not-found")
        (self.store / "dir").mkdir()
        (self.store / "dir" / "1.pdf").mkdir()
        self.assertError(self.one("resolve", "pdfannex://docstore/dir?rev=1"), "resource-not-found")

    @unittest.skipIf(os.geteuid() == 0, "root can read everything")
    def test_unreadable_revision(self):
        path = self.store / "memo" / "2.pdf"
        path.chmod(0)
        try:
            self.assertError(self.one("resolve", "pdfannex://docstore/memo?rev=2"), "permission-denied")
        finally:
            path.chmod(0o644)

    def test_batch_mixes_success_and_failure(self):
        out = self.call("resolve", {"source": "pdfannex://docstore/memo"},
                        {"source": "pdfannex://docstore/none"},
                        {"source": "pdfannex://docstore/memo?rev=1"})
        self.assertEqual([("resolved" in r) for r in out], [True, False, True])
        self.assertEqual([r["id"] for r in out], ["0", "1", "2"])

    def test_unicode_and_odd_ids_do_not_crash(self):
        for src in ("pdfannex://docstore/Ü", "pdfannex://docstore/%00", "pdfannex://docstore/a\nb",
                    "pdfannex://docstore/" + "a" * 5000):
            self.assertIn("error", self.one("resolve", src))

    # --- status ----------------------------------------------------------------
    def status(self, source, resolved, locked_data=None):
        extra = {"resolved": resolved}
        if locked_data is not None:
            extra["lockedSha256"] = sha(locked_data)
        return self.one("status", source, **extra)

    def test_status_up_to_date_and_update_available(self):
        self.assertEqual(self.status("pdfannex://docstore/memo", "pdfannex://docstore/memo?rev=2",
                                     PDF + b"two")["state"], "up-to-date")
        self.assertEqual(self.status("pdfannex://docstore/memo", "pdfannex://docstore/memo?rev=1",
                                     PDF + b"one")["state"], "update-available")

    def test_status_of_pinned_source_ignores_newer_revisions(self):
        self.assertEqual(self.status("pdfannex://docstore/memo?rev=1", "pdfannex://docstore/memo?rev=1",
                                     PDF + b"one")["state"], "up-to-date")

    def test_status_detects_tampering_in_place(self):
        self.rev("memo", 2, PDF + b"evil")
        self.assertEqual(self.status("pdfannex://docstore/memo", "pdfannex://docstore/memo?rev=2",
                                     PDF + b"two")["state"], "update-available")

    def test_status_when_locked_revision_was_deleted(self):
        (self.store / "memo" / "2.pdf").unlink()
        self.assertError(self.status("pdfannex://docstore/memo", "pdfannex://docstore/memo?rev=2",
                                     PDF + b"two"), "resource-not-found")
        shutil.rmtree(self.store / "memo")
        self.assertError(self.status("pdfannex://docstore/memo", "pdfannex://docstore/memo?rev=2"),
                         "resource-not-found")

    def test_status_without_lock_information_is_unknown(self):
        self.assertEqual(self.one("status", "pdfannex://docstore/memo")["state"], "unknown")
        self.assertError(self.one("status", "pdfannex://docstore/none"), "resource-not-found")

    # --- protocol edges --------------------------------------------------------
    def test_describe_and_bad_requests(self):
        proc = subprocess.run(["texlua", str(ADAPTER)], input='{"operation":"describe"}',
                              capture_output=True, text=True)
        out = json.loads(proc.stdout)
        self.assertEqual(out["schemes"], ["docstore"])
        for payload in ('{"operation":"nope"}', '[1,2]', '', '{"operation":"resolve","protocolVersion":1}',
                        '{"operation":"resolve","protocolVersion":1,"requests":"x"}'):
            proc = subprocess.run(["texlua", str(ADAPTER)], input=payload, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0, payload)
            self.assertIn("error", json.loads(proc.stdout), payload)

    def test_adapter_never_writes_to_the_store(self):
        before = sorted((p, p.stat().st_mtime_ns) for p in self.store.rglob("*"))
        self.one("resolve", "pdfannex://docstore/memo")
        self.one("status", "pdfannex://docstore/memo", resolved="pdfannex://docstore/memo?rev=2")
        self.assertEqual(before, sorted((p, p.stat().st_mtime_ns) for p in self.store.rglob("*")))


if __name__ == "__main__":
    unittest.main()
