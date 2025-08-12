"""
Configuration module for Sandy Viper Bot
Manages all configuration parameters and environment variables
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    max_position_size: float = 100000.0
    risk_per_trade: float = 0.02
    max_daily_loss: float = 5000.0
    trading_hours_start: str = "09:15"
    trading_hours_end: str = "15:30"


@dataclass
class KiteConfig:
    """Kite API configuration"""
    api_key: str = ""
    api_secret: str = ""
    request_token: str = ""
    access_token: str = ""
    public_token: str = ""


@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    bot_token: str = ""
    chat_id: str = ""
    admin_chat_ids: list = None


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.trading = TradingConfig()
        self.kite = KiteConfig()
        self.telegram = TelegramConfig()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Kite API credentials
        self.kite.api_key = os.getenv('KITE_API_KEY', '')
        self.kite.api_secret = os.getenv('KITE_API_SECRET', '')
        self.kite.access_token = os.getenv('KITE_ACCESS_TOKEN', '')
        
        # Telegram credentials
        self.telegram.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Trading parameters
        self.trading.max_position_size = float(os.getenv('MAX_POSITION_SIZE', '100000'))
        self.trading.risk_per_trade = float(os.getenv('RISK_PER_TRADE', '0.02'))
        self.trading.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', '5000'))
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_fields = [
            self.kite.api_key,
            self.kite.api_secret,
            self.telegram.bot_token
        ]
        return all(field for field in required_fields)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding sensitive data)"""
        return {
            'trading': {
                'max_position_size': self.trading.max_position_size,
                'risk_per_trade': self.trading.risk_per_trade,
                'max_daily_loss': self.trading.max_daily_loss,
                'trading_hours_start': self.trading.trading_hours_start,
                'trading_hours_end': self.trading.trading_hours_end
            },
            'kite': {
                'api_key_configured': bool(self.kite.api_key),
                'access_token_configured': bool(self.kite.access_token)
            },
            'telegram': {
                'bot_configured': bool(self.telegram.bot_token),
                'chat_configured': bool(self.telegram.chat_id)
            }
        }


# Global configuration instance
config = Config()
