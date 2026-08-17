# uranium — ウラン・原子力関連銘柄の2024年研究snapshot

[![IAEA PRIS source](https://github.com/KAFKA2306/uranium/actions/workflows/pris-source.yml/badge.svg)](https://github.com/KAFKA2306/uranium/actions/workflows/pris-source.yml)

> **状態: 過去snapshot / 自動更新なし**  
> このリポジトリは、2024年10月に作成されたウラン、原子力、SMR、データセンター電力需要に関係する銘柄候補と、価格取得・簡易分析scriptのsnapshotです。現在の銘柄構成、企業関係、価格、投資判断を示すものではありません。

## 目的

原子力発電・小型モジュール炉・ウラン・データセンター電力需要というテーマに関係し得る企業やETFを整理し、Alpha Vantageまたはyfinanceから価格を取得する試行を保存しています。

## 主なファイル

| ファイル | 内容 |
|---|---|
| `input/tickers.md` | 2024年時点の銘柄候補と短い説明 |
| `src/tickers.json` | Python辞書形式で書かれたticker分類。JSONではない |
| `_ticker_list.csv` | 分類ごとの企業名一覧 |
| `src/vantage.py` | Alpha Vantageの日次系列取得試行 |
| `src/yf.py` | yfinanceによる価格取得・簡易分析試行 |
| `.gitignore` | `.env`とAPI key fileの除外規則 |

## 現在の制約

### データとidentity

- ticker一覧の確認日は2024年10月で、継続更新されていない
- 企業説明・テーマ分類の出典URLと確認日が保存されていない
- ticker変更、上場廃止、社名変更、ETF名称変更を追跡していない
- `_ticker_list.csv`は企業名中心で、取引所、通貨、ISIN、正式名称、as-ofを保持していない
- `src/tickers.json`は有効なJSONではなくPython codeである

### 実行環境

- `requirements.txt`、`pyproject.toml`、lock fileがない
- testとCIがない
- API responseのschema・rate limit・取得失敗を十分に検証していない
- 生成済み価格dataの基準日、調整済み価格、通貨、timezoneを保証していない

### credential

`src/vantage.py`は環境変数`ALPHA_VANTAGE_API_KEY`を読み、未設定時には対話入力した値を`.env`へ追記します。

- `.env`をcommitしない
- API keyを標準出力、Notebook、CSVへ保存しない
- 共有端末では平文`.env`を使い回さない
- 漏えいしたkeyは削除だけでなく失効・再発行する

## 実行について

現在は依存versionとsample dataが固定されていないため、再現可能なquick startは提供しません。隔離環境でcodeを監査したうえで実行してください。

必要になる可能性があるlibrary:

```text
pandas
numpy
requests
python-dotenv
yfinance
```

これは正準な依存定義ではありません。再開時に`pyproject.toml`とlock fileへ移行します。

## 結果の解釈

- テーマへの掲載は企業価値、収益感応度、原子力事業比率を証明しない
- 株価相関は因果関係を証明しない
- ETFは指数、経費率、組入銘柄、rebalance規則が異なる
- 日本株と米国株を比較するときは通貨・取引時間・休日をそろえる
- 価格dataだけで事業実態、受注、規制、燃料供給を評価しない
- 本リポジトリは投資助言、売買推奨、将来収益の保証ではない

## 再開する場合の最小条件

1. 企業・ETFごとに正式名称、ticker、取引所、通貨、identifier、確認日を保存する
2. テーマ採用理由を一次情報URLとともに保存する
3. raw dataとderived metricsを分離する
4. 調整済み価格、配当、分割、timezoneを契約化する
5. API response validation、rate-limit処理、testを追加する
6. 取得日時とcode commit SHAを成果物へ保存する
7. 現行の正準金融基盤へ統合するか、独立維持の理由を明示する

## 関連する監査

- README監査Issue: https://github.com/KAFKA2306/uranium/issues/1
- 全repository README監査: https://github.com/KAFKA2306/com/issues/3

**README監査日:** 2026年8月5日