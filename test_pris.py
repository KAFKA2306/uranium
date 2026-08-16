from src.collect_pris import parse_reactors


def test_parse_pris_reactor_table():
    html = b'''<table><tr><th>Name</th><th>Type</th><th>Status</th><th>Location</th><th>Reference Unit Power [MW]</th><th>Gross Electrical Capacity [MW]</th><th>First Grid Connection</th></tr><tr><td>TEST-1</td><td>PWR</td><td>Operational</td><td>TEST SITE</td><td>1000</td><td>1100</td><td>2026-01-02</td></tr></table>'''
    rows = parse_reactors(html, "XX")
    assert rows == [{
        "country_code": "XX",
        "name": "TEST-1",
        "reactor_type": "PWR",
        "status": "Operational",
        "location": "TEST SITE",
        "reference_unit_power_mw": 1000,
        "gross_electrical_capacity_mw": 1100,
        "first_grid_connection": "2026-01-02",
    }]
