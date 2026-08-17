import json
from pathlib import Path

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
        }
    )
    assert row["reactor_id"] == 652
    assert row["name"] == "ANO-1"
    assert row["status"] == "Operational"
    assert row["type_code"] == "PWR"
    assert row["gross_electrical_capacity_mw"] == 903
    assert row["net_electrical_capacity_mw"] == 836
    assert row["first_grid_connection"] == "1974-08-17T00:00:00"
    assert row["shutdown_date"] is None


def test_japan_status_snapshot():
    path = ROOT / "data" / "official" / "pris-japan-status-2026-08-17.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["publisher"] == "IAEA Power Reactor Information System (PRIS)"
    assert payload["country_code"] == "JP"
    assert payload["source"] == {
        "url": "https://pris-stats.iaea.org/reactor/reactors-by-code/JP",
        "sha256": "8d9b07785793373c44b4d6a1cd7d7f999f1d1e95cd40a6423f623a09ebedcdc8",
        "reactor_count": 62,
    }

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
    assert sum(count for count, _ in by_status.values()) == 62
