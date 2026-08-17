#!/usr/bin/env python3
"""Build deterministic reactor, event, and capacity views from stored PRIS snapshots."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

EVENT_FIELDS = (
    ("construction_start", "construction_date"),
    ("first_criticality", "first_criticality_date"),
    ("first_grid_connection", "first_grid_connection"),
    ("commercial_operation", "commercial_operation_date"),
    ("suspended_operation", "latest_suspended_operation_date"),
    ("restart_operation", "latest_restart_operation_date"),
    ("permanent_shutdown", "shutdown_date"),
)


def load_latest(root: Path) -> tuple[Path, dict]:
    candidates = []
    for path in root.glob("*/*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        candidates.append((str(payload["retrieved_at"]), path, payload))
    if not candidates:
        raise ValueError("no persisted PRIS reactor snapshots found")
    _, path, payload = max(candidates, key=lambda item: item[0])
    return path, payload


def capacity(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def build_events(reactors: list[dict], observed_at: str) -> list[dict]:
    events = []
    for reactor in reactors:
        for event_type, field in EVENT_FIELDS:
            value = reactor.get(field)
            if not value:
                continue
            events.append(
                {
                    "reactor_id": reactor["reactor_id"],
                    "reactor_name": reactor["name"],
                    "country_code": reactor["country_code"],
                    "country_name": reactor["country_name"],
                    "event_type": event_type,
                    "event_at": str(value),
                    "source_field": field,
                    "observed_at": observed_at,
                    "source_url": reactor["source_url"],
                    "source_sha256": reactor["source_sha256"],
                }
            )
    events.sort(key=lambda row: (row["event_at"], row["reactor_id"], row["event_type"]))
    return events


def aggregate(reactors: list[dict], key: str) -> list[dict]:
    groups: dict[str, dict[str, float]] = defaultdict(lambda: {"reactor_count": 0, "net_capacity_mw": 0.0})
    for reactor in reactors:
        group = str(reactor.get(key) or "Unknown")
        groups[group]["reactor_count"] += 1
        groups[group]["net_capacity_mw"] += capacity(reactor.get("net_electrical_capacity_mw"))
    return [
        {
            key: name,
            "reactor_count": int(values["reactor_count"]),
            "net_electrical_capacity_mw": values["net_capacity_mw"],
        }
        for name, values in sorted(groups.items())
    ]


def build(snapshot_root: Path, output_dir: Path) -> None:
    snapshot_path, source = load_latest(snapshot_root)
    observed_at = str(source["retrieved_at"])
    reactors = []
    for row in source["reactors"]:
        normalized = dict(row)
        normalized["observed_at"] = observed_at
        reactors.append(normalized)
    reactors.sort(key=lambda row: (str(row["country_code"]), str(row["name"]), row["reactor_id"]))

    events = build_events(reactors, observed_at)
    events_2026 = [row for row in events if row["event_at"].startswith("2026-")]
    statuses = aggregate(reactors, "status")
    countries = aggregate(reactors, "country_code")
    reactor_types = aggregate(reactors, "type_code")

    status_map = {row["status"]: row for row in statuses}
    capacity_view = {
        "observed_at": observed_at,
        "operating": status_map.get("Operational", {"reactor_count": 0, "net_electrical_capacity_mw": 0.0}),
        "suspended_operation": status_map.get("Suspended Operation", {"reactor_count": 0, "net_electrical_capacity_mw": 0.0}),
        "under_construction": status_map.get("Under Construction", {"reactor_count": 0, "net_electrical_capacity_mw": 0.0}),
        "permanent_shutdown": status_map.get("Permanent Shutdown", {"reactor_count": 0, "net_electrical_capacity_mw": 0.0}),
    }

    outputs = {
        "reactors.json": {
            "schema_version": 1,
            "publisher": source["publisher"],
            "observed_at": observed_at,
            "source_snapshot": str(snapshot_path),
            "reactor_count": len(reactors),
            "reactors": reactors,
        },
        "status-events.json": {
            "schema_version": 1,
            "publisher": source["publisher"],
            "observed_at": observed_at,
            "event_count": len(events),
            "events": events,
        },
        "status-events-2026.json": {
            "schema_version": 1,
            "publisher": source["publisher"],
            "observed_at": observed_at,
            "event_count": len(events_2026),
            "events": events_2026,
        },
        "capacity.json": capacity_view,
        "by-status.json": {"observed_at": observed_at, "groups": statuses},
        "by-country.json": {"observed_at": observed_at, "groups": countries},
        "by-reactor-type.json": {"observed_at": observed_at, "groups": reactor_types},
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-dir", type=Path, default=Path("data/official/pris-reactors"))
    parser.add_argument("--output-dir", type=Path, default=Path("api/v1/nuclear-power"))
    args = parser.parse_args()
    build(args.snapshot_dir, args.output_dir)


if __name__ == "__main__":
    main()
