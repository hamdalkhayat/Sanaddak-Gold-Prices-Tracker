"""
Generates README.md from price_history.json with latest prices and full history table.
"""

import json
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "price_history.json"
README_FILE = Path(__file__).parent / "README.md"

LABELS = ["US Dollar (USD)", "21K Gold", "24K Gold", "Gold Pound"]
UNITS  = ["EGP / USD", "EGP / gram", "EGP / gram", "EGP"]


def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def render(history: list) -> str:
    if not history:
        return "# Sanaddak Gold Prices Tracker\n\nNo data yet.\n"

    latest = history[-1]
    prices = latest["prices"]
    fetched_at = latest["fetched_at"]
    page_ts = prices.get("_page_timestamp", "")

    lines = []

    # Header
    lines.append("# Sanaddak Gold Prices Tracker")
    lines.append("")
    lines.append(f"> Prices sourced from [ta3weem.com](https://ta3weem.com/en/)  ")
    lines.append(f"> Updated automatically 3× daily (09:00, 12:00, 15:00 Cairo time)")
    lines.append("")

    # Latest prices
    lines.append("## Latest Prices")
    lines.append("")
    lines.append(f"**Fetched at:** {fetched_at}  ")
    if page_ts:
        lines.append(f"**Site timestamp:** {page_ts}  ")
    lines.append("")
    lines.append("| Asset | Price | Unit |")
    lines.append("|-------|------:|------|")
    for label, unit in zip(LABELS, UNITS):
        if label in prices:
            display = prices[label]["display"]
            lines.append(f"| {label} | **{display}** | {unit} |")
    lines.append("")

    # Full history
    lines.append("## Price History")
    lines.append("")
    lines.append("| Fetched At | USD/EGP | 21K Gold | 24K Gold | Gold Pound |")
    lines.append("|------------|--------:|---------:|---------:|-----------:|")

    for entry in reversed(history):
        p = entry["prices"]
        ts = entry["fetched_at"]
        usd   = p.get("US Dollar (USD)", {}).get("display", "-")
        g21   = p.get("21K Gold",        {}).get("display", "-")
        g24   = p.get("24K Gold",        {}).get("display", "-")
        gpound = p.get("Gold Pound",     {}).get("display", "-")
        lines.append(f"| {ts} | {usd} | {g21} | {g24} | {gpound} |")

    lines.append("")
    return "\n".join(lines)


def run() -> None:
    history = load_history()
    readme = render(history)
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"README.md generated with {len(history)} entries.")


if __name__ == "__main__":
    run()
