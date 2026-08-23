# nuclear-power — IAEA PRIS reactor evidence

[![IAEA PRIS source](https://github.com/KAFKA2306/uranium/actions/workflows/pris-source.yml/badge.svg)](https://github.com/KAFKA2306/uranium/actions/workflows/pris-source.yml)
[![Deploy Pages](https://github.com/KAFKA2306/uranium/actions/workflows/pages.yml/badge.svg)](https://github.com/KAFKA2306/uranium/actions/workflows/pages.yml)

IAEA Power Reactor Information System (PRIS) の公開一次情報から、世界の原子炉、設備容量、主要milestoneとstatus eventを継続取得します。現在のGitHub repository名は `uranium`、正準責務は `nuclear-power` です。

## Public dashboard

- Daily entry point: https://kafka2306.github.io/uranium/
- latest verified PRIS milestone
- Operational / Under Construction / Suspended Operationを別state・別capacityとして表示
- 2026 milestone timeline
- country reactor inventory
- source observation timeとIAEA PRIS evidenceへの直接link

原子力fleetは毎日変化するとは限りません。Pagesは架空のdaily deltaを作らず、**latest verified event** とcurrent observed fleetを表示します。

## Primary source

- PRIS Analytics: https://pris-stats.iaea.org/
- About PRIS: https://pris.iaea.org/PRIS/About.aspx
- country registry: https://pris-stats.iaea.org/country/countries/
- reactor by country: `https://pris-stats.iaea.org/reactor/reactors-by-code/{countryCode}`

PRISはIAEA加盟国が指定したdata providerから収集されたreactor specification / status / performance informationをIAEAが維持するdatabaseです。

## Canonical outputs

- [`api/v1/nuclear-power/reactors.json`](api/v1/nuclear-power/reactors.json) — reactor master
- [`api/v1/nuclear-power/status-events.json`](api/v1/nuclear-power/status-events.json) — explicit milestone/event ledger
- [`api/v1/nuclear-power/status-events-2026.json`](api/v1/nuclear-power/status-events-2026.json) — 2026 events
- [`api/v1/nuclear-power/capacity.json`](api/v1/nuclear-power/capacity.json) — Operational / Suspended / Under Construction / Permanent Shutdown capacity
- [`api/v1/nuclear-power/by-status.json`](api/v1/nuclear-power/by-status.json)
- [`api/v1/nuclear-power/by-country.json`](api/v1/nuclear-power/by-country.json)
- [`api/v1/nuclear-power/by-reactor-type.json`](api/v1/nuclear-power/by-reactor-type.json)

Pagesはこれらをread-onlyで投影し、current valuesを別管理しません。

## Event contract

Event ledgerはPRISが明示する次の日付だけを使用します。

- construction start
- first criticality
- first grid connection
- commercial operation
- latest suspended operation
- latest restart operation
- permanent shutdown

current statusから過去statusを逆算しません。各eventはreactor identity、event date、observed_at、source URL、source SHA-256を保持します。

## Data contract

- IAEA PRISをfactのcanonical sourceとする
- reactor countとcapacityを混同しない
- capacityとgenerationを同じmetricとして扱わない
- Operational / Suspended / Under Construction / Permanent Shutdownを分離する
- planned projectをconstruction-start済みreactorへ昇格させない
- sourceにないgeneration / outage seriesを推測で補完しない
- source snapshotを上書きせず、source changeを履歴として保持する
- milestone/status eventはPRISのexplicit dateだけから生成する
- derived viewは保存済みraw snapshotから再生成可能にする

## Collection and verification

```bash
python -m unittest -v test_pris
python src/collect_pris.py --country US --country JP --output /tmp/pris-reactors.json
```

全世界取得とview生成:

```bash
python src/collect_pris.py
python src/build_pris_views.py
```

- `IAEA PRIS source` は週次でcountry registryを列挙し、source stateが変わった場合だけraw snapshotとderived viewsをcommitします。
- `Deploy Pages` はPRでcanonical state boundaryとdashboard JSを検証し、mainではcanonical APIをdeploy後に`deployment.json`のexact commit SHAまで照合します。

本repositoryのデータは投資助言ではありません。
