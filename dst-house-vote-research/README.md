# DST Permanent Time — House Vote Research

Research package on the US House passage of **H.R. 139, the Sunshine Protection Act of 2025**
(House Roll Call Vote 238, 119th Congress, 2nd Session — July 14, 2026; passed 308–117 with
6 not voting), which would make daylight saving time permanent nationwide unless a state
opts out.

## Contents

| Path | What it is |
|---|---|
| `raw/votes/` | Official House Clerk roll call XML for vote 238, parsed per-member CSV, parser script, and vote metadata |
| `raw/members/` | House member demographics (age, state, district, party, tenure) built from the `unitedstates/congress-legislators` dataset, plus the build script and source JSON |
| `research/` | Sourced research on the health and economic costs of the twice-yearly clock change (traffic fatalities, cardiovascular events, other mortality/morbidity, economic estimates), including the permanent-DST-vs-permanent-standard-time counterpoint |
| `synthesis/` | Final synthesis report joining the vote to member demographics — age statistics (mean/median/min/max) by vote position, party/region breakdowns, notable tidbits — plus the analysis script and computed stats tables |

## Data provenance

- Vote data: clerk.house.gov (official Clerk of the House electronic vote system XML)
- Member demographics: unitedstates/congress-legislators (public-domain canonical dataset; joined to votes via Bioguide ID)
- Research: peer-reviewed studies and reputable secondary sources, cited inline in `research/transition-costs.md`

Ages are computed as of the vote date (2026-07-14). "Abstentions" are recorded by the
Clerk as "Not Voting". Tenure is measured from the start of each member's first House term
and may overstate continuous service for members with interrupted service.
