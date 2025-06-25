import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime

# ================== CONFIGURATION ==================
SYMBOL = "BTCUSDT"  # Trading pair
INTERVAL = '15m'    # Timeframe (15 minutes)
LIMIT = 100         # Number of candles to fetch

# Strategy parameters
MIN_BODY_RATIO = 0.1    # Minimum candle body-to-range ratio
MIN_CONSECUTIVE = 2     # Minimum consecutive candles for signal

# ================== PARABOLIC SAR CALCULATION ==================
def calculate_parabolic_sar(dataframe, af=0.05, max_af=0.2):
    """
    Calculate Parabolic SAR indicator for the given DataFrame.

    Args:
        dataframe: DataFrame with columns: open, high, low, close
        af: Initial acceleration factor (default: 0.05)
        max_af: Maximum acceleration factor (default: 0.2)

    Returns:
        DataFrame with additional columns: sar, ep, af, trend
    """
    df = dataframe.copy()
    df['sar'] = df['close'].copy()
    df['ep'] = df['high'].copy()  # Extreme point
    df['af'] = af                 # Acceleration factor
    df['trend'] = 1               # 1 for uptrend, -1 for downtrend

    for i in range(1, len(df)):
        prev = i - 1
        if df['trend'].iloc[prev] == 1:  # Uptrend
            df.loc[i, 'sar'] = df['sar'].iloc[prev] + df['af'].iloc[prev] * (df['ep'].iloc[prev] - df['sar'].iloc[prev])
            if df['low'].iloc[i] < df['sar'].iloc[i]:
                df.loc[i, 'trend'] = -1
                df.loc[i, 'sar'] = df['ep'].iloc[prev]
                df.loc[i, 'af'] = af
                df.loc[i, 'ep'] = df['low'].iloc[i]
            else:
                df.loc[i, 'trend'] = 1
                if df['high'].iloc[i] > df['ep'].iloc[prev]:
                    df.loc[i, 'ep'] = df['high'].iloc[i]
                    df.loc[i, 'af'] = min(df['af'].iloc[prev] + af, max_af)
                else:
                    df.loc[i, 'ep'] = df['ep'].iloc[prev]
                    df.loc[i, 'af'] = df['af'].iloc[prev]
        else:  # Downtrend
            df.loc[i, 'sar'] = df['sar'].iloc[prev] + df['af'].iloc[prev] * (df['ep'].iloc[prev] - df['sar'].iloc[prev])
            if df['high'].iloc[i] > df['sar'].iloc[i]:
                df.loc[i, 'trend'] = 1
                df.loc[i, 'sar'] = df['ep'].iloc[prev]
                df.loc[i, 'af'] = af
                df.loc[i, 'ep'] = df['high'].iloc[i]
            else:
                df.loc[i, 'trend'] = -1
                if df['low'].iloc[i] < df['ep'].iloc[prev]:
                    df.loc[i, 'ep'] = df['low'].iloc[i]
                    df.loc[i, 'af'] = min(df['af'].iloc[prev] + af, max_af)
                else:
                    df.loc[i, 'ep'] = df['ep'].iloc[prev]
                    df.loc[i, 'af'] = df['af'].iloc[prev]
    return df

def determine_parabolic_sar_signal(pair, dataframe, interval="15m"):
    """
    Determine the Parabolic SAR signal for the given pair and timeframe.

    Args:
        pair: Trading pair (e.g., BTCUSDT)
        dataframe: DataFrame with candle data
        interval: Timeframe (e.g., 15m)

    Returns:
        str: 'BUY' for uptrend, 'SELL' for downtrend
    """
    df = calculate_parabolic_sar(dataframe)
    trend = 'BUY' if df['trend'].iloc[-1] == 1 else 'SELL'
    print(f"{pair} ({interval}) Parabolic SAR signal: {trend}")
    return trend

