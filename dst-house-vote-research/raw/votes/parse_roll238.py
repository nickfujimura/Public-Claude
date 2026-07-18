#!/usr/bin/env python3
"""Parse the official Clerk 'Final Vote Results for Roll Call 238' page (saved as a
Safari webarchive of https://clerk.house.gov/evs/2026/roll238.xml rendered via the
Clerk's XSL) into a per-member CSV joined to Bioguide IDs.

Clerk formatting conventions: Republicans in roman, Democrats in <i>italic</i>,
Independents <u>underlined</u>; duplicate surnames disambiguated with '(ST)' and/or
'Last, First' forms. Non-voting Delegates/Resident Commissioner never appear.

Outputs raw/votes/roll238_votes.csv: bioguide_id, name_as_listed, full_name,
party, state, district, vote.
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = (HERE / "roll238_clerk_page.html").read_text()
LEGISLATORS = HERE.parent / "members" / "legislators-current.json"
OUT = HERE / "roll238_votes.csv"

NON_VOTING_STATES = {"DC", "PR", "GU", "AS", "VI", "MP"}
PARTY_BY_MARKUP = {"i": "Democrat", "u": "Independent", None: "Republican"}
EXPECTED = {"Yea": 308, "Nay": 117, "Not Voting": 6}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def extract_entries(html: str):
    """Yield (display_name, markup_tag, vote) for every listed member."""
    sections = [
        ("Yea", re.search(r"---- YEAS.*?<table.*?>(.*?)</table>", html, re.S)),
        ("Nay", re.search(r"---- NAYS.*?<table.*?>(.*?)</table>", html, re.S)),
        ("Not Voting", re.search(r"---- NOT VOTING.*?<table.*?>(.*?)</table>", html, re.S)),
    ]
    for vote, m in sections:
        if not m:
            sys.exit(f"Could not locate section: {vote}")
        body = m.group(1)
        for chunk in re.split(r"<br\s*/?>", body):
            chunk = re.sub(r"</?(?:td|tr|tbody|table)[^>]*>", "", chunk).strip()
            if not chunk:
                continue
            tag_m = re.match(r"^<(i|u)>(.*?)</\1>$", chunk)
            tag, name = (tag_m.group(1), tag_m.group(2)) if tag_m else (None, chunk)
            name = re.sub(r"<[^>]+>", "", name).replace("&nbsp;", " ").strip()
            if name:
                yield name, tag, vote


def load_reps():
    reps = []
    for m in json.load(open(LEGISLATORS)):
        t = m["terms"][-1]
        if t["type"] != "rep" or t["state"] in NON_VOTING_STATES:
            continue
        reps.append(
            {
                "bioguide_id": m["id"]["bioguide"],
                "last": m["name"]["last"],
                "first": m["name"]["first"],
                "nickname": m["name"].get("nickname", ""),
                "official_full": m["name"].get("official_full", f"{m['name']['first']} {m['name']['last']}"),
                "party": t["party"],
                "state": t["state"],
                "district": t["district"],
            }
        )
    return reps


def match(display: str, party: str, reps):
    state_m = re.search(r"\(([A-Z]{2})\)\s*$", display)
    state = state_m.group(1) if state_m else None
    core = re.sub(r"\s*\([A-Z]{2}\)\s*$", "", display).strip()
    first_hint = None
    if "," in core:
        core, first_hint = (p.strip() for p in core.split(",", 1))

    def try_pool(pool):
        if state:
            pool = [r for r in pool if r["state"] == state]
        if first_hint:
            fh = fold(first_hint).rstrip(".")
            pool = [
                r
                for r in pool
                if fold(r["first"]).startswith(fh)
                or fold(r["nickname"]).startswith(fh)
                or fold(r["official_full"]).startswith(fh)
            ]
        return pool

    # exact last-name match, party-constrained
    pool = try_pool([r for r in reps if fold(r["last"]) == fold(core) and r["party"] == party])
    if len(pool) == 1:
        return pool[0]
    # last-name match ignoring party (party switches, data lag) — only if unique
    if not pool:
        pool = try_pool([r for r in reps if fold(r["last"]) == fold(core)])
        if len(pool) == 1:
            return pool[0]
    # substring of official_full (multi-word surnames recorded differently)
    if not pool:
        pool = try_pool([r for r in reps if fold(core) in fold(r["official_full"]) and r["party"] == party])
        if len(pool) == 1:
            return pool[0]
    return None if len(pool) != 1 else pool[0]


def main():
    reps = load_reps()
    rows, unmatched, used = [], [], {}
    for display, tag, vote in extract_entries(HTML):
        party = PARTY_BY_MARKUP[tag]
        r = match(display, party, reps)
        if r is None:
            unmatched.append((display, party, vote))
            continue
        if r["bioguide_id"] in used:
            sys.exit(f"Duplicate match: {display} and {used[r['bioguide_id']]} both -> {r['bioguide_id']}")
        used[r["bioguide_id"]] = display
        if r["party"] != party:
            print(f"note: party mismatch for {display}: clerk={party}, dataset={r['party']}", file=sys.stderr)
        rows.append(
            {
                "bioguide_id": r["bioguide_id"],
                "name_as_listed": display,
                "full_name": r["official_full"],
                "party": party,
                "state": r["state"],
                "district": r["district"],
                "vote": vote,
            }
        )

    counts = {}
    for row in rows:
        counts[row["vote"]] = counts.get(row["vote"], 0) + 1
    print(f"Matched {len(rows)} members; counts={counts}; expected={EXPECTED}")
    if unmatched:
        print("UNMATCHED:", file=sys.stderr)
        for u in unmatched:
            print(f"  {u}", file=sys.stderr)
        sys.exit(1)
    if counts != EXPECTED:
        sys.exit(f"Count mismatch: {counts} != {EXPECTED}")

    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
