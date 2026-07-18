# House Roll Call Vote 238 (2026) — H.R. 139, Sunshine Protection Act of 2025

**Verified aggregate data.** Collected 2026-07-18 via web search across multiple independent
sources (House Clerk summary snippets, GovTrack, NBC News, CBS News, CNN, The Hill,
Washington Post, House Energy & Commerce Committee release).

| Field | Value |
|---|---|
| Bill | H.R. 139 — Sunshine Protection Act of 2025 |
| Congress / Session | 119th Congress, 2nd Session |
| Roll call | 238 |
| Date / time | July 14, 2026, 5:17 PM ET |
| Question | On Passage |
| Vote type | Yea-and-Nay |
| Result | **Passed 308–117** (0 Present, 6 Not Voting) |
| Next step | Sent to the Senate (prospects uncertain; opposition to the Senate companion in committee from both parties) |

## Party breakdown (voting members)

| Party | Yea | Nay |
|---|---|---|
| Republican | 193 | 22 |
| Democrat | 114 | 95 |
| Independent | 1* | 0* |

\* Inferred: reported party splits (R 193–22, D 114–95) sum to 307 Yea / 117 Nay; the
chamber totals are 308–117, so the House's one Independent voted Yea.

## What the bill does

Makes daylight saving time the new permanent standard time nationwide (the clock setting
currently observed March–November), eliminating the twice-yearly clock change, unless a
state exempts itself before the act takes effect. Backed by President Trump.

## Color

Rep. Scott DesJarlais (R-TN), presiding over the vote, played the Beatles'
"Here Comes the Sun" from his phone while reading the final tally.

## Per-member data status

**Complete.** The execution environment's network egress policy blocks clerk.house.gov
(and every mirror: govtrack.us, voteview.com, congress.gov, govinfo.gov, c-span.org,
web.archive.org, news/wiki sites), so the per-member data could not be fetched directly.
The user uploaded a Safari webarchive of the official Clerk page
(https://clerk.house.gov/evs/2026/roll238.xml as rendered by the Clerk's site —
"Final Vote Results for Roll Call 238") to the branch. Pipeline:

1. `Final Vote Results for Roll Call 238.webarchive` — user-supplied official Clerk page
2. `roll238_clerk_page.html` — HTML payload extracted from the webarchive
3. `parse_roll238.py` — parses the Clerk page (roman = Republican, *italic* = Democrat,
   underline = Independent; "(ST)"/"Last, First" disambiguators) and joins each of the
   431 voting members to a Bioguide ID via `raw/members/legislators-current.json`
4. `roll238_votes.csv` — the result; validated to exactly match the official chamber
   totals (308–117–0–6) **and** the official party table (R 193/22/3, D 114/95/3, I 1 Yea),
   with 431 unique members and zero unmatched names

An earlier agent run produced *mock* per-member data as a placeholder; it was deleted to
avoid any chance of fabricated data being mistaken for real votes.

## Sources

- https://clerk.house.gov/Votes/2026238 (official record; blocked from this session, verified via search snippets)
- https://www.govtrack.us/congress/votes/119-2026/h238
- https://www.nbcnews.com/politics/congress/house-passes-bill-daylight-saving-time-permanent-sunshine-protection-rcna587531
- https://www.cbsnews.com/news/daylight-saving-time-permanent-house-vote/
- https://www.cnn.com/2026/07/14/politics/house-vote-daylight-savings-time
- https://thehill.com/homenews/house/5968255-house-sunshine-protection-act-daylight-saving-time/
- https://www.washingtonpost.com/politics/2026/07/14/trumps-plan-make-daylight-saving-time-permanent-get-vote-house/
- https://energycommerce.house.gov/posts/house-passes-legislation-to-make-daylight-saving-time-permanent