# ================== TRADING SIGNAL ANALYSIS ==================
def get_trading_signal(dataframe):
    """
    Analyze candles to generate a trading signal based on consecutive candle patterns.

    Args:
        dataframe: DataFrame with columns: open, high, low, close

    Returns:
        pd.Series: Signal value (-2: STRONG_SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG_BUY)
    """
    df = dataframe.copy()

    # Calculate candle body and range
    df['body'] = np.abs(df['close'] - df['open'])
    df['range'] = df['high'] - df['low']
    df['body_ratio'] = np.where(df['range'] > 0, df['body'] / df['range'], 0)

    # Determine candle direction (1: bullish, -1: bearish, 0: neutral)
    df['direction'] = np.where(df['close'] > df['open'], 1, np.where(df['close'] < df['open'], -1, 0))

    # Adaptive min_body_ratio based on historical data
    lookback = min(50, len(df))
    recent_body_ratios = df['body_ratio'].tail(lookback)
    min_body_ratio = 0.5 if recent_body_ratios.empty or recent_body_ratios.isna().all() else \
                     min(max(recent_body_ratios.mean() + recent_body_ratios.std(), 0.3), 0.7)

    # Adaptive min_consecutive based on volatility
    if lookback > 1:
        log_returns = np.log(df['close'] / df['close'].shift(1)).dropna()
        volatility = np.std(log_returns.tail(lookback)) * np.sqrt(96)  # Annualized volatility
        min_consecutive = 3 if volatility < 0.01 else 2 if volatility < 0.03 else 1
    else:
        min_consecutive = 2

    # Count consecutive candles
    consecutive_up = 0
    consecutive_down = 0
    signals = []

    for i in range(len(df)):
        if df['body_ratio'].iloc[i] >= min_body_ratio:
            if df['direction'].iloc[i] == 1:  # Bullish
                consecutive_up += 1
                consecutive_down = 0
            elif df['direction'].iloc[i] == -1:  # Bearish
                consecutive_down += 1
                consecutive_up = 0
            else:  # Neutral
                consecutive_up = consecutive_down = 0
        else:
            consecutive_up = consecutive_down = 0
        signals.append((consecutive_up, consecutive_down))

    # Analyze recent candles
    last_signals = signals[-min_consecutive:] if len(signals) >= min_consecutive else signals
    last_body_ratios = df['body_ratio'].iloc[-min_consecutive:] if len(df) >= min_consecutive else df['body_ratio']
    avg_body_ratio = last_body_ratios.mean() if not last_body_ratios.empty else 0

    # Determine signal strength
    signal_value = 0
    if all(up >= min_consecutive for up, _ in last_signals) and avg_body_ratio >= min_body_ratio:
        signal_value = 2 if avg_body_ratio >= (min_body_ratio + 0.2) else 1
    elif all(down >= min_consecutive for _, down in last_signals) and avg_body_ratio >= min_body_ratio:
        signal_value = -2 if avg_body_ratio >= (min_body_ratio + 0.2) else -1

    return pd.Series(signal_value)

# ================== DATA FETCHING ==================
def fetch_and_prepare_data(symbol=SYMBOL, interval=INTERVAL, limit=LIMIT):
    """
    Fetch and prepare candlestick data from Binance.

    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        interval: Timeframe (e.g., 15m)
        limit: Number of candles to fetch

    Returns:
        DataFrame with columns: timestamp, open, high, low, close
    """
    client = Client()
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)

    # Create DataFrame
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])

    # Convert data types
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].apply(pd.to_numeric)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df[['timestamp', 'open', 'high', 'low', 'close']]

# ================== SIGNAL DISPLAY ==================
def print_signal(signal_value, dataframe, symbol=SYMBOL, interval=INTERVAL, limit=LIMIT):
    """
    Display the trading signal and recent candle details.

    Args:
        signal_value: Integer signal (-2: STRONG_SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG_BUY)
        dataframe: DataFrame with candle data
        symbol: Trading pair
        interval: Timeframe
        limit: Number of candles analyzed
    """
    signal_map = {
        2: "STRONG_BUY", 1: "BUY", 0: "NEUTRAL", -1: "SELL", -2: "STRONG_SELL"
    }
    signal_str = signal_map.get(signal_value, "UNKNOWN")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "=" * 60)
    print(f"TRADING SIGNAL ANALYSIS - {current_time}")
    print(f"Pair: {symbol} | Timeframe: {interval} | Candles: {limit}")
    print("-" * 60)
    print(f"SIGNAL: {signal_str}")
    print("-" * 60)
    print("RECENT CANDLE DETAILS:")
    print(dataframe.tail(3))
    print("=" * 60)

    # Explain signal
    if signal_value in [1, 2]:
        print("\nEXPLANATION:")
        print(f"- Detected {MIN_CONSECUTIVE} consecutive BULLISH candles")
        print(f"- Candle body ratio >= {MIN_BODY_RATIO}")
        print("- Recommendation: Consider entering a BUY position")
    elif signal_value in [-1, -2]:
        print("\nEXPLANATION:")
        print(f"- Detected {MIN_CONSECUTIVE} consecutive BEARISH candles")
        print(f"- Candle body ratio >= {MIN_BODY_RATIO}")
        print("- Recommendation: Consider entering a SELL position")

# ================== MAIN EXECUTION ==================
if __name__ == "__main__":
    try:
        # Fetch data
        df = fetch_and_prepare_data()

        # Calculate Parabolic SAR signal
        determine_parabolic_sar_signal(SYMBOL, df, INTERVAL)

        # Analyze trading signal
        signal = get_trading_signal(df).iloc[-1]

        # Display results
        print_signal(signal, df)

    except Exception as e:
        print(f"Error during execution: {str(e)}")
