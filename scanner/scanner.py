"""
Cardano GitHub Scanner
Scans Cardano-related orgs for issues and opportunities.
"""

import os
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

CARDANO_ORGS = [
    "IntersectMBO",
    "input-output-hk",
    "cardanofoundation",
    "SundaeSwap-finance",
    "Minswap",
    "midnightntwrk"
]

def list_repos(org):
    url = f"https://api.github.com/orgs/{org}/repos?per_page=100"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return [r["name"] for r in resp.json()]

def list_issues(org, repo, label="bug"):
    url = f"https://api.github.com/repos/{org}/{repo}/issues?state=open&labels={label}&per_page=50"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    return [{"number": i["number"], "title": i["title"], "url": i["html_url"]} for i in resp.json()]

def scan_org(org):
    print(f"Scanning {org}...")
    try:
        repos = list_repos(org)
    except Exception as e:
        print(f"  Error listing repos: {e}")
        return []
    findings = []
    for repo in repos[:20]:  # limit for demo
        issues = list_issues(org, repo)
        if issues:
            findings.append({"repo": repo, "issues": issues})
    return findings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", help="Specific org to scan")
    args = parser.parse_args()
    orgs = [args.org] if args.org else CARDANO_ORGS
    for org in orgs:
        findings = scan_org(org)
        print(f"{org}: {len(findings)} repos with open bugs")

if __name__ == "__main__":
    main()
