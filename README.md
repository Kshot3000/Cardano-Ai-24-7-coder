# Cardano AI 24/7 Coder

Automated scanning, problem solving, and tool building for Cardano GitHub ecosystem.

## Mission
Continuously scan Cardano-related GitHub organizations and repositories, identify bugs, missing features, and opportunities, then build tools, fixers, and new applications.

## Scope
Organizations scanned:
- IntersectMBO
- input-output-hk
- Cardano Foundation
- SundaeSwap
- Minswap
- Midnight
- And related Cardano projects

## Tools
- `scanner/scanner.py` – GitHub API scanner for issues/PRs (the working tool)
- `tools/auto_fix_template.py` – template for generated fixes; **not implemented yet** — `apply_fix` raises `NotImplementedError` rather than claiming a fix it did not make
- `apps/example_app.py` – minimal example-app scaffold (prints a startup line only)

## Automation
The `Cardano AI 24/7 Scan` GitHub Actions workflow runs the scanner every
6 hours (and on manual dispatch) and uploads the generated `reports/` as a
run artifact (retained 30 days), so scan output is kept instead of being
discarded when the job ends.

## Usage
```bash
pip install -r requirements.txt
python scanner/scanner.py --org IntersectMBO --label bug
```
Without `--org` it scans every org in `scanner/scanner.py`'s `CARDANO_ORGS`
list (see ORGS_PRIORITY.md for the tiering). `--label` defaults to `bug`;
`--max-repos` (default 20) caps how many of each org's top repos are scanned;
it must be a positive integer (0 or negative values are rejected, exit 2).
The scanner pages through each org's full repo list, ignores pull requests
when collecting issues, and times out any hung GitHub request after 30s.

`python generate_reports.py` writes per-org report *scaffolds* only — it
never invents repo names or star counts. Live figures come solely from
running the scanner, which overwrites the scaffolds with real GitHub data.

## Tests
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
```
All HTTP is mocked — no network or token needed. The suite guards the
documented CLI flags, pagination, PR filtering, request timeouts, and the
no-invented-data rule for reports.

## Donation
Cardano: addr1q8hnl6vl5a6k3rw3n5g3jtte696zcl76kfatzv7gpswa9r0dj7fma6klq55y4ffm7tf0em09udnyhuk4ah92pl5x9jpqjae44v

Built by [@kshot9000](https://x.com/kshot9000) · [github.com/Kshot3000](https://github.com/Kshot3000)
