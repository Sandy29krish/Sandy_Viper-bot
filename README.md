# Sandy Viper Bot

A sophisticated automated trading bot for Indian stock markets with Telegram integration and AI-powered assistance.

## 🚀 Features

- **Zerodha Kite Integration**: Full API integration for order placement and market data
- **Telegram Bot Interface**: ## 🛠️ Utils Package

The `utils/` folder contains comprehensive utility modules:

### DateTime Utils (`utils/datetime_utils.py`)
```python
from utils import DateTimeUtils

# Check market status
is_open = DateTimeUtils.is_market_open()
session = DateTimeUtils.get_market_session()

# Get time to market events
time_to_open = DateTimeUtils.time_to_market_open()
next_expiry = DateTimeUtils.get_expiry_dates("NIFTY", 1)[0]
```

### Market Utils (`utils/market_utils.py`)
```python
from utils import MarketUtils

# Parse option symbols
parsed = MarketUtils.parse_option_symbol("NIFTY24AUG18500CE")
lot_size = MarketUtils.get_lot_size("NIFTY")

# Strike calculations
atm_strike = MarketUtils.get_atm_strike(18500, "NIFTY")
puts, calls = MarketUtils.get_otm_strikes(18500, "NIFTY", 5)
```

### Validation Utils (`utils/validation_utils.py`)
```python
from utils import ValidationUtils

# Validate trading data
is_valid_symbol = ValidationUtils.validate_symbol("NIFTY")
is_valid_price = ValidationUtils.validate_price(125.50)
order_errors = ValidationUtils.validate_order_params(order_data)
```

### Formatting Utils (`utils/formatting_utils.py`)
```python
from utils import FormattingUtils

# Format data for display
formatted_currency = FormattingUtils.format_currency(125000)  # "₹1.25 L"
formatted_pnl = FormattingUtils.format_pnl(1500)  # "🟢 +₹1,500.00"
formatted_table = FormattingUtils.format_table(data)
```

### File Utils (`utils/file_utils.py`)
```python
from utils import FileUtils

# File operations
FileUtils.write_json(data, "data.json")
loaded_data = FileUtils.read_json("data.json")
backup_path = FileUtils.backup_file("important.log")
```

## 🔧 Getting Startedontrol and monitor trades via Telegram
- **Risk Management**: Advanced position sizing and risk controls
- **Technical Indicators**: Comprehensive technical analysis toolkit
- **AI Assistant**: Machine learning-powered trading assistance
- **Real-time Monitoring**: System health and performance monitoring
- **Auto Token Management**: Automatic session refresh handling
- **NSE Data Integration**: Real-time market data from NSE
- **Strategy Framework**: Extensible trading strategy implementation

## 📁 Project Structure

```
Sandy_Viper-bot/
├── config.py                 # Configuration management
├── trade_logger.py           # Trade logging and data persistence
├── zerodha_auth.py           # Zerodha API authentication
├── kite_api.py               # Kite Connect API wrapper
├── auto_token_refresher.py   # Automatic token refresh
├── nse_data.py               # NSE market data handling
├── lot_manager.py            # Position sizing and risk management
├── watchdog.py               # System monitoring and alerts
├── utils/                    # Utility modules
│   ├── __init__.py          # Utils package initialization
│   ├── datetime_utils.py    # Date/time and market session utilities
│   ├── market_utils.py      # Market-specific calculations and data
│   ├── validation_utils.py  # Data validation and input sanitization
│   ├── formatting_utils.py  # Data formatting and display utilities
│   ├── file_utils.py        # File operations and data persistence
│   └── indicators.py        # Technical indicators and analysis
├── strategy_expiry.py        # Trading strategies (placeholder)
├── runner_expiry.py          # Strategy execution runner (placeholder)
├── telegram_bot.py           # Telegram bot interface (placeholder)
├── telegram_commands.py      # Bot command handlers (placeholder)
├── ai_assistant_expiry.py    # AI trading assistant (placeholder)
├── learning_engine.py        # Machine learning engine (placeholder)
├── main.py                   # Main application entry point
├── utils_demo.py             # Utils package demonstration
└── README.md                 # This file
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sandy29krish/Sandy_Viper-bot.git
   cd Sandy_Viper-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file with your credentials:
   ```env
   # Zerodha Kite API
   KITE_API_KEY=your_api_key
   KITE_API_SECRET=your_api_secret
   KITE_ACCESS_TOKEN=your_access_token

   # Telegram Bot
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id

   # Trading Parameters
   MAX_POSITION_SIZE=100000
   RISK_PER_TRADE=0.02
   MAX_DAILY_LOSS=5000
   ```

## 🔧 Configuration

### Trading Configuration
- `MAX_POSITION_SIZE`: Maximum position value (default: ₹100,000)
- `RISK_PER_TRADE`: Risk percentage per trade (default: 2%)
- `MAX_DAILY_LOSS`: Maximum daily loss limit (default: ₹5,000)
- `TRADING_HOURS_START`: Market start time (default: "09:15")
- `TRADING_HOURS_END`: Market end time (default: "15:30")

### API Configuration
- Configure Zerodha Kite API credentials
- Set up Telegram bot token and chat IDs
- Ensure proper authentication setup

## 📊 Core Modules

### 1. Configuration Manager (`config.py`)
```python
from config import config

# Access trading parameters
max_position = config.trading.max_position_size
risk_per_trade = config.trading.risk_per_trade

# Validate configuration
if config.validate():
    print("Configuration is valid")
