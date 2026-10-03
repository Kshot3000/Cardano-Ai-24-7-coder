"""Tests for the Cardano GitHub scanner and report scaffolds.

Run from the repo root:  python -m unittest discover -s tests -v
All HTTP is mocked — no network, no token needed.
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scanner import scanner  # noqa: E402
import generate_reports  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise scanner.requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def repo(name, stars):
    return {"name": name, "stargazers_count": stars}


class ListReposTests(unittest.TestCase):
    def test_paginates_past_first_100_and_sorts_by_stars(self):
        page1 = [repo(f"r{i}", i) for i in range(100)]
        page2 = [repo("biggest", 99999), repo("small", 1)]
        with mock.patch.object(scanner.requests, "get",
                               side_effect=[FakeResponse(page1), FakeResponse(page2)]) as get:
            repos = scanner.list_repos("SomeOrg")
        self.assertEqual(len(repos), 102)
        self.assertEqual(repos[0]["name"], "biggest")
        self.assertEqual(get.call_count, 2)

    def test_requests_carry_a_timeout(self):
        with mock.patch.object(scanner.requests, "get",
                               return_value=FakeResponse([repo("a", 1)])) as get:
            scanner.list_repos("SomeOrg")
        self.assertEqual(get.call_args.kwargs.get("timeout"), scanner.REQUEST_TIMEOUT)


class ListIssuesTests(unittest.TestCase):
    def test_pull_requests_are_not_reported_as_issues(self):
        payload = [
            {"number": 7, "title": "Real bug", "html_url": "https://example.test/7"},
            {"number": 8, "title": "A PR, not an issue", "html_url": "https://example.test/8",
             "pull_request": {"url": "https://example.test/pr/8"}},
        ]
        with mock.patch.object(scanner.requests, "get", return_value=FakeResponse(payload)) as get:
            issues = scanner.list_issues("Org", "repo", label="bug")
        self.assertEqual([i["number"] for i in issues], [7])
        self.assertEqual(get.call_args.kwargs["params"]["labels"], "bug")

    def test_http_failure_returns_empty_not_crash(self):
        with mock.patch.object(scanner.requests, "get",
                               side_effect=scanner.requests.ConnectionError("down")):
            self.assertEqual(scanner.list_issues("Org", "repo"), [])


class CliTests(unittest.TestCase):
    def test_readme_usage_label_flag_is_accepted(self):
        # README documents: python scanner/scanner.py --org IntersectMBO --label bug
        # That command used to die with "unrecognized arguments: --label".
        with mock.patch.object(scanner, "scan_org", return_value=[]) as scan:
            rc = scanner.main(["--org", "IntersectMBO", "--label", "bug"])
        self.assertEqual(rc, 0)
        self.assertEqual(scan.call_args.kwargs["label"], "bug")


class HonestyTests(unittest.TestCase):
    def test_scaffold_invents_no_repos_or_stars(self):
        text = generate_reports.scaffold("IntersectMBO")
        self.assertNotIn("repo1", text)
        self.assertNotIn("10000", text)
        self.assertIn("Not scanned yet", text)
        self.assertIn(scanner.DONATION_ADDR, text)

    def test_org_lists_agree(self):
        self.assertEqual(generate_reports.CARDANO_ORGS, scanner.CARDANO_ORGS)

    def test_committed_report_has_no_invented_repos(self):
        with open(os.path.join(ROOT, "reports", "IntersectMBO_report.md")) as f:
            self.assertNotIn("repo1", f.read())

    def test_gitignore_blocks_env_files(self):
        with open(os.path.join(ROOT, ".gitignore")) as f:
            text = f.read()
        self.assertIn("\n.env\n", "\n" + text)
        self.assertIn("!.env.example", text)

    def test_org_list_has_no_verified_dead_slugs(self):
        # All three were verified against the GitHub org API (2026-10-02):
        # MLabsHaskell 404s (real org: mlabs-haskell); cardano-node and
        # cardano-wallet are repositories, not orgs.
        self.assertNotIn("MLabsHaskell", scanner.CARDANO_ORGS)
        self.assertNotIn("cardanofoundation", scanner.CARDANO_ORGS)
        self.assertNotIn("cardano-node", scanner.CARDANO_ORGS)
        self.assertNotIn("cardano-wallet", scanner.CARDANO_ORGS)
        self.assertIn("mlabs-haskell", scanner.CARDANO_ORGS)
        self.assertIn("cardano-foundation", scanner.CARDANO_ORGS)

    def test_funding_file_uses_no_unknown_platform_key(self):
        with open(os.path.join(ROOT, ".github", "FUNDING.yml")) as f:
            for line in f:
                self.assertFalse(line.startswith("cardano:"), line)


if __name__ == "__main__":
    unittest.main()
