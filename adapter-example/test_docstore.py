#!/usr/bin/env python3
"""Module tests of the docstore example adapter, independent of the pdfannex CLI.

The adapter runs as a real process against the mock server in
docstore_server.py. The tests cover what an adapter must get right before any
integration test: invalid sources and options, a deleted or emptied store,
tampered content, authentication, outages, timeouts, redirects, bad service
answers, batches, protocol errors and leftover temporary files. Hashing and
locking belong to the pdfannex CLI, not to the adapter.
"""

import glob
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from conformance import conform  # noqa: E402
from docstore_server import DocstoreServer  # noqa: E402

ADAPTER = HERE / "pdfannex-resolver-docstore"
TEXLUA = shutil.which("texlua")
NEEDS = TEXLUA and shutil.which("curl")
PDF = b"%PDF-1.4\n% fake but PDF-shaped\n"
TOKEN = "s3cret-token"
DOC = "pdfannex://docstore/memo"


def sha(data):
    return hashlib.sha256(data).hexdigest()


@unittest.skipUnless(NEEDS, "texlua or curl missing")
class DocstoreAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.store = self.d / "store"
        self.rev("memo", 1, PDF + b"one")
        self.rev("memo", 2, PDF + b"two")
        self.server = DocstoreServer(self.store, TOKEN).start()
        self.env = dict(os.environ, PDFANNEX_DOCSTORE_URL=self.server.url,
                        PDFANNEX_DOCSTORE_TOKEN=TOKEN, PDFANNEX_DOCSTORE_TIMEOUT="5")
        self.temp_before = set(glob.glob("/tmp/lua_*"))

    def tearDown(self):
        self.server.stop()
        self.tmp.cleanup()

    def rev(self, doc, n, data):
        (self.store / doc).mkdir(parents=True, exist_ok=True)
        (self.store / doc / f"{n}.pdf").write_bytes(data)

    def run_adapter(self, payload, raw=None, env=None):
        data = raw if raw is not None else json.dumps(payload)
        return subprocess.run([TEXLUA, str(ADAPTER)], input=data, cwd=self.d,
                              env=env or self.env, capture_output=True, text=True)

    def call(self, op, *reqs, env=None, **extra):
        payload = {"protocolVersion": 1, "operation": op,
                   "requests": [dict(id=str(i), **r) for i, r in enumerate(reqs)]}
        payload.update(extra)
        proc = self.run_adapter(payload, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)["results"]

    def one(self, op, source, env=None, **extra):
        return self.call(op, dict(source=source, **extra), env=env)[0]

    def assertError(self, result, code):
        self.assertEqual(result.get("error", {}).get("code"), code, result)

    def new_temp_files(self):
        return set(glob.glob("/tmp/lua_*")) - self.temp_before

    # --- protocol conformance -------------------------------------------------
    def test_conforms(self):
        saved = os.environ.copy()
        os.environ.update(self.env)
        try:
            conform(str(ADAPTER), "docstore", DOC, "pdfannex://docstore/none")
        finally:
            os.environ.clear()
            os.environ.update(saved)

    # --- resolve ---------------------------------------------------------------
    def test_latest_is_pinned_in_resolved_locator(self):
        r = self.one("resolve", DOC)
        self.assertEqual(r["resolved"], DOC + "?rev=2")
        self.assertEqual(Path(r["artifact"]["path"]).read_bytes(), PDF + b"two")
        os.remove(r["artifact"]["path"])

    def test_explicit_revision(self):
        r = self.one("resolve", DOC + "?rev=1")
        self.assertEqual(r["resolved"], DOC + "?rev=1")
        self.assertEqual(Path(r["artifact"]["path"]).read_bytes(), PDF + b"one")
        os.remove(r["artifact"]["path"])

    def test_revisions_are_numeric_not_lexicographic(self):
        self.rev("memo", 10, PDF + b"ten")
        r = self.one("resolve", DOC)
        self.assertEqual(r["resolved"], DOC + "?rev=10")
        os.remove(r["artifact"]["path"])

    def test_invalid_sources(self):
        for src in ("pdfannex://docstore/", "pdfannex://docstore/../memo", "pdfannex://docstore/a/b",
                    "pdfannex://docstore/me mo", "pdfannex://docstore/memo/", "pdfannex://file/memo",
                    "memo", "", "pdfannex://docstore/%2e%2e", "pdfannex://docstore/a;b",
                    "pdfannex://docstore/a'b", "pdfannex://docstore/$(x)"):
            self.assertError(self.one("resolve", src), "invalid-source")

    def test_bad_options(self):
        for q in ("rev=0", "rev=", "rev=-1", "rev=01", "rev=1.5", "rev=1&rev=2", "rev=1234567890",
                  "x=1", "rev=1&x=2", "REV=1", "latest", "rev=1;x"):
            self.assertError(self.one("resolve", DOC + "?" + q), "unsupported-source-option")

    def test_missing_document_revision_and_empty_document(self):
        self.assertError(self.one("resolve", "pdfannex://docstore/none"), "resource-not-found")
        self.assertError(self.one("resolve", DOC + "?rev=9"), "resource-not-found")
        (self.store / "empty").mkdir()
        self.assertError(self.one("resolve", "pdfannex://docstore/empty"), "resource-not-found")

    def test_deleted_store_and_deleted_latest(self):
        (self.store / "memo" / "2.pdf").unlink()
        r = self.one("resolve", DOC)
        self.assertEqual(r["resolved"], DOC + "?rev=1")
        os.remove(r["artifact"]["path"])
        shutil.rmtree(self.store)
        self.store.mkdir()
        self.assertError(self.one("resolve", DOC), "resource-not-found")

    def test_tampered_revisions_are_refused_or_passed_through_unchanged(self):
        for data in (b"", b"%PD", b"MZ\x90\x00", b"<html>", b"\x00" * 10):
            self.rev("memo", 2, data)
            self.assertError(self.one("resolve", DOC), "resource-not-found")
        # A PDF-shaped replacement is handed over unchanged; the CLI's hash
        # check against the lock is what rejects it.
        self.rev("memo", 2, PDF + b"evil")
        r = self.one("resolve", DOC)
        self.assertEqual(Path(r["artifact"]["path"]).read_bytes(), PDF + b"evil")
        os.remove(r["artifact"]["path"])

    def test_batch_mixes_success_and_failure(self):
        out = self.call("resolve", {"source": DOC}, {"source": "pdfannex://docstore/none"},
                        {"source": DOC + "?rev=1"})
        self.assertEqual([("resolved" in r) for r in out], [True, False, True])
        self.assertEqual([r["id"] for r in out], ["0", "1", "2"])
        for r in out:
            if "artifact" in r:
                os.remove(r["artifact"]["path"])

    def test_unicode_and_odd_ids_do_not_crash(self):
        for src in ("pdfannex://docstore/Ü", "pdfannex://docstore/%00", "pdfannex://docstore/a\nb",
                    "pdfannex://docstore/" + "a" * 5000):
            self.assertIn("error", self.one("resolve", src))

    # --- authentication and configuration -----------------------------------
    def test_wrong_missing_and_unusable_tokens(self):
        for token in ("wrong", None, 'quo"te', "back\\slash", "new\nline"):
            env = dict(self.env)
            env.pop("PDFANNEX_DOCSTORE_TOKEN")
            if token is not None:
                env["PDFANNEX_DOCSTORE_TOKEN"] = token
            self.assertError(self.one("resolve", DOC, env=env), "authentication-required")

    def test_token_is_never_echoed(self):
        env = dict(self.env, PDFANNEX_DOCSTORE_TOKEN="wrong" + TOKEN)
        proc = self.run_adapter({"protocolVersion": 1, "operation": "resolve",
                                 "requests": [{"id": "a", "source": DOC}]}, env=env)
        self.assertNotIn(TOKEN, proc.stdout + proc.stderr)

    def test_missing_url_is_reported_per_request(self):
        env = {k: v for k, v in self.env.items() if k != "PDFANNEX_DOCSTORE_URL"}
        self.assertError(self.one("resolve", DOC, env=env), "temporarily-unavailable")

    def test_forbidden(self):
        self.server.force_status = 403
        self.assertError(self.one("resolve", DOC), "permission-denied")

    # --- outages and bad service answers -----------------------------------
    def test_server_down_is_temporarily_unavailable(self):
        self.server.stop()
        self.assertError(self.one("resolve", DOC), "temporarily-unavailable")
        self.assertError(self.one("status", DOC, resolved=DOC + "?rev=2"), "temporarily-unavailable")
        self.server = DocstoreServer(self.store, TOKEN).start()  # for tearDown

    def test_server_errors_and_rate_limits(self):
        for status in (429, 500, 502, 503):
            self.server.force_status = status
            self.assertError(self.one("resolve", DOC), "temporarily-unavailable")

    def test_redirects_are_not_followed(self):
        self.server.force_status = 302
        self.assertError(self.one("resolve", DOC), "temporarily-unavailable")

    def test_slow_server_times_out(self):
        self.server.delay = 3
        env = dict(self.env, PDFANNEX_DOCSTORE_TIMEOUT="1")
        self.assertError(self.one("resolve", DOC, env=env), "temporarily-unavailable")

    def test_garbage_document_description(self):
        for body in (b"not json", b"[]", b'{"latest":"2"}', b'{"latest":0}', b'{"latest":1.5}', b"{}"):
            self.server.meta_override = body
            self.assertError(self.one("resolve", DOC), "temporarily-unavailable")

    # --- status ----------------------------------------------------------------
    def status(self, source, resolved, locked_data=None):
        extra = {"resolved": resolved}
        if locked_data is not None:
            extra["lockedSha256"] = sha(locked_data)
        return self.one("status", source, **extra)

    def test_status_up_to_date_and_update_available(self):
        self.assertEqual(self.status(DOC, DOC + "?rev=2", PDF + b"two")["state"], "up-to-date")
        self.assertEqual(self.status(DOC, DOC + "?rev=1", PDF + b"one")["state"], "update-available")

    def test_status_of_pinned_source_ignores_newer_revisions(self):
        self.assertEqual(self.status(DOC + "?rev=1", DOC + "?rev=1", PDF + b"one")["state"], "up-to-date")

    def test_status_detects_tampering_in_place(self):
        self.rev("memo", 2, PDF + b"evil")
        self.assertEqual(self.status(DOC, DOC + "?rev=2", PDF + b"two")["state"], "update-available")

    def test_status_when_locked_revision_was_deleted(self):
        (self.store / "memo" / "2.pdf").unlink()
        self.rev("memo", 3, PDF + b"three")
        self.assertError(self.status(DOC, DOC + "?rev=2", PDF + b"two"), "resource-not-found")
        shutil.rmtree(self.store / "memo")
        self.assertError(self.status(DOC, DOC + "?rev=2"), "resource-not-found")

    def test_status_without_lock_information_is_unknown(self):
        self.assertEqual(self.one("status", DOC)["state"], "unknown")
        self.assertError(self.one("status", "pdfannex://docstore/none"), "resource-not-found")

    # --- protocol edges and hygiene -------------------------------------------
    def test_describe_works_without_configuration(self):
        proc = self.run_adapter(None, raw='{"operation":"describe"}', env={"PATH": os.environ["PATH"]})
        out = json.loads(proc.stdout)
        self.assertEqual(out["schemes"], ["docstore"])
        self.assertEqual(proc.returncode, 0)

    def test_bad_requests(self):
        for payload in ('{"operation":"nope"}', '[1,2]', '', '{"operation":"resolve","protocolVersion":1}',
                        '{"operation":"resolve","protocolVersion":1,"requests":"x"}'):
            proc = self.run_adapter(None, raw=payload)
            self.assertNotEqual(proc.returncode, 0, payload)
            self.assertIn("error", json.loads(proc.stdout), payload)

    def test_no_temporary_files_are_left_behind(self):
        self.one("status", DOC, resolved=DOC + "?rev=2")
        self.one("status", DOC, resolved=DOC + "?rev=2", lockedSha256=sha(PDF + b"two"))
        self.one("resolve", "pdfannex://docstore/none")
        self.one("resolve", DOC + "?x=1")
        self.rev("memo", 2, b"junk")
        self.one("resolve", DOC)
        self.server.force_status = 503
        self.one("resolve", DOC)
        self.assertEqual(self.new_temp_files(), set())

    def test_adapter_never_writes_to_the_working_directory_or_server_store(self):
        before = sorted((p, p.stat().st_mtime_ns) for p in self.d.rglob("*"))
        r = self.one("resolve", DOC)
        os.remove(r["artifact"]["path"])
        self.one("status", DOC, resolved=DOC + "?rev=2")
        self.assertEqual(before, sorted((p, p.stat().st_mtime_ns) for p in self.d.rglob("*")))


@unittest.skipUnless(TEXLUA, "texlua missing")
class MissingCurlDiagnostic(unittest.TestCase):
    def test_missing_curl_has_install_hint_and_describe_still_works(self):
        with tempfile.TemporaryDirectory() as empty_path:
            env = {"PATH": empty_path, "PDFANNEX_DOCSTORE_URL": "http://example.invalid"}
            request = {"protocolVersion": 1, "operation": "resolve",
                       "requests": [{"id": "1", "source": DOC}]}
            proc = subprocess.run([TEXLUA, str(ADAPTER)], input=json.dumps(request),
                                  cwd=empty_path, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(proc.stdout)["results"][0]
            self.assertEqual(result["error"]["code"], "temporarily-unavailable")
            self.assertIn("install curl", result["error"]["message"])
            self.assertIn("PATH", result["error"]["message"])

            proc = subprocess.run([TEXLUA, str(ADAPTER)], input='{"operation":"describe"}',
                                  cwd=empty_path, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["schemes"], ["docstore"])


if __name__ == "__main__":
    unittest.main()
