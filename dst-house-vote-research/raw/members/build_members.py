#!/usr/bin/env python3
"""
Build a demographics dataset for current members of the US House of
Representatives (119th Congress), as of a reference date.

Source: unitedstates/congress-legislators project
  https://unitedstates.github.io/congress-legislators/legislators-current.json
  (mirrored locally as legislators-current.json in this directory)

Output: house_members.csv in this same directory.
"""

import csv
import json
import os
from datetime import date

# Reference date for age / tenure calculations.
REFERENCE_DATE = date(2026, 7, 14)

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(HERE, "legislators-current.json")
OUTPUT_PATH = os.path.join(HERE, "house_members.csv")


def parse_iso_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def years_between(start, end):
    """Precise fractional-year difference between two date objects."""
    delta_days = (end - start).days
    return delta_days / 365.25


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        legislators = json.load(f)

    rows = []
    missing_birthday = []

    for leg in legislators:
        terms = leg.get("terms", [])
        if not terms:
            continue

        # Most recent term determines current chamber/state/district/party.
        current_term = terms[-1]
        if current_term.get("type") != "rep":
            # Not currently serving in the House (e.g. a Senator, or a
            # member whose most recent term was a Senate term).
            continue

        bioguide_id = leg.get("id", {}).get("bioguide", "")
        name = leg.get("name", {})
        full_name = " ".join(
            part
            for part in [name.get("first"), name.get("middle"), name.get("last")]
            if part
        )
        # Prefer official_full if present.
        if name.get("official_full"):
            full_name = name["official_full"]

        bio = leg.get("bio", {})
        gender = bio.get("gender", "")
        birthday_str = bio.get("birthday", "")
        birthday = parse_iso_date(birthday_str)

        state = current_term.get("state", "")
        district = current_term.get("district", "")
        party = current_term.get("party", "")

        # All terms served as a House member ("rep"), in chronological order
        # (the source data lists terms chronologically already, but sort
        # defensively on term start date).
        rep_terms = [t for t in terms if t.get("type") == "rep"]
        rep_terms_sorted = sorted(
            rep_terms, key=lambda t: parse_iso_date(t.get("start")) or date.min
        )
        first_term_start = parse_iso_date(rep_terms_sorted[0].get("start")) if rep_terms_sorted else None
        total_terms = len(rep_terms)

        if birthday is None:
            missing_birthday.append((bioguide_id, full_name))
            age_at_vote = ""
        else:
            age_at_vote = round(years_between(birthday, REFERENCE_DATE), 1)

        if first_term_start is None:
            house_tenure_years = ""
        else:
            # NOTE: this measures years from the member's EARLIEST House
            # term start date to the reference date. It does NOT account
            # for gaps in service (e.g. a member who served, lost
            # re-election, and later returned to the House) -- for such
            # members this will overstate actual cumulative years served.
            house_tenure_years = round(years_between(first_term_start, REFERENCE_DATE), 1)

        rows.append(
            {
                "bioguide_id": bioguide_id,
                "full_name": full_name,
                "state": state,
                "district": district,
                "party": party,
                "gender": gender,
                "birthday": birthday_str,
                "age_at_vote": age_at_vote,
                "first_house_term_start": rep_terms_sorted[0].get("start") if rep_terms_sorted else "",
                "house_tenure_years": house_tenure_years,
                "total_terms": total_terms,
            }
        )

    # Sort by state then district for readability.
    def district_sort_key(r):
        try:
            d = int(r["district"])
        except (ValueError, TypeError):
            d = -1
        return (r["state"], d)

    rows.sort(key=district_sort_key)

    fieldnames = [
        "bioguide_id",
        "full_name",
        "state",
        "district",
        "party",
        "gender",
        "birthday",
        "age_at_vote",
        "first_house_term_start",
        "house_tenure_years",
        "total_terms",
    ]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # --- Sanity checks / report ---
    n = len(rows)
    print(f"Total House members written: {n}")
    if not (429 <= n <= 435):
        print(f"WARNING: expected roughly 429-435 rows, got {n}")

    if missing_birthday:
        print(f"Missing birthday for {len(missing_birthday)} member(s):")
        for bid, nm in missing_birthday:
            print(f"  - {bid}: {nm}")
    else:
        print("No missing birthdays.")

    ages = [r["age_at_vote"] for r in rows if r["age_at_vote"] != ""]
    if ages:
        print(f"Min age: {min(ages)}")
        print(f"Max age: {max(ages)}")
        print(f"Mean age: {round(sum(ages) / len(ages), 1)}")


if __name__ == "__main__":
    main()
