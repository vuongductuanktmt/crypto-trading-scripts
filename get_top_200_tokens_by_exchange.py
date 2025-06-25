import pandas as pd
import json
import inquirer
import requests
import re
from datetime import datetime

# List of stablecoins to exclude
STABLECOINS = {
    'USDC', 'BUSD', 'TUSD', 'DAI', 'USDP', 'PAX', 'GUSD', 'HUSD', 'SUSD',
    'EURT', 'EURUSD', 'FDUSD', 'PYUSD', 'USDJ', 'UST', 'USTC'
}

# Function to check if base token is valid
def is_valid_base_token(token):
    """Check if base token is valid (minimum 2 characters, alphanumeric only, not a stablecoin)."""
    if not token or len(token) < 2:
        return False
    if token in STABLECOINS:
        return False
    if not re.match(r'^[A-Za-z0-9]+$', token):
        return False
    return True

# List of exchanges and their futures API endpoints
EXCHANGES = {
    'bybit': {
        'url': 'https://api.bybit.com/v5/market/tickers?category=linear',
        'symbol_key': 'symbol',
        'volume_key': 'volume24h',
        'symbol_format': lambda s: f"{s[:-4]}/USDT:USDT" if s.endswith('USDT') else None,
        'tickers_path': lambda data: data['result']['list']
    },
    'binance': {
        'url': 'https://fapi.binance.com/fapi/v1/ticker/24hr',
        'symbol_key': 'symbol',
        'volume_key': 'quoteVolume',
        'symbol_format': lambda s: f"{s[:-4]}/USDT:USDT" if s.endswith('USDT') else None,
        'tickers_path': lambda data: data
    },
    'okx': {
        'url': 'https://www.okx.com/api/v5/market/tickers?instType=SWAP',
        'symbol_key': 'instId',
        'volume_key': 'volCcy24h',
        'symbol_format': lambda s: f"{s.split('-')[0]}/USDT:USDT" if s.endswith('-USDT-SWAP') else None,
        'tickers_path': lambda data: data['data']
    },
    'kucoin': {
        'url': 'https://api-futures.kucoin.com/api/v1/contracts/active',
        'symbol_key': 'symbol',
        'volume_key': 'turnoverOf24h',
        'symbol_format': lambda s: f"{'BTC' if s.startswith('XBT') else s[:-5]}/USDT:USDT" if s.endswith('USDTM') else None,
        'tickers_path': lambda data: data['data']
    },
    'gateio': {
        'url': 'https://api.gateio.ws/api/v4/futures/usdt/tickers',
        'symbol_key': 'contract',
        'volume_key': 'volume_24h_quote',
        'symbol_format': lambda s: f"{s[:-5]}/USDT:USDT" if s.endswith('_USDT') else None,
        'tickers_path': lambda data: data
    }
}

def select_exchange():
    """Display menu to select an exchange."""
    questions = [
        inquirer.List('exchange',
                      message="Select an exchange:",
                      choices=list(EXCHANGES.keys()))
    ]
    answers = inquirer.prompt(questions)
    return answers['exchange']

def get_futures_tickers(exchange_name):
    """Fetch futures tickers data from the exchange."""
    try:
        config = EXCHANGES[exchange_name]
        url = config['url']
        symbol_key = config['symbol_key']
        volume_key = config['volume_key']
        symbol_format = config['symbol_format']
        tickers_path = config['tickers_path']
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        tickers = tickers_path(data)
        
        usdt_pairs = []
        invalid_pairs = []
        for ticker in tickers:
            symbol = ticker.get(symbol_key, '')
            ccxt_symbol = symbol_format(symbol)
            if ccxt_symbol:
                base_token = ccxt_symbol.split('/')[0]
                if not is_valid_base_token(base_token):
                    invalid_pairs.append((symbol, ccxt_symbol))
                    continue
                quote_volume = float(ticker.get(volume_key, 0))
                if quote_volume > 0:
                    usdt_pairs.append({
                        'symbol': ccxt_symbol,
                        'volume_24h': quote_volume
                    })
            else:
                invalid_pairs.append((symbol, ccxt_symbol))
        
        print(f"Found {len(usdt_pairs)} USDT Futures pairs on {exchange_name} (after excluding stablecoins and invalid pairs)")
        if invalid_pairs:
            print(f"Invalid pairs excluded: {invalid_pairs[:5]}")
        print(f"Sample data for {exchange_name}:", tickers[:5])
        return usdt_pairs
    except Exception as e:
        print(f"Error fetching data from {exchange_name} Futures: {str(e)}")
        return []

def get_top_200_tokens(exchange_name):
    """Fetch top 200 USDT Futures trading pairs from the exchange."""
    try:
        usdt_pairs = get_futures_tickers(exchange_name)
        
        if not usdt_pairs:
            print(f"No USDT Futures pairs with volume data found on {exchange_name}!")
            return None
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(usdt_pairs)
        
        # Sort by 24h volume in descending order
        df = df.sort_values(by='volume_24h', ascending=False)
        
        # Get top 200
        top_200 = df.head(200)
        
        # Extract symbols list
        pair_whitelist = top_200['symbol'].tolist()
        
        # Save to JSON file named after the exchange
        output_file = f"./{exchange_name}_pair_whitelist.json"
        with open(output_file, 'w') as f:
            json.dump({
                'pair_whitelist': pair_whitelist
            }, f, indent=4)
        
        print(f"Saved top 200 tokens to file '{output_file}'")
        print(f"\nTop 10 tokens on {exchange_name}:")
        for symbol in pair_whitelist[:10]:
            print(f"{symbol}")
        
        return pair_whitelist
    
    except Exception as e:
        print(f"Error processing data from {exchange_name}: {str(e)}")
        return None

def main():
    """Main program."""
    print("Fetching top 200 USDT Futures pairs from exchange (excluding stablecoins and invalid pairs)")
    exchange_name = select_exchange()
    print(f"Selected exchange: {exchange_name}")
    top_200_tokens = get_top_200_tokens(exchange_name)

if __name__ == "__main__":
    main()
