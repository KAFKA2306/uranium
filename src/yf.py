import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

# Ticker definitions
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

# Convert to DataFrame
df = pd.DataFrame.from_dict(tickers, orient='index').T

# Save the DataFrame as a CSV file
df.to_csv('_ticker_list.csv', index=False)
print("The  ticker list has been saved as '_ticker_list.csv' in the current working directory.")

# Data Retrieval and Analysis
end_date = datetime.now()
start_date = end_date - timedelta(days=365*3)  # 3 years of data

def get_data(ticker_list):
    tickers_str = ','.join(ticker_list)
    data = yf.download(tickers_str, start=start_date, end=end_date)['Adj Close']
    return data.dropna(axis=1)

all_tickers = [ticker for sector_tickers in tickers.values() for ticker in sector_tickers]
df = get_data(all_tickers)
valid_tickers = df.columns.tolist()

print(f"Number of tickers retrieved: {len(valid_tickers)}")
print(f"Tickers not retrieved: {set(all_tickers) - set(valid_tickers)}")

# Performance Calculation
performance = df.pct_change().cumsum()

# Sector-wise Performance
sector_performance = {}
for sector, sector_tickers in tickers.items():
    valid_sector_tickers = [ticker for ticker in sector_tickers if ticker in valid_tickers]
    if valid_sector_tickers:
        sector_performance[sector] = performance[valid_sector_tickers].mean(axis=1)

# Output Results
print("\nAverage returns per sector:")
for sector, perf in sector_performance.items():
    print(f"{sector}: {perf.iloc[-1]:.2%}")

if len(valid_tickers) > 1:
    print("\nTop 5 pairs with highest correlation:")
    corr_pairs = []
    for i in range(len(valid_tickers)):
        for j in range(i+1, len(valid_tickers)):
            corr_pairs.append((valid_tickers[i], valid_tickers[j], performance[valid_tickers[i]].corr(performance[valid_tickers[j]])))

    corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for pair in corr_pairs[:5]:
        print(f"{pair[0]} - {pair[1]}: {pair[2]:.2f}")
else:
    print("\nCorrelation analysis skipped as there is only one valid ticker.")

if len(valid_tickers) > 0:
    print("\nTop 5 tickers by volatility:")
    volatility = df.pct_change().std() * np.sqrt(252)  # Annualized Volatility
    for ticker, vol in volatility.nlargest(5).items():
        print(f"{ticker}: {vol:.2%}")
else:
    print("\nVolatility analysis skipped as there are no valid tickers.")