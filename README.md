# nuclear-power — IAEA PRIS reactor evidence

[![IAEA PRIS source](https://github.com/KAFKA2306/uranium/actions/workflows/pris-source.yml/badge.svg)](https://github.com/KAFKA2306/uranium/actions/workflows/pris-source.yml)

IAEA Power Reactor Information System (PRIS) の公開一次情報から、世界の原子炉、設備容量、主要milestoneとstatus eventを継続取得するrepositoryです。

現在のGitHub repository名は `uranium` ですが、正準責務は `nuclear-power` です。旧2024年ticker snapshot・Alpha Vantage・Yahoo価格取得scriptは正準責務と無関係になったため削除しました。

## 一次情報

- PRIS Analytics: https://pris-stats.iaea.org/
- About PRIS: https://pris.iaea.org/PRIS/About.aspx
- country registry: https://pris-stats.iaea.org/country/countries/
- reactor by country: `https://pris-stats.iaea.org/reactor/reactors-by-code/{countryCode}`

PRISはIAEA加盟国が指定したdata providerから収集された原子炉仕様・status・performance情報をIAEAが維持するデータベースです。

## 正準データ

all-country raw snapshot:

```text
data/official/pris-reactors/YYYY-MM-DD/<source-fingerprint>.json
```

country registryと各country reactor responseのSHA-256からfingerprintを作り、同じsource stateは重複保存しません。sourceが変わった場合も以前のsnapshotを上書きしません。

reactor rowは最低限、次を保持します。

- reactor / site / country identity
- reactor type / model / status
- thermal / gross / net / design net capacity
- construction / first criticality / first grid connection / commercial operation / shutdown
- latest suspended operation / restart
- operator / owner / supplier
- source URL / source SHA-256

## 再利用可能なview

workflowがraw snapshotから次を決定的に生成します。

- [`api/v1/nuclear-power/reactors.json`](api/v1/nuclear-power/reactors.json) — reactor master
- [`api/v1/nuclear-power/status-events.json`](api/v1/nuclear-power/status-events.json) — PRISの明示日付から作るmilestone/event ledger
- [`api/v1/nuclear-power/status-events-2026.json`](api/v1/nuclear-power/status-events-2026.json) — 2026年event
- [`api/v1/nuclear-power/capacity.json`](api/v1/nuclear-power/capacity.json) — Operational / Suspended / Under Construction / Permanent Shutdownを分離したcapacity view
- [`api/v1/nuclear-power/by-status.json`](api/v1/nuclear-power/by-status.json)
- [`api/v1/nuclear-power/by-country.json`](api/v1/nuclear-power/by-country.json)
- [`api/v1/nuclear-power/by-reactor-type.json`](api/v1/nuclear-power/by-reactor-type.json)

`capacity` と `generation` は同じmetricとして扱いません。planned projectをconstruction-start済みreactorとして補完しません。

## status event

event ledgerは次のPRIS fieldが明示する日付だけを使用します。

- construction start
- first criticality
- first grid connection
- commercial operation
- latest suspended operation
- latest restart operation
- permanent shutdown

現在statusから過去statusを逆算しません。各eventにreactor identity、observed_at、source URL、source SHA-256を保持します。

## generation / outage

PRISはenergy production、energy loss、outage、performance historyを保有すると公式に説明しています。一方、このrepositoryが現在利用している公開reactor JSON endpointにはそのseriesが含まれません。取得できないfieldを推測で補完せず、公開かつ機械取得可能なIAEA endpointを確認できた場合だけ同じevidence contractへ追加します。

## 自動取得

[`IAEA PRIS source`](https://github.com/KAFKA2306/uranium/actions/workflows/pris-source.yml) は週次でcountry registryにある全countryを列挙してreactor listを取得し、raw snapshotとderived viewに変化がある場合だけcommitします。

Pull RequestではUS / Japanのlive APIを実取得し、normalizationとview生成はunit testで検証します。

```bash
python -m unittest -v test_pris
python src/collect_pris.py --country US --country JP --output /tmp/pris-reactors.json
```

全世界取得:

```bash
python src/collect_pris.py
python src/build_pris_views.py
```

## データ契約

- IAEA PRISをfactの正準sourceとする
- status / capacity / generationを別metricにする
- source取得不可fieldを推測しない
- current snapshotを上書きせずsource changeを残す
- milestone/status eventはPRISの明示日付だけから生成する
- operating / suspended / under construction / permanent shutdownを別集計する
- derived viewは保存済みraw snapshotから再生成する

本repositoryのデータは投資助言ではありません。
