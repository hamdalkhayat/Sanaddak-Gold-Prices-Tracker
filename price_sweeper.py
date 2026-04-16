"""
Ta3weem Price Sweeper
Fetches gold and USD/EGP exchange prices from ta3weem.com
Appends results to price_history.json.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://ta3weem.com/en/"
HISTORY_FILE = Path(__file__).parent / "price_history.json"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
}

TARGETS = {
    "US Dollar (USD)",
    "21K Gold",
    "24K Gold",
    "Gold Pound",
}


def fetch_prices() -> dict:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    prices = {}
    for card in soup.find_all("a", href=True):
        h3 = card.find("h3", class_="text-xs")
        price_span = card.find("span", class_="font-medium")
        if not (h3 and price_span):
            continue
        label = h3.get_text(strip=True)
        if label not in TARGETS:
            continue
        price_text = price_span.get_text(strip=True)
        try:
            value = float(price_text.replace(",", ""))
        except ValueError:
            value = price_text
        prices[label] = {"display": price_text, "value": value}

    for tag in soup.find_all(string=re.compile(r"Last refreshed on", re.I)):
        prices["_page_timestamp"] = tag.strip()
        break

    return prices


def load_history() -> list:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: list) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def print_summary(entry: dict) -> None:
    prices = entry["prices"]
    page_ts = prices.get("_page_timestamp", "N/A")
    print("=" * 50)
    print(f"  Ta3weem Prices — {entry['fetched_at']}")
    print(f"  Site: {page_ts}")
    print("=" * 50)
    for label in ["US Dollar (USD)", "21K Gold", "24K Gold", "Gold Pound"]:
        if label in prices:
            p = prices[label]
            unit = "EGP/USD" if "Dollar" in label else "EGP/gram" if "Gold Pound" not in label else "EGP"
            print(f"  {label:<20} {p['display']:>12}  {unit}")
    print("=" * 50)


def run() -> None:
    print(f"Fetching prices from {URL} ...")
    prices = fetch_prices()

    if not prices:
        print("ERROR: No prices found. The page structure may have changed.")
        sys.exit(1)

    entry = {
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "prices": prices,
    }

    history = load_history()
    history.append(entry)
    save_history(history)

    print_summary(entry)
    print(f"\nAppended to: {HISTORY_FILE}")


if __name__ == "__main__":
    run()
