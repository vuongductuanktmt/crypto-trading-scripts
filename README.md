# Crypto Trading Scripts

Welcome to the **Crypto Trading Scripts** repository! This collection includes Python scripts designed to assist with cryptocurrency trading tasks, such as fetching trading pairs, analyzing market data, and other utilities like brute-forcing RAR file passwords. Each script is documented below with setup instructions, usage, and output details.

## Table of Contents
- [Prerequisites](#prerequisites)
  - [Install Python](#install-python)
  - [Install Required Libraries](#install-required-libraries)
- [Scripts](#scripts)
  - [get_top_200_futures_by_exchange.py](#get_top_200_futures_by_exchangepy)
  - [candle_signal_analysis.py](#candle_signal_analysispy)
  - [brute_force_rar.py](#brute_force_rarpy)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running any script in this repository, ensure you have the following:

### Install Python
- **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/).
- Verify Python version:
  ```bash
  python --version
  ```
- Ensure `pip` is up-to-date:
  ```bash
  python -m pip install --upgrade pip
  ```

### Install Required Libraries
Install all necessary Python libraries with a single command:
```bash
pip install --upgrade pandas inquirer requests python-binance numpy rarfile
```

**Library Details**:
- `pandas`: Data manipulation and analysis for handling candlestick and market data.
- `inquirer`: Interactive command-line prompts for selecting exchanges.
- `requests`: HTTP requests for fetching data from exchange APIs (e.g., KuCoin, Bybit).
- `python-binance`: Binance API client for fetching candlestick data.
- `numpy`: Numerical computations for volatility and signal calculations.
- `rarfile`: Handles RAR file extraction for password brute-forcing.

**Additional Requirements**:
- **Internet Connection**: Scripts fetch data from exchange APIs (e.g., Binance, KuCoin, OKX).
- **Binance API Access**: No API key is required for public endpoints, but ensure your IP is not blocked by Binance.
- **RAR File Handling**: For `brute_force_rar.py`, ensure the system has `unrar` installed (required by `rarfile`):
  - **Windows**: Install WinRAR or download `unrar.dll` from [unrarlib](http://www.rarlab.com/rar_add.htm).
  - **Linux**: Install `unrar` via package manager (e.g., `sudo apt-get install unrar`).
  - **macOS**: Install `unrar` via Homebrew (`brew install unrar`).
- **Optional**: A text editor (e.g., VSCode) for modifying scripts.
- **Freqtrade (Optional)**: For integration with Freqtrade, follow the [Freqtrade installation guide](https://www.freqtrade.io/en/stable/installation/).

## Scripts

### get_top_200_futures_by_exchange.py

This script fetches the top 200 USDT perpetual futures pairs from a selected cryptocurrency exchange, sorted by 24-hour trading volume. It excludes stablecoin pairs (e.g., USDC/USDT) and invalid pairs, then saves the results to a JSON file compatible with Freqtrade.

#### Features
- Supports multiple exchanges: Bybit, Binance, OKX, KuCoin, Gate.io.
- Filters out stablecoin pairs (e.g., USDC, BUSD, TUSD).
- Validates base tokens (minimum 2 characters, alphanumeric only).
- Outputs a Freqtrade-compatible `pair_whitelist` JSON file.
- Provides debug information (e.g., number of pairs found, invalid pairs).

#### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/vuongductuanktmt/crypto-trading-scripts.git
   cd crypto-trading-scripts
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade pandas inquirer requests
   ```
3. Save the script (`get_top_200_futures_by_exchange.py`) in the repository folder.

#### Usage
1. Run the script:
   ```bash
   python get_top_200_futures_by_exchange.py
   ```
2. Select an exchange from the interactive menu (e.g., `kucoin`):
   ```
   ? Select an exchange: kucoin
   ```
3. The script will:
   - Fetch USDT perpetual futures data from the exchange's API.
   - Parse and validate pairs (e.g., `ETHUSDTM` → `ETH/USDT:USDT`).
   - Exclude stablecoins and invalid pairs.
   - Save the top 200 pairs to `./<exchange>_pair_whitelist.json`.
   - Display the top 10 pairs and debug information.

#### Output
The script generates a JSON file (e.g., `./kucoin_pair_whitelist.json`) with the following format:
```json
{
    "pair_whitelist": [
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "SOL/USDT:USDT",
        ...
    ]
}
```

#### Integration with Freqtrade
Copy the `pair_whitelist` from the output JSON file into your Freqtrade configuration:
```json
"exchange": {
    "name": "kucoin",
    "pair_whitelist": [
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "SOL/USDT:USDT",
        ...
    ]
}
```

#### Debugging
If the script fails or produces incorrect pairs:
1. **Check API data**:
   ```python
   import requests
   response = requests.get('https://api-futures.kucoin.com/api/v1/contracts/active')  # Example for KuCoin
   print(response.json()['data'][:10])
   ```
2. **Enable debug logging**:
   - Add the following line before `if ccxt_symbol:` in the `get_futures_tickers` function:
     ```python
     print(f"Raw Symbol: {symbol}, CCXT Symbol: {ccxt_symbol}, Base Token: {base_token if ccxt_symbol else 'None'}")
     ```
   - Check the `invalid_pairs` output for excluded pairs.
3. **Test other exchanges**:
   - Run with `okx`, `binance`, or `gateio` to verify functionality.
4. **Check connectivity**:
   - Ensure no firewall or VPN blocks API requests.

#### Notes
- **Stablecoin exclusion**: Pairs like `USDC/USDT:USDT` are excluded. Update `STABLECOINS` in the script if needed.
- **Pair count**: Some exchanges may have fewer than 200 pairs; the script takes the maximum available.
- **Periodic updates**: Run the script regularly to refresh the pair list.
- **Public APIs**: No API keys are required.

---

### candle_signal_analysis.py
This script fetches candlestick data from Binance for a specified trading pair and timeframe, calculates the Parabolic SAR indicator, and generates trading signals based on consecutive candle patterns. It outputs the signal and recent candle details, suitable for manual trading or integration with automated strategies.

#### Features
- Fetches candlestick data from Binance (default: BTCUSDT, 15m timeframe, 100 candles).
- Calculates Parabolic SAR with configurable acceleration factors.
- Analyzes consecutive bullish/bearish candles with adaptive body ratio and thresholds.
- Generates signals: STRONG_BUY (2), BUY (1), NEUTRAL (0), SELL (-1), STRONG_SELL (-2).
- Displays detailed signal output with recent candle data.

#### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/vuongductuanktmt/crypto-trading-scripts.git
   cd crypto-trading-scripts
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade pandas python-binance numpy
   ```
3. Save the script (`candle_signal_analysis.py`) in the repository folder.

#### Usage
1. Run the script:
   ```bash
   python candle_signal_analysis.py
   ```
2. The script will:
   - Fetch candlestick data for `BTCUSDT` on the 15-minute timeframe (100 candles).
   - Calculate the Parabolic SAR signal (BUY or SELL).
   - Analyze consecutive candles to generate a trading signal.
   - Display the signal, recent candles, and an explanation.

#### Configuration
Modify the following parameters in the script to customize behavior:
- `SYMBOL`: Trading pair (e.g., `ETHUSDT`).
- `INTERVAL`: Timeframe (e.g., `1h`, `15m`).
- `LIMIT`: Number of candles to fetch (default: 100).
- `MIN_BODY_RATIO`: Minimum candle body-to-range ratio (default: 0.1).
- `MIN_CONSECUTIVE`: Minimum consecutive candles for a signal (default: 2).

#### Output
Example console output:
```
BTCUSDT (15m) Parabolic SAR signal: BUY
============================================================
TRADING SIGNAL ANALYSIS - 2025-06-25 10:27:00
Pair: BTCUSDT | Timeframe: 15m | Candles: 100
------------------------------------------------------------
SIGNAL: BUY
------------------------------------------------------------
RECENT CANDLE DETAILS:
                timestamp     open     high      low    close
97 2025-06-25 09:45:00  65000.0  65200.0  64950.0  65150.0
98 2025-06-25 10:00:00  65150.0  65300.0  65100.0  65250.0
99 2025-06-25 10:15:00  65250.0  65400.0  65200.0  65350.0
============================================================

EXPLANATION:
- Detected 2 consecutive BULLISH candles
- Candle body ratio >= 0.1
- Recommendation: Consider entering a BUY position
```

#### Integration
- **Manual Trading**: Use the console output to inform trading decisions.
- **Automated Trading**: Integrate the `get_trading_signal` function into a trading bot (e.g., Freqtrade strategy) by passing a DataFrame with OHLC data.
- **Custom Strategies**: Combine with other indicators by modifying the `get_trading_signal` function.

#### Debugging
If the script fails or produces unexpected signals:
1. **Check API**:
   ```python
   from binance.client import Client
   client = Client()
   klines = client.get_klines(symbol='BTCUSDT', interval='15m', limit=10)
   print(klines)
   ```
2. **Verify DataFrame**:
   - Add `print(df.head())` after `fetch_and_prepare_data` to inspect data.
3. **Check Signal Logic**:
   - Add `print(df[['body_ratio', 'direction']].tail(5))` in `get_trading_signal` to debug candle analysis.
4. **Test Parameters**:
   - Adjust `MIN_BODY_RATIO` or `MIN_CONSECUTIVE` to fine-tune signal sensitivity.

#### Notes
- **Public API**: No Binance API key is required for candlestick data.
- **Rate Limits**: Binance may impose rate limits; handle errors with retries if needed.
- **Adaptivity**: The script adjusts `min_body_ratio` and `min_consecutive` based on market conditions.
- **Customization**: Modify Parabolic SAR algorithm parameters (`af`, `sa`) for different market behaviors.

---

### brute_force_rar.py

This script performs a brute-force attack to recover the password of a RAR file by generating combinations of provided strings (e.g., phone numbers, usernames). It uses multi-threading to test passwords efficiently and outputs the correct password if found.

#### Features
- Generates password combinations of lengths 2 to 3 from a provided list of strings.
- Uses multi-threading with `ThreadPoolExecutor` for concurrent password testing.
- Validates RAR file integrity before attempting brute force.
- Provides progress updates with attempt counts.
- Stops immediately upon finding the correct password.

#### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/vuongductuanktmt/crypto-trading-scripts.git
   cd crypto-trading-scripts
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade rarfile
   ```
3. Install system-level `unrar` dependency:
   - **Windows**: Install WinRAR or download `unrar.dll` from [rarlab.com](http://www.rarlab.com/rar_add.htm) and place it in the script directory or system path.
   - **Linux**: Install `unrar` via `sudo apt-get install unrar`.
   - **macOS**: Install `unrar` via Homebrew (`brew install rar`).
4. Save the script (`brute_force_rar.py`) in the repository folder.
5. Prepare a RAR file (e.g., `profile_19112017.rar`) and place it in the script directory.

#### Usage
1. Modify the script to specify:
   - `rar_file`: Path to the RAR file (e.g., `./[filename].rar`).
   - `phone_numbers`: List of strings for password combinations (e.g., phone numbers, usernames).
   - `num_threads`: Number of threads (default: 2).
2. Run the script:
   ```bash
   python brute_force_rar.py
   ```
3. The script will:
   - Generate password combinations (lengths 2-3) from the provided list.
   - Test passwords concurrently using multiple threads.
   - Display progress with attempt counts.
   - Output the correct password and total attempts if found, or report failure.

#### Configuration
Edit the following variables in the script:
- `rar_file`: Path to the target RAR file.
- `phone_numbers`: List of strings to generate password combinations.
- `num_threads`: Number of threads (increase based on CPU cores, e.g., 4 for quad-core).

#### Output
Example console output:
```
Total passwords to test: 6840
Password '01686918781thaocute' failed. Attempt: 1
Password '01686918781190217' failed. Attempt: 2
...
Success! Password found: 0168691878119112017
Total attempts: 3250
```

#### Integration
- **Manual Use**: Run the script to recover RAR file passwords.
- **Automation**: Integrate the `brute_force_rar` function into a larger tool by passing a RAR file path and password list.
- **Custom Lists**: Modify `phone_numbers` to include other potential password components.

#### Debugging
If the script fails or does not find the password:
1. **Check RAR File**:
   - Ensure the file exists and is not corrupted:
     ```python
     import rarfile
     try:
         with rarfile.RarFile('./profile_19112017.rar') as rar:
             print("RAR file is valid")
         except Exception as e:
             print(f"Error: {e}")
     ```
2. **Verify `unrar`**:
   - Confirm `unrar` or `unrar.dll` is installed and accessible.
3. **Inspect Passwords**:
   - Add `print(all_passwords[:10])` in `brute_force_rar` to check generated passwords.
4. **Test Single Thread**:
   - Set `num_threads=1` to simplify debugging.

#### Notes
- **Performance**: Increase `num_threads` based on CPU cores, but avoid overloading (e.g., 2-4 threads for most systems).
- **Combination Size**: Limited to lengths 2-3 to avoid excessive combinations; modify `range(2, 4)` for different lengths.
- **Security**: Use responsibly and only on files you own or have permission to access.
- **Dependencies**: `rarfile` requires `unrar` or `unrar.dll` to function.

---

*More scripts will be added here in future updates. Follow the same structure to document new scripts.*

## Contributing

Contributions are welcome! To add a new script or improve existing ones:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-script`).
3. Add or update the script and document it in this `README.md`.
4. Commit changes (`git commit -m "Add new script XYZ"`).
5. Push to your fork (`git push origin feature/new-script`).
6. Open a pull request.

Please ensure:
- Scripts are well-documented with comments and usage instructions.
- New scripts follow the same structure in `README.md`.
- Code is tested and compatible with Python 3.8+.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
