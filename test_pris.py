import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.build_pris_views import build
from src.collect_pris import normalize_reactor

ROOT = Path(__file__).resolve().parent


def test_normalize_current_pris_reactor_record():
    row = normalize_reactor(
        {
            "id": 652,
            "countryCode": "US",
            "countryName": "United States of America",
            "unitName": "ANO-1",
            "alternateName": "Arkansas Nuclear One, Unit 1",
            "siteId": 309,
            "siteName": "ARKANSAS ONE",
            "typeName": "Pressurized Light-Water-Moderated and Cooled Reactor",
            "typeCode": "PWR",
            "statusName": "Operational",
            "statusCode": "1O",
            "model": "B&W LLP (DRYAMB)",
            "thermalPower": 2568,
            "grossElectricalCapacity": 903,
            "netElectricalCapacity": 836,
            "designNetElectricalCapacity": 850,
            "constructionDate": "1968-10-01T00:00:00",
            "criticalityDate": "1974-08-06T00:00:00",
            "gridDate": "1974-08-17T00:00:00",
            "commercialDate": "1974-12-19T00:00:00",
            "shutdownDate": None,
            "operatorName": "Entergy Nuclear Operations, Inc.",
            "ownerName": "ENTERGY ARKANSAS, INC.",
            "reactorSupplierName": "BABCOCK & WILCOX CO.",
            "turbineSupplierName": "WESTINGHOUSE ELECTRIC CORPORATION",
            "informationStatusCode": "PUB",
            "informationStatusDescription": "Published",
        },
        "https://pris-stats.iaea.org/reactor/reactors-by-code/US",
        "a" * 64,
    )
    assert row["reactor_id"] == 652
    assert row["name"] == "ANO-1"
    assert row["status"] == "Operational"
    assert row["type_code"] == "PWR"
    assert row["gross_electrical_capacity_mw"] == 903
    assert row["net_electrical_capacity_mw"] == 836
    assert row["first_grid_connection"] == "1974-08-17T00:00:00"
    assert row["shutdown_date"] is None
    assert row["source_sha256"] == "a" * 64


def test_japan_status_snapshot():
    path = ROOT / "data" / "official" / "pris-japan-status-2026-08-17.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["publisher"] == "IAEA Power Reactor Information System (PRIS)"
    assert payload["country_code"] == "JP"
    by_status = {
        item["status"]: (item["reactor_count"], item["net_electrical_capacity_mw"])
        for item in payload["status_aggregates"]
    }
    assert by_status == {
        "Operational": (14, 12631),
        "Suspended Operation": (19, 19048),
        "Under Construction": (2, 2653),
        "Permanent Shutdown": (27, 17119),
    }


def test_views_keep_explicit_2026_events_and_separate_capacity_statuses():
    reactor = {
        "reactor_id": 1,
        "country_code": "XX",
        "country_name": "Example",
        "name": "EXAMPLE-1",
        "type_code": "PWR",
        "status": "Under Construction",
        "net_electrical_capacity_mw": 1000,
        "construction_date": "2026-01-16T00:00:00",
        "first_criticality_date": None,
        "first_grid_connection": None,
        "commercial_operation_date": None,
        "latest_suspended_operation_date": None,
        "latest_restart_operation_date": None,
        "shutdown_date": None,
        "source_url": "https://pris-stats.iaea.org/reactor/reactors-by-code/XX",
        "source_sha256": "b" * 64,
    }
    source = {
        "schema_version": 3,
        "publisher": "IAEA Power Reactor Information System (PRIS)",
        "retrieved_at": "2026-08-17T10:00:00+00:00",
        "country_count": 1,
        "reactor_count": 1,
        "sources": [],
        "reactors": [reactor],
    }
    with TemporaryDirectory() as tmp:
        root = Path(tmp) / "snapshots"
        path = root / "2026-08-17" / "fixture.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(source), encoding="utf-8")
        output = Path(tmp) / "api"
        build(root, output)
        events = json.loads((output / "status-events-2026.json").read_text())
        capacity = json.loads((output / "capacity.json").read_text())
        assert events["event_count"] == 1
        assert events["events"][0]["event_type"] == "construction_start"
        assert events["events"][0]["source_url"].startswith("https://pris-stats.iaea.org/")
        assert capacity["operating"]["net_electrical_capacity_mw"] == 0.0
        assert capacity["under_construction"]["net_electrical_capacity_mw"] == 1000.0


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test in (
        test_normalize_current_pris_reactor_record,
        test_japan_status_snapshot,
        test_views_keep_explicit_2026_events_and_separate_capacity_statuses,
    ):
        suite.addTest(unittest.FunctionTestCase(test))
    return suite
