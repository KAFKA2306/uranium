#!/usr/bin/env python3
"""Collect reactor-level status from IAEA PRIS country pages."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://pris.iaea.org/PRIS/CountryStatistics/CountryDetails.aspx"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"td", "th"}:
            self.in_cell = True
            self.cell_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"td", "th"} and self.in_cell:
            value = " ".join(" ".join(self.cell_parts).split())
            self.row.append(value)
            self.in_cell = False
        elif tag == "tr":
            if self.row:
                self.rows.append(self.row)
            self.row = []


def fetch_country(code: str) -> tuple[bytes, str]:
    url = f"{BASE}?{urlencode({'current': code.upper()})}"
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/151 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(req, timeout=60) as response:
        return response.read(), url


def parse_reactors(html: bytes, country_code: str) -> list[dict[str, object]]:
    parser = TableParser()
    parser.feed(html.decode("utf-8", errors="replace"))
    header_index = None
    for i, row in enumerate(parser.rows):
        lowered = [cell.lower() for cell in row]
        if "name" in lowered and "type" in lowered and "status" in lowered and any("first grid connection" in cell for cell in lowered):
            header_index = i
            break
    if header_index is None:
        raise ValueError("PRIS reactor table header not found")

    header = [cell.lower() for cell in parser.rows[header_index]]
    name_i = header.index("name")
    type_i = header.index("type")
    status_i = header.index("status")
    location_i = header.index("location")
    ref_i = next(i for i, cell in enumerate(header) if "reference unit power" in cell)
    gross_i = next(i for i, cell in enumerate(header) if "gross electrical capacity" in cell)
    grid_i = next(i for i, cell in enumerate(header) if "first grid connection" in cell)
    max_i = max(name_i, type_i, status_i, location_i, ref_i, gross_i, grid_i)

    reactors = []
    for row in parser.rows[header_index + 1 :]:
        if len(row) <= max_i:
            continue
        name = row[name_i].strip()
        status = row[status_i].strip()
        if not name or status not in {"Operational", "Suspended Operation", "Under Construction", "Permanent Shutdown"}:
            continue

        def number(value: str) -> int | None:
            cleaned = re.sub(r"[^0-9.]", "", value)
            return int(float(cleaned)) if cleaned else None

        reactors.append({
            "country_code": country_code.upper(),
            "name": name,
            "reactor_type": row[type_i].strip(),
            "status": status,
            "location": row[location_i].strip(),
            "reference_unit_power_mw": number(row[ref_i]),
            "gross_electrical_capacity_mw": number(row[gross_i]),
            "first_grid_connection": row[grid_i].strip() or None,
        })
    if not reactors:
        raise ValueError("PRIS reactor table contained no recognized reactor rows")
    return reactors


def collect(country_codes: list[str]) -> dict[str, object]:
    sources = []
    reactors = []
    for code in country_codes:
        raw, url = fetch_country(code)
        country_rows = parse_reactors(raw, code)
        reactors.extend(country_rows)
        sources.append({"country_code": code.upper(), "url": url, "sha256": hashlib.sha256(raw).hexdigest(), "reactor_count": len(country_rows)})
    return {
        "schema_version": 1,
        "publisher": "IAEA Power Reactor Information System (PRIS)",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "reactors": reactors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", action="append", dest="countries", required=True, help="PRIS country code, e.g. US, CN, JP")
    parser.add_argument("--output", type=Path, default=Path("output/pris-reactors.json"))
    args = parser.parse_args()
    payload = collect(args.countries)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(payload['reactors'])} reactors -> {args.output}")


if __name__ == "__main__":
    main()
