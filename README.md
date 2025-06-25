# Crypto Trading Scripts

Welcome to the **Crypto Trading Scripts** repository! This collection includes Python scripts designed to assist with cryptocurrency trading tasks, such as fetching trading pairs, analyzing market data, and integrating with trading platforms like Freqtrade. Each script is documented below with setup instructions, usage, and output details.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Scripts](#scripts)
  - [get_top_200_futures_by_exchange.py](#get_top_200_futures_by_exchangepy)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running any script in this repository, ensure you have the following:

- **Python 3.8+**: Install Python from [python.org](https://www.python.org/downloads/).
- **Required Libraries**: Install dependencies using pip:
  ```bash
  pip install --upgrade pandas inquirer requests
  ```
- **Internet Connection**: Scripts fetch data from exchange APIs (e.g., Binance, KuCoin, OKX).
- **Optional**: A text editor (e.g., VSCode) for modifying scripts.
- **Freqtrade (Optional)**: If integrating with Freqtrade, follow the [Freqtrade installation guide](https://www.freqtrade.io/en/stable/installation/).

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
   git clone https://github.com/your-username/crypto-trading-scripts.git
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
