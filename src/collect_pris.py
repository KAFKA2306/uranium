#!/usr/bin/env python3
"""Collect reactor-level status from the public IAEA PRIS JSON API."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://pris-stats.iaea.org"
COUNTRIES_PATH = "/country/countries/"
REACTORS_PATH = "/reactor/reactors-by-code/{country_code}"


def fetch_json(path: str) -> tuple[dict[str, object], bytes, str]:
    url = f"{BASE}{path}"
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 nuclear-power/1.0 github.com/KAFKA2306/uranium",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=60) as response:
        raw = response.read()
    return json.loads(raw), raw, url


def normalize_reactor(row: dict[str, object]) -> dict[str, object]:
    return {
        "reactor_id": row.get("id"),
        "country_code": row.get("countryCode"),
        "country_name": row.get("countryName"),
        "name": row.get("unitName"),
        "alternate_name": row.get("alternateName"),
        "site_id": row.get("siteId"),
        "site_name": row.get("siteName"),
        "reactor_type": row.get("typeName"),
        "type_code": row.get("typeCode"),
        "status": row.get("statusName"),
        "status_code": row.get("statusCode"),
        "model": row.get("model"),
        "thermal_power_mw": row.get("thermalPower"),
        "gross_electrical_capacity_mw": row.get("grossElectricalCapacity"),
        "net_electrical_capacity_mw": row.get("netElectricalCapacity"),
        "design_net_electrical_capacity_mw": row.get("designNetElectricalCapacity"),
        "construction_date": row.get("constructionDate"),
        "first_criticality_date": row.get("criticalityDate"),
        "first_grid_connection": row.get("gridDate"),
        "commercial_operation_date": row.get("commercialDate"),
        "shutdown_date": row.get("shutdownDate"),
        "latest_suspended_operation_date": row.get("latestSuspendedOperationsDate"),
        "latest_restart_operation_date": row.get("latestRestartOperationsDate"),
        "operator": row.get("operatorName"),
        "owner": row.get("ownerName"),
        "reactor_supplier": row.get("reactorSupplierName"),
        "turbine_supplier": row.get("turbineSupplierName"),
        "information_status_code": row.get("informationStatusCode"),
        "information_status": row.get("informationStatusDescription"),
    }


def collect(country_codes: list[str]) -> dict[str, object]:
    countries_payload, countries_raw, countries_url = fetch_json(COUNTRIES_PATH)
    countries = countries_payload.get("items") or []
    if not isinstance(countries, list):
        raise ValueError("PRIS countries response has no items list")

    valid_codes = {
        str(row.get("countryCode", "")).upper()
        for row in countries
        if isinstance(row, dict) and row.get("countryCode")
    }
    requested = [code.upper() for code in country_codes]
    unknown = sorted(set(requested) - valid_codes)
    if unknown:
        raise ValueError(f"unknown PRIS country codes: {unknown}")

    sources: list[dict[str, object]] = [
        {
            "type": "country_registry",
            "url": countries_url,
            "sha256": hashlib.sha256(countries_raw).hexdigest(),
            "country_count": len(countries),
        }
    ]
    reactors: list[dict[str, object]] = []

    for code in requested:
        path = REACTORS_PATH.format(country_code=code)
        payload, raw, url = fetch_json(path)
        rows = payload.get("items") or []
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"PRIS returned no reactors for {code}")
        normalized = [
            normalize_reactor(row)
            for row in rows
            if isinstance(row, dict)
        ]
        if not normalized:
            raise ValueError(f"PRIS returned no valid reactor records for {code}")
        reactors.extend(normalized)
        sources.append(
            {
                "type": "reactors_by_country",
                "country_code": code,
                "url": url,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "reactor_count": len(normalized),
            }
        )

    return {
        "schema_version": 2,
        "publisher": "IAEA Power Reactor Information System (PRIS)",
        "retrieved_at": datetime.now(UTC).isoformat(),
        "sources": sources,
        "reactors": reactors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--country",
        action="append",
        dest="countries",
        required=True,
        help="PRIS country code, e.g. US, CN, JP",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/pris-reactors.json"),
    )
    args = parser.parse_args()
    payload = collect(args.countries)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(payload['reactors'])} reactors -> {args.output}")


if __name__ == "__main__":
    main()
