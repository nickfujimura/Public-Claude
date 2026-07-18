#!/usr/bin/env python3
"""Join House roll call 238 (H.R. 139, Sunshine Protection Act) to member demographics
and compute age/tenure statistics by vote position.

Inputs:
  raw/votes/roll238_votes.csv — per-member votes parsed from the official Clerk page
                                by raw/votes/parse_roll238.py
  raw/members/house_members.csv — demographics from unitedstates/congress-legislators

Outputs (written next to this script):
  vote_age_stats.csv      — age/tenure stats (mean/median/min/max) per vote position
  vote_age_stats.md       — human-readable stats tables, crosstabs, and superlatives
"""
import csv
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOTES_PATH = HERE.parent / "raw" / "votes" / "roll238_votes.csv"
MEMBERS_PATH = HERE.parent / "raw" / "members" / "house_members.csv"
EXPECTED = {"Yea": 308, "Nay": 117, "Present": 0, "Not Voting": 6}


def stats_block(values):
    if not values:
        return {"n": 0, "mean": "", "median": "", "min": "", "max": ""}
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 1),
        "median": round(statistics.median(values), 1),
        "min": min(values),
        "max": max(values),
    }


def main():
    if not VOTES_PATH.exists():
        sys.exit(f"Missing {VOTES_PATH}. Run raw/votes/parse_roll238.py first.")
    with open(VOTES_PATH, newline="") as f:
        votes = list(csv.DictReader(f))

    counts = {}
    for v in votes:
        counts[v["vote"]] = counts.get(v["vote"], 0) + 1
    mismatches = {k: (counts.get(k, 0), exp) for k, exp in EXPECTED.items() if counts.get(k, 0) != exp}
    if mismatches:
        print(f"WARNING: vote totals differ from expected {EXPECTED}: got {counts}", file=sys.stderr)

    with open(MEMBERS_PATH, newline="") as f:
        members = {row["bioguide_id"]: row for row in csv.DictReader(f)}

    unmatched = [v for v in votes if v["bioguide_id"] not in members]
    joined = [
        {**v, **members[v["bioguide_id"]]} for v in votes if v["bioguide_id"] in members
    ]

    positions = ["Yea", "Nay", "Present", "Not Voting"]
    rows, md = [], []
    md.append("# Roll Call 238 — age and tenure by vote position\n")
    md.append(f"Vote counts: {counts}. Joined {len(joined)}/{len(votes)} members to demographics"
              + (f"; UNMATCHED: {[v['bioguide_id'] + ' ' + v['name_as_listed'] for v in unmatched]}" if unmatched else ".") + "\n")

    md.append("| Vote | n | Mean age | Median age | Min age | Max age | Mean tenure (yrs) | Median tenure |")
    md.append("|---|---|---|---|---|---|---|---|")
    for pos in positions:
        grp = [m for m in joined if m["vote"] == pos]
        ages = [float(m["age_at_vote"]) for m in grp if m["age_at_vote"]]
        tenures = [float(m["house_tenure_years"]) for m in grp if m["house_tenure_years"]]
        a, t = stats_block(ages), stats_block(tenures)
        rows.append({"vote": pos, "metric": "age", **a})
        rows.append({"vote": pos, "metric": "tenure_years", **t})
        md.append(f"| {pos} | {a['n']} | {a['mean']} | {a['median']} | {a['min']} | {a['max']} | {t['mean']} | {t['median']} |")

    # Party x vote crosstab
    md.append("\n## Party × vote\n")
    parties = sorted({m["party"] for m in joined})
    md.append("| Party | " + " | ".join(positions) + " | Mean age Yea | Mean age Nay |")
    md.append("|---|" + "---|" * (len(positions) + 2))
    for p in parties:
        cells = [str(sum(1 for m in joined if m["party"] == p and m["vote"] == pos)) for pos in positions]
        ya = [float(m["age_at_vote"]) for m in joined if m["party"] == p and m["vote"] == "Yea"]
        na = [float(m["age_at_vote"]) for m in joined if m["party"] == p and m["vote"] == "Nay"]
        cells += [str(round(statistics.mean(ya), 1)) if ya else "—",
                  str(round(statistics.mean(na), 1)) if na else "—"]
        md.append(f"| {p} | " + " | ".join(cells) + " |")

    # Age decade x vote
    md.append("\n## Age decade × vote (share voting Yea among those voting)\n")
    md.append("| Age band | Yea | Nay | % Yea |")
    md.append("|---|---|---|---|")
    for lo in range(20, 100, 10):
        band = [m for m in joined if lo <= float(m["age_at_vote"]) < lo + 10 and m["vote"] in ("Yea", "Nay")]
        if not band:
            continue
        y = sum(1 for m in band if m["vote"] == "Yea")
        n = len(band) - y
        md.append(f"| {lo}–{lo + 9} | {y} | {n} | {round(100 * y / len(band))}% |")

    # Superlatives
    md.append("\n## Superlatives\n")
    for pos in ("Yea", "Nay", "Not Voting"):
        grp = sorted((m for m in joined if m["vote"] == pos), key=lambda m: float(m["age_at_vote"]))
        if grp:
            yng, old = grp[0], grp[-1]
            md.append(f"- **{pos}** — youngest: {yng['full_name']} ({yng['party'][0]}-{yng['state']}), "
                      f"{yng['age_at_vote']}; oldest: {old['full_name']} ({old['party'][0]}-{old['state']}), {old['age_at_vote']}")
    nv = [m for m in joined if m["vote"] == "Not Voting"]
    if nv:
        md.append("- **Not voting:** " + "; ".join(
            f"{m['full_name']} ({m['party'][0]}-{m['state']}, age {m['age_at_vote']})" for m in nv))

    with open(HERE / "vote_age_stats.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["vote", "metric", "n", "mean", "median", "min", "max"])
        w.writeheader()
        w.writerows(rows)
    (HERE / "vote_age_stats.md").write_text("\n".join(md) + "\n")
    print(f"Wrote vote_age_stats.csv, vote_age_stats.md. Counts: {counts}")
    if unmatched:
        print(f"Unmatched bioguide IDs: {unmatched}", file=sys.stderr)


if __name__ == "__main__":
    main()
