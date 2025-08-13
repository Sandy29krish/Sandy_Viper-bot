"""
Utils demo for Sandy Viper Bot
Demonstrates all utility functions and their usage
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append('/workspaces/Sandy_Viper-bot')

from utils import (
    DateTimeUtils, MarketUtils, ValidationUtils, 
    FormattingUtils, FileUtils, TechnicalIndicators
)


def demo_datetime_utils():
    """Demonstrate DateTime utilities"""
    print("=" * 60)
    print("📅 DateTime Utils Demo")
    print("=" * 60)
    
    # Current IST time
    current_time = DateTimeUtils.get_current_ist_time()
    print(f"Current IST Time: {current_time}")
    
    # Market session info
    session = DateTimeUtils.get_market_session()
    print(f"Current Market Session: {session}")
    
    # Check market status
    is_open = DateTimeUtils.is_market_open()
    print(f"Is Market Open: {'Yes' if is_open else 'No'}")
    
    # Time to market open/close
    time_to_open = DateTimeUtils.time_to_market_open()
    if time_to_open:
        formatted_time = DateTimeUtils.format_time_duration(time_to_open)
        print(f"Time to Market Open: {formatted_time}")
    
    # Next trading day
    next_trading_day = DateTimeUtils.get_next_trading_day()
    print(f"Next Trading Day: {next_trading_day.strftime('%Y-%m-%d')}")
    
    # Expiry dates for NIFTY
    expiry_dates = DateTimeUtils.get_expiry_dates("NIFTY", 2)
    print(f"Next 8 NIFTY Expiries: {[d.strftime('%Y-%m-%d') for d in expiry_dates[:8]]}")


def demo_market_utils():
    """Demonstrate Market utilities"""
    print("\n" + "=" * 60)
    print("📊 Market Utils Demo")
    print("=" * 60)
    
    # Option symbol parsing
    option_symbol = "NIFTY24AUG18500CE"
    parsed = MarketUtils.parse_option_symbol(option_symbol)
    if parsed:
        print(f"Parsed Option Symbol: {option_symbol}")
        print(f"  Underlying: {parsed['underlying']}")
        print(f"  Strike: {parsed['strike']}")
        print(f"  Type: {parsed['option_type']}")
        print(f"  Expiry: {parsed['expiry_date']}")
    
    # Lot sizes
    print(f"\nLot Sizes:")
    for symbol in ['NIFTY', 'BANKNIFTY', 'FINNIFTY']:
        lot_size = MarketUtils.get_lot_size(symbol)
        print(f"  {symbol}: {lot_size}")
    
    # ATM and OTM strikes
    spot_price = 18500
    atm_strike = MarketUtils.get_atm_strike(spot_price, "NIFTY")
    put_strikes, call_strikes = MarketUtils.get_otm_strikes(spot_price, "NIFTY", 3)
    
    print(f"\nFor NIFTY spot at {spot_price}:")
    print(f"  ATM Strike: {atm_strike}")
    print(f"  OTM Put Strikes: {put_strikes}")
    print(f"  OTM Call Strikes: {call_strikes}")
    
    # Option moneyness
    moneyness = MarketUtils.calculate_option_moneyness(18500, 18400, "CE")
    print(f"\nOption Moneyness (18500 spot, 18400 CE):")
    print(f"  Moneyness: {moneyness['moneyness']}")
    print(f"  Intrinsic Value: ₹{moneyness['intrinsic_value']:.2f}")
    print(f"  Distance: {moneyness['percentage_distance']:.2f}%")


def demo_validation_utils():
    """Demonstrate Validation utilities"""
    print("\n" + "=" * 60)
    print("✅ Validation Utils Demo")
    print("=" * 60)
    
    # Symbol validation
    symbols = ["NIFTY", "123INVALID", "BANKNIFTY", "nifty"]
    print("Symbol Validation:")
    for symbol in symbols:
        is_valid = ValidationUtils.validate_symbol(symbol)
        print(f"  {symbol}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Price validation
    prices = [100.50, -10, 0.01, "abc", 1000000]
    print("\nPrice Validation:")
    for price in prices:
        is_valid = ValidationUtils.validate_price(price)
        print(f"  {price}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Order parameters validation
    order_data = {
        'symbol': 'NIFTY24AUG18500CE',
        'quantity': 50,
        'order_type': 'LIMIT',
        'transaction_type': 'BUY',
        'product': 'MIS',
        'price': 125.50
    }
    
    errors = ValidationUtils.validate_order_params(order_data)
    print(f"\nOrder Validation:")
    if not errors:
        print("  ✅ All parameters valid")
    else:
        print(f"  ❌ Errors found: {errors}")
    
    # Email and phone validation
    test_data = [
        ("email", "user@example.com", ValidationUtils.validate_email),
        ("email", "invalid-email", ValidationUtils.validate_email),
        ("phone", "+91-9876543210", ValidationUtils.validate_phone),
        ("phone", "invalid", ValidationUtils.validate_phone)
    ]
    
    print("\nContact Validation:")
    for data_type, value, validator in test_data:
        is_valid = validator(value)
        print(f"  {data_type} '{value}': {'✅ Valid' if is_valid else '❌ Invalid'}")


def demo_formatting_utils():
    """Demonstrate Formatting utilities"""
    print("\n" + "=" * 60)
    print("🎨 Formatting Utils Demo")
    print("=" * 60)
    
    # Currency formatting
    amounts = [1250.50, 125000, 1250000, 12500000, -5000]
    print("Currency Formatting:")
    for amount in amounts:
        formatted = FormattingUtils.format_currency(amount)
        print(f"  ₹{amount} → {formatted}")
    
    # Percentage formatting
    percentages = [2.5, -1.25, 0, 15.678]
    print("\nPercentage Formatting:")
    for pct in percentages:
        formatted = FormattingUtils.format_percentage(pct)
        print(f"  {pct} → {formatted}")
    
    # P&L formatting
    pnl_values = [1500, -2500, 0, 750.50]
    print("\nP&L Formatting:")
    for pnl in pnl_values:
        formatted = FormattingUtils.format_pnl(pnl)
        print(f"  {pnl} → {formatted}")
    
    # DateTime formatting
    now = datetime.now()
    formats = ["default", "short", "human", "trading"]
    print(f"\nDateTime Formatting ({now}):")
    for fmt in formats:
        formatted = FormattingUtils.format_datetime(now, fmt)
        print(f"  {fmt}: {formatted}")
    
    # Duration formatting
    durations = [
        timedelta(seconds=30),
        timedelta(minutes=5, seconds=30),
        timedelta(hours=2, minutes=15),
        timedelta(days=1, hours=3)
    ]
    print("\nDuration Formatting:")
    for duration in durations:
        formatted = FormattingUtils.format_duration(duration)
        print(f"  {duration} → {formatted}")
    
    # Table formatting
    sample_data = [
        {"Symbol": "NIFTY", "LTP": 18500, "Change": 25.50, "Volume": 1250000},
        {"Symbol": "BANKNIFTY", "LTP": 45200, "Change": -15.25, "Volume": 850000}
    ]
    
    print("\nTable Formatting:")
    table = FormattingUtils.format_table(sample_data)
    print(table)


def demo_file_utils():
    """Demonstrate File utilities"""
    print("\n" + "=" * 60)
    print("📁 File Utils Demo")
    print("=" * 60)
    
    # Create test directory
    test_dir = "/tmp/sandy_viper_test"
    FileUtils.ensure_directory(test_dir)
    print(f"✅ Created test directory: {test_dir}")
    
    # JSON operations
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "symbol": "NIFTY",
        "price": 18500.50,
        "volume": 1250000
    }
    
    json_file = f"{test_dir}/test_data.json"
    success = FileUtils.write_json(test_data, json_file)
    print(f"JSON Write: {'✅ Success' if success else '❌ Failed'}")
    
    loaded_data = FileUtils.read_json(json_file)
    print(f"JSON Read: {'✅ Success' if loaded_data else '❌ Failed'}")
    if loaded_data:
        print(f"  Loaded: {loaded_data['symbol']} at ₹{loaded_data['price']}")
    
    # CSV operations
    csv_data = [
        {"Symbol": "NIFTY", "Price": 18500, "Volume": 1250000},
        {"Symbol": "BANKNIFTY", "Price": 45200, "Volume": 850000}
    ]
    
    csv_file = f"{test_dir}/test_data.csv"
    success = FileUtils.write_csv(csv_data, csv_file)
    print(f"CSV Write: {'✅ Success' if success else '❌ Failed'}")
    
    loaded_csv = FileUtils.read_csv(csv_file)
    print(f"CSV Read: {'✅ Success' if loaded_csv else '❌ Failed'}")
    if loaded_csv:
        print(f"  Rows loaded: {len(loaded_csv)}")
    
    # File size and backup
    file_size = FileUtils.get_file_size(json_file)
    print(f"File size: {FormattingUtils.format_file_size(file_size)}")
    
    backup_path = FileUtils.backup_file(json_file)
    print(f"Backup created: {'✅ Success' if backup_path else '❌ Failed'}")
    if backup_path:
        print(f"  Backup location: {backup_path}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    print("🧹 Cleaned up test files")


def demo_technical_indicators():
    """Demonstrate Technical Indicators"""
    print("\n" + "=" * 60)
    print("📈 Technical Indicators Demo")
    print("=" * 60)
    
    # Sample price data
    prices = [18400, 18450, 18425, 18475, 18500, 18485, 18520, 18495, 18530, 18510]
    high_prices = [p + 20 for p in prices]
    low_prices = [p - 15 for p in prices]
    
    print(f"Sample Prices: {prices}")
    
    indicators = TechnicalIndicators()
    
    # Moving averages
    sma_5 = indicators.sma(prices, 5)
    ema_5 = indicators.ema(prices, 5)
    
    print(f"\nMoving Averages (Period 5):")
    print(f"  SMA: {sma_5[-1]:.2f}" if sma_5 else "  SMA: Insufficient data")
    print(f"  EMA: {ema_5[-1]:.2f}" if ema_5 else "  EMA: Insufficient data")
    
    # RSI
    rsi = indicators.rsi(prices, 5)
    print(f"  RSI: {rsi[-1]:.2f}" if rsi else "  RSI: Insufficient data")
    
    # MACD
    macd_line, signal_line, histogram = indicators.macd(prices, 5, 8, 3)
    if macd_line and signal_line:
        print(f"  MACD: {macd_line[-1]:.2f}, Signal: {signal_line[-1]:.2f}")
    
    # Bollinger Bands
    upper, middle, lower = indicators.bollinger_bands(prices, 5, 2)
    if upper and middle and lower:
        print(f"  Bollinger Bands: Upper: {upper[-1]:.2f}, Middle: {middle[-1]:.2f}, Lower: {lower[-1]:.2f}")
    
    # Stochastic
    k_values, d_values = indicators.stochastic(high_prices, low_prices, prices, 5, 3)
    if k_values and d_values:
        print(f"  Stochastic: %K: {k_values[-1]:.2f}, %D: {d_values[-1]:.2f}")
    
    # Trend analysis
    trend = indicators.analyze_trend(prices, 5)
    trend_emoji = {"UPTREND": "📈", "DOWNTREND": "📉", "SIDEWAYS": "↔️"}.get(trend, "❓")
    print(f"  Trend: {trend_emoji} {trend}")
    
    # Support and Resistance
    supports, resistances = indicators.support_resistance(prices, 2)
    print(f"  Support Levels: {supports}")
    print(f"  Resistance Levels: {resistances}")
    
    # Pivot Points (using last high, low, close)
    pivot_data = indicators.pivot_points(high_prices[-1], low_prices[-1], prices[-1])
    print(f"  Pivot Point: {pivot_data['pivot']:.2f}")
    print(f"  Resistance: R1: {pivot_data['r1']:.2f}, R2: {pivot_data['r2']:.2f}")
    print(f"  Support: S1: {pivot_data['s1']:.2f}, S2: {pivot_data['s2']:.2f}")


def demo_queue_flush():
    from kite_api import place_market, flush_queue
    # Force queue (simulate by not having valid session)
    r1 = place_market('NIFTY24500CE', 1, 'BUY')
    print('queued_res:', r1)
    # Now flush (will still fail if no session, but function returns counters)
    res = flush_queue()
    print('flush_res:', res)


def main():
    """Main demo function"""
    print("🐍 Sandy Viper Bot - Utils Package Demo")
    print("=" * 60)
    
    try:
        demo_datetime_utils()
        demo_market_utils()
        demo_validation_utils()
        demo_formatting_utils()
        demo_file_utils()
        demo_technical_indicators()
        demo_queue_flush() # Added new demo function
        
        print("\n" + "=" * 60)
        print("✅ All Utils Demos Completed Successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