```

### 2. Trade Logger (`trade_logger.py`)
```python
from trade_logger import trade_logger, TradeLog

# Log a trade
trade = TradeLog(
    timestamp=datetime.now().isoformat(),
    symbol="NIFTY2540018500PE",
    action="BUY",
    quantity=50,
    price=125.50,
    order_id="230801000001",
    strategy="scalping"
)
trade_logger.log_trade(trade)

# Get daily P&L
daily_pnl = trade_logger.calculate_daily_pnl()
```

### 3. Kite API Wrapper (`kite_api.py`)
```python
from kite_api import kite_api

# Place an order
response = kite_api.place_order(
    symbol="NIFTY2540018500PE",
    quantity=50,
    order_type="LIMIT",
    transaction_type="BUY",
    product="MIS",
    price=125.50
)

# Get live quotes
quotes = kite_api.get_quote(["NSE:NIFTY BANK"])
```

### 4. Technical Indicators (`utils/indicators.py`)
```python
from utils.indicators import TechnicalIndicators

# Calculate indicators
indicators = TechnicalIndicators()
prices = [100, 102, 101, 103, 105, 104, 106]
sma = indicators.sma(prices, period=5)
rsi = indicators.rsi(prices, period=14)
macd_line, signal_line, histogram = indicators.macd(prices)
```

### 5. Risk Management (`lot_manager.py`)
```python
from lot_manager import lot_manager

# Calculate position size
quantity = lot_manager.calculate_position_size(
    symbol="NIFTY",
    entry_price=18500,
    stop_loss=18400,
    risk_amount=1000
)

# Check risk limits
if lot_manager.check_risk_limits("NIFTY", quantity, 18500):
    # Place trade
    pass
```

### 6. System Monitoring (`watchdog.py`)
```python
from watchdog import watchdog

# Start monitoring
watchdog.start()

# Get health status
status = watchdog.get_status_summary()
print(f"System Status: {status['overall_status']}")

# Add alert callback
def alert_handler(alert):
    print(f"Alert: {alert['message']}")

watchdog.add_alert_callback(alert_handler)
```

## 🔐 Authentication

### Zerodha Kite Setup
1. Get API credentials from Zerodha Kite Connect
2. Generate access token using login flow
3. Configure credentials in environment variables

```python
from zerodha_auth import zerodha_auth

# Get login URL
login_url = zerodha_auth.get_login_url()
print(f"Login at: {login_url}")

# After login, generate session with request token
session_data = zerodha_auth.generate_session(request_token)

# Validate session
if zerodha_auth.is_authenticated():
    print("Authentication successful")
```

## 📈 Market Data

### NSE Data Integration
```python
from nse_data import nse_data

# Get market status
market_status = nse_data.get_market_status()

# Get option chain
option_chain = nse_data.get_option_chain("NIFTY")

# Get index data
nifty_data = nse_data.get_index_data("NIFTY")

# Get market summary
summary = nse_data.get_market_summary()
```

## 🛡️ Risk Management Features

- **Position Sizing**: Automatic calculation based on risk parameters
- **Stop Loss Management**: Dynamic stop loss adjustment
- **Daily Loss Limits**: Automatic trading halt on loss limits
- **Margin Monitoring**: Real-time margin requirement checks
- **Risk Utilization**: Percentage-based risk allocation

## 📊 Logging and Monitoring

- **Trade Logs**: CSV and JSON format trade logs
- **System Monitoring**: CPU, memory, and disk usage monitoring
- **API Health**: Connection status and response time monitoring
- **Alert System**: Real-time alerts for system and trading events
- **Performance Metrics**: Daily P&L and performance tracking

## 🔧 Development Status

### ✅ Implemented Modules
- Configuration Management
- Trade Logging
- Zerodha Authentication
- Kite API Integration
- Auto Token Refresher
- NSE Data Handler
- Technical Indicators
- Risk Management
- System Monitoring

### 🚧 Pending Implementation
- Trading Strategies (`strategy_expiry.py`)
- Strategy Runner (`runner_expiry.py`)
- Telegram Bot Interface (`telegram_bot.py`)
- Telegram Commands (`telegram_commands.py`)
- AI Assistant (`ai_assistant_expiry.py`)
- Learning Engine (`learning_engine.py`)

## 🚀 Getting Started

1. **Setup Authentication**
   ```python
   # Configure your API credentials
   python -c "from config import config; print(config.validate())"
   ```

2. **Test API Connection**
   ```python
   # Test Kite API
   from kite_api import kite_api
   profile = kite_api.get_profile()
   ```

3. **Start Monitoring**
   ```python
   # Start system monitoring
   from watchdog import watchdog
   watchdog.start()
   ```

4. **Test Technical Indicators**
   ```python
   # Test indicators
   from utils.indicators import TechnicalIndicators
   indicators = TechnicalIndicators()
   prices = [100, 102, 104, 103, 105]
   sma = indicators.sma(prices, 3)
   ```

5. **Run Utils Demo**
   ```bash
   # Comprehensive utils demonstration
   python utils_demo.py
   ```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading in financial markets involves substantial risk of loss. Users should:

- Test thoroughly in paper trading mode
- Understand all risks before live trading
- Comply with all applicable regulations
- Use appropriate risk management
- Monitor positions actively

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Review the documentation
- Check the logs for error details

## 🔄 Version History

- **v1.0.0**: Initial structured implementation
  - Core modules implemented
  - Basic trading infrastructure
  - Risk management framework
  - System monitoring
  - Technical indicators
