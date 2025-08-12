"""
Trade logging module for Sandy Viper Bot
Handles all trade-related logging and data persistence
"""

import logging
import json
import csv
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class TradeLog:
    """Trade log data structure"""
    timestamp: str
    symbol: str
    action: str  # BUY/SELL
    quantity: int
    price: float
    order_id: str
    strategy: str
    pnl: Optional[float] = None
    commission: Optional[float] = None
    status: str = "PENDING"


class TradeLogger:
    """Trade logger class"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup file logger
        self.logger = logging.getLogger('trade_logger')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_trade(self, trade: TradeLog) -> None:
        """Log a trade"""
        trade_dict = asdict(trade)
        
        # Log to file
        self.logger.info(f"TRADE: {json.dumps(trade_dict)}")
        
        # Save to CSV
        self._save_to_csv(trade)
        
        # Save to JSON
        self._save_to_json(trade)
    
    def _save_to_csv(self, trade: TradeLog) -> None:
        """Save trade to CSV file"""
        csv_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Check if file exists to write header
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=asdict(trade).keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(asdict(trade))
    
    def _save_to_json(self, trade: TradeLog) -> None:
        """Save trade to JSON file"""
        json_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.json"
        
        trades = []
        if json_file.exists():
            with open(json_file, 'r') as f:
                trades = json.load(f)
        
        trades.append(asdict(trade))
        
        with open(json_file, 'w') as f:
            json.dump(trades, f, indent=2)
    
    def get_daily_trades(self, date: Optional[str] = None) -> List[TradeLog]:
        """Get trades for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        json_file = self.log_dir / f"trades_{date}.json"
        
        if not json_file.exists():
            return []
        
        with open(json_file, 'r') as f:
            trades_data = json.load(f)
        
        return [TradeLog(**trade) for trade in trades_data]
    
    def calculate_daily_pnl(self, date: Optional[str] = None) -> float:
        """Calculate daily P&L"""
        trades = self.get_daily_trades(date)
        return sum(trade.pnl for trade in trades if trade.pnl is not None)
    
    def log_info(self, message: str) -> None:
        """Log general information"""
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def log_warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)


# Global logger instance
trade_logger = TradeLogger()
