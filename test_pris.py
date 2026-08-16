from src.collect_pris import normalize_reactor


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
