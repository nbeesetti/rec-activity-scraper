import os
import sys
import csv
import re
import requests
from bs4 import BeautifulSoup
import certifi
from datetime import datetime
from zoneinfo import ZoneInfo


URL = "https://www.asi.calpoly.edu/asi-current-space-activity/"
verify_arg = True
OUTPUT_CSV = "rec_data.csv"


def main():
    print(f"Fetching: {URL}")
    ca_bundle = os.getenv("REQUESTS_CA_BUNDLE") or certifi.where()
    print(f"TLS CA bundle: {ca_bundle}")

    try:
        r = requests.get(
            URL,
            timeout=15,
            verify=ca_bundle,
        )
        print("Status:", r.status_code)
        r.raise_for_status()

    except requests.exceptions.SSLError as e:
        print("\nTLS/SSL error!")
        raise

    soup = BeautifulSoup(r.text, "lxml")
    rooms = []

    print("Page title:", soup.title.get_text(strip=True))

    for block in soup.select("div.splitContent__outer"):
        h2 = block.select_one("h2.splitContent__title")
        bar = block.select_one(".occupancyBar__progressWrapper")

        if not (h2 and bar):
            continue

        name = h2.get_text(strip=True)

        style = bar.get("style", "")
        m = re.search(r"width:\s*([0-9.]+)\s*%", style)
        pct = m.group(1) if m else None

        if "Exercise" in name:
            rooms.append(
                {
                    "name": name,
                    "percent": float(pct) if pct else None,
                }
            )

    for r in rooms:
        print(f"{r['name']}: {r['percent']}")

    timestamp = datetime.now(ZoneInfo("America/Los_Angeles")).isoformat()

    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "room_name", "percent"])

    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in rooms:
            w.writerow([timestamp, r["name"], r["percent"]])

    print(f"Wrote {len(rooms)} rows to {OUTPUT_CSV} at {timestamp}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
