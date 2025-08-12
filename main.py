"""
Main entry point for Sandy Viper Bot
Demonstrates the integration of all modules
"""

import sys
import time
from datetime import datetime
from config import config
from trade_logger import trade_logger
from zerodha_auth import zerodha_auth
from auto_token_refresher import auto_refresher
from watchdog import watchdog
from lot_manager import lot_manager
from nse_data import nse_data


def initialize_bot():
    """Initialize the trading bot"""
    print("=" * 60)
    print("🐍 Sandy Viper Bot - Initialization")
    print("=" * 60)
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed!")
        print("Please check your environment variables:")
        print("- KITE_API_KEY")
        print("- KITE_API_SECRET") 
        print("- TELEGRAM_BOT_TOKEN")
        return False
    
    print("✅ Configuration validated successfully")
    
    # Start trade logger
    trade_logger.log_info("Sandy Viper Bot starting up...")
    
    # Start watchdog monitoring
    print("🔍 Starting system monitoring...")
    watchdog.start()
    
    # Start auto token refresher
    print("🔄 Starting auto token refresher...")
    auto_refresher.start()
    
    print("✅ Bot initialization completed!")
    return True


def display_status():
    """Display current system status"""
    print("\n" + "=" * 60)
    print("📊 System Status")
    print("=" * 60)
    
    # Configuration status
    config_data = config.to_dict()
    print(f"📋 Configuration:")
    print(f"   - API Key Configured: {config_data['kite']['api_key_configured']}")
    print(f"   - Access Token: {config_data['kite']['access_token_configured']}")
    print(f"   - Telegram Bot: {config_data['telegram']['bot_configured']}")
    print(f"   - Max Position Size: ₹{config_data['trading']['max_position_size']:,}")
    print(f"   - Risk Per Trade: {config_data['trading']['risk_per_trade']*100:.1f}%")
    
    # Authentication status
    auth_status = "✅ Authenticated" if zerodha_auth.is_authenticated() else "❌ Not Authenticated"
    print(f"🔐 Authentication: {auth_status}")
    
    # Market status
    market_data = nse_data.get_market_status()
    market_status = "🟢 Open" if market_data.get('market_open', False) else "🔴 Closed"
    print(f"🏛️ Market Status: {market_status}")
    
    # Position summary
    positions = lot_manager.get_position_summary()
    print(f"💼 Positions:")
    print(f"   - Open Positions: {positions.get('total_positions', 0)}")
    print(f"   - Daily P&L: ₹{positions.get('daily_realized_pnl', 0):,.2f}")
    print(f"   - Unrealized P&L: ₹{positions.get('total_unrealized_pnl', 0):,.2f}")
    print(f"   - Risk Utilization: {positions.get('risk_utilization', 0):.1f}%")
    
    # Watchdog status
    watchdog_status = watchdog.get_status_summary()
    status_emoji = {"HEALTHY": "🟢", "DEGRADED": "🟡", "ERROR": "🔴"}.get(
        watchdog_status['overall_status'], "⚪"
    )
    print(f"🛡️ System Health: {status_emoji} {watchdog_status['overall_status']}")
    print(f"   - System: {watchdog_status['system_status']}")
    print(f"   - Trading: {watchdog_status['trading_status']}")
    print(f"   - API: {watchdog_status['api_status']}")
    print(f"   - Recent Alerts: {watchdog_status['recent_alerts_count']}")


def demo_technical_analysis():
    """Demonstrate technical analysis capabilities"""
    print("\n" + "=" * 60)
    print("📈 Technical Analysis Demo")
    print("=" * 60)
    
    from utils.indicators import TechnicalIndicators
    
    # Sample price data
    sample_prices = [18450, 18465, 18480, 18470, 18485, 18495, 18475, 18490, 18505, 18485]
    
    print(f"📊 Sample Price Data: {sample_prices}")
    
    # Calculate indicators
    indicators = TechnicalIndicators()
    sma_5 = indicators.sma(sample_prices, 5)
    rsi_values = indicators.rsi(sample_prices, 5)
    
    if sma_5:
        print(f"📏 SMA(5): {sma_5[-1]:.2f}")
    
    if rsi_values:
        print(f"⚡ RSI(5): {rsi_values[-1]:.2f}")
    
    # Trend analysis
    trend = indicators.analyze_trend(sample_prices, 5)
    trend_emoji = {"UPTREND": "📈", "DOWNTREND": "📉", "SIDEWAYS": "↔️"}.get(trend, "❓")
    print(f"📊 Trend Analysis: {trend_emoji} {trend}")


def demo_risk_management():
    """Demonstrate risk management capabilities"""
    print("\n" + "=" * 60)
    print("🛡️ Risk Management Demo")
    print("=" * 60)
    
    # Example position sizing
    symbol = "NIFTY"
    entry_price = 18500
    stop_loss = 18400
    
    quantity = lot_manager.calculate_position_size(symbol, entry_price, stop_loss)
    lot_size = lot_manager.get_lot_size(symbol)
    
    print(f"📊 Position Sizing for {symbol}:")
    print(f"   - Entry Price: ₹{entry_price}")
    print(f"   - Stop Loss: ₹{stop_loss}")
    print(f"   - Lot Size: {lot_size}")
    print(f"   - Calculated Quantity: {quantity}")
    
    # Risk check
    risk_ok = lot_manager.check_risk_limits(symbol, quantity, entry_price)
    risk_status = "✅ Approved" if risk_ok else "❌ Rejected"
    print(f"   - Risk Check: {risk_status}")


def main():
    """Main function"""
    try:
        # Initialize bot
        if not initialize_bot():
            sys.exit(1)
        
        # Main loop
        print("\n🚀 Sandy Viper Bot is running...")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Display status every 30 seconds
                display_status()
                
                # Demo features (comment out in production)
                demo_technical_analysis()
                demo_risk_management()
                
                print(f"\n⏰ Next update in 30 seconds... (Current time: {datetime.now().strftime('%H:%M:%S')})")
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Shutdown requested...")
                break
                
    except Exception as e:
        trade_logger.log_error(f"Critical error in main: {str(e)}")
        print(f"❌ Critical error: {str(e)}")
        
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        watchdog.stop()
        auto_refresher.stop()
        trade_logger.log_info("Sandy Viper Bot shutdown completed")
        print("👋 Sandy Viper Bot stopped successfully!")


if __name__ == "__main__":
    main()
