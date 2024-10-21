import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time

# Load API key from .env file
load_dotenv()

def get_api_key():
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        api_key = input("Alpha Vantage APIキーを入力してください: ")
        with open('.env', 'a') as f:
            f.write(f"\nALPHA_VANTAGE_API_KEY={api_key}")
    return api_key

def fetch_vantage(api_key, tickers):
    base_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}"
    valid_tickers, invalid_tickers = [], []
    for i, (category, symbols) in enumerate(tickers.items()):
        for ticker, company in symbols.items():
            if i > 0 and i % 5 == 0:
                print("API利用制限のため60秒間待機しています...")
                time.sleep(60)
            try:
                url = base_url.format(ticker, api_key)
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if "Error Message" in data:
                    raise ValueError(data["Error Message"])
                valid_tickers.append((ticker, category))
                print(f"{ticker}のデータを取得しました ({company})")
                # Save data to CSV
                folder_path = os.path.join('vantage', category)
                os.makedirs(folder_path, exist_ok=True)
                file_path = os.path.join(folder_path, f"{ticker}.csv")
                pd.DataFrame(data['Time Series (Daily)']).T.to_csv(file_path)
                print(f"{ticker}のデータを保存しました: {file_path}")
            except Exception as e:
                print(f"{ticker}のデータ取得中にエラーが発生しました: {e}")
                invalid_tickers.append((ticker, category))
    return valid_tickers, invalid_tickers

def main():
    api_key = get_api_key()
    tickers = {
        'Small Modular Reactor (SMR) developers': {
            'SMR': 'NuScale Power',
            'OKLO': 'Oklo'
        },
        'Data Center Operators': {
            'AMZN': 'Amazon.com Inc',
            'GOOGL': 'Alphabet Inc (Google)',
            'MSFT': 'Microsoft Corporation'
        },
        'Carbon-Free Energy Producers': {
            'CEG': 'Constellation Energy Corp',
            'D': 'Dominion Energy',
            'TLN': 'Talen Energy Corp'
        },
        'Semiconductor/Chip Manufacturers': {
            'NVDA': 'NVIDIA Corporation'
        },
        'Energy/Sector ETFs': {
            'SOXX': 'iShares Semiconductor ETF',
            'VDE': 'Vanguard Energy ETF',
            'XLE': 'Energy Select Sector SPDR Fund',
            'ICLN': 'iShares Global Clean Energy ETF',
            'URA': 'Global X Uranium ETF',
            'NLR': 'VanEck Uranium+Nuclear Energy ETF'
        },
        'Renewable Energy Companies': {
            'GEV': 'Gevo Inc'
        },
        'Nuclear Technology Companies': {
            'BWXT': 'BWX Technologies Inc'
        },
        'Uranium Companies': {
            'CCJ': 'Cameco Corporation',
            'UEC': 'Uranium Energy Corp'
        },
        'Japanese Electric Power Companies (Nuclear Operators)': {
            '9501.T': 'Tokyo Electric Power Company Holdings',
            '9503.T': 'Kansai Electric Power Co., Inc.',
            '9508.T': 'Kyushu Electric Power Company, Incorporated',
            '9507.T': 'Shikoku Electric Power Company, Incorporated',
            '9504.T': 'Chugoku Electric Power Company, Incorporated',
            '9509.T': 'Hokkaido Electric Power Company, Incorporated'
        }
    }
    
    valid_tickers, invalid_tickers = fetch_vantage(api_key, tickers)
    print(f"有効なティッカー数: {len(valid_tickers)}")
    print(f"無効なティッカー: {invalid_tickers}")
    print("注意: フリープランでは1日25リクエストまでの制限があります。")

if __name__ == "__main__":
    main()
