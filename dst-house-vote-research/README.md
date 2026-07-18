# DST Permanent Time — House Vote Research

Research package on the US House passage of **H.R. 139, the Sunshine Protection Act of 2025**
(House Roll Call Vote 238, 119th Congress, 2nd Session — July 14, 2026; passed 308–117 with
6 not voting), which would make daylight saving time permanent nationwide unless a state
opts out.

**Start here: [`synthesis/report.md`](synthesis/report.md)** — the full synthesis of the
research and the vote analysis.

## Contents

| Path | What it is |
|---|---|
| `synthesis/report.md` | Capstone report: research summary, vote-by-age analysis, party/gender/tenure/regional cuts, tidbits, caveats |
| `synthesis/vote_age_stats.md` / `.csv` | Computed statistics: age and tenure (mean/median/min/max) by vote position, party × vote, age-decade × vote, superlatives |
| `synthesis/compute_stats.py` | Script that produces the statistics from the raw data |
| `research/transition-costs.md` | Sourced research report on the health and economic costs of the twice-yearly clock change (traffic fatalities, cardiovascular events, other morbidity/mortality, economic estimates), including the permanent-DST-vs-permanent-standard-time counterpoint |
| `research/key-findings.md` | Bullet summary of the headline research numbers |
| `raw/votes/` | Official Clerk tally page for Roll Call 238 (user-supplied Safari webarchive + extracted HTML), the parser that reads it, the validated per-member vote CSV, and vote metadata/provenance |
| `raw/members/` | House member demographics (age at vote date, state, district, party, gender, tenure) built from the `unitedstates/congress-legislators` dataset, plus the build script and source JSON |

## Data provenance

- **Vote data:** the official Clerk of the House tally page ("Final Vote Results for
  Roll Call 238", clerk.house.gov), supplied as a Safari webarchive because this execution
  environment's network policy blocks clerk.house.gov and all mirrors. Parsed per-member
  votes validate exactly against the official chamber totals (308–117–0–6) and party table
  (R 193/22/3, D 114/95/3, I 1 Yea), with all 431 voting members matched to Bioguide IDs.
  See `raw/votes/vote_metadata.md` for details.
- **Member demographics:** `unitedstates/congress-legislators` (public-domain canonical
  dataset; joined to votes via Bioguide ID).
- **Research:** peer-reviewed studies and reputable secondary sources, cited inline in
  `research/transition-costs.md`.

## Reproducing the analysis

```sh
python3 raw/members/build_members.py   # legislators-current.json -> house_members.csv
python3 raw/votes/parse_roll238.py     # Clerk page HTML -> roll238_votes.csv (validated)
python3 synthesis/compute_stats.py     # join + stats -> vote_age_stats.{csv,md}
```

## Caveats

Ages are computed as of the vote date (2026-07-14). "Abstentions" are recorded by the
Clerk as "Not Voting". Tenure is measured from the start of each member's first House term
and may overstate continuous service for members with interrupted service. Age/tenure
patterns in a single roll call are descriptive, not causal.
