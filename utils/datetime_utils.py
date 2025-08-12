"""
DateTime utility functions for Sandy Viper Bot
Handles market timings, session management, and date operations
"""

from datetime import datetime, timedelta, time
from typing import Optional, Tuple, List
import pytz
from dataclasses import dataclass


@dataclass
class TradingSession:
    """Trading session information"""
    name: str
    start_time: time
    end_time: time
    is_active: bool = False


class DateTimeUtils:
    """DateTime utility functions"""
    
    # Indian Standard Time
    IST = pytz.timezone('Asia/Kolkata')
    
    # Market timings
    MARKET_OPEN = time(9, 15)  # 9:15 AM
    MARKET_CLOSE = time(15, 30)  # 3:30 PM
    
    # Pre-market and after-market sessions
    PRE_MARKET_START = time(9, 0)   # 9:00 AM
    PRE_MARKET_END = time(9, 15)    # 9:15 AM
    
    AFTER_MARKET_START = time(15, 30)  # 3:30 PM
    AFTER_MARKET_END = time(16, 0)     # 4:00 PM
    
    @classmethod
    def get_current_ist_time(cls) -> datetime:
        """Get current time in IST"""
        return datetime.now(cls.IST)
    
    @classmethod
    def is_market_open(cls, current_time: Optional[datetime] = None) -> bool:
        """Check if market is currently open"""
        if current_time is None:
            current_time = cls.get_current_ist_time()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if current_time.weekday() >= 5:  # Saturday or Sunday
            return False
        
        current_time_only = current_time.time()
        return cls.MARKET_OPEN <= current_time_only <= cls.MARKET_CLOSE
    
    @classmethod
    def is_pre_market(cls, current_time: Optional[datetime] = None) -> bool:
        """Check if it's pre-market session"""
        if current_time is None:
            current_time = cls.get_current_ist_time()
        
        if current_time.weekday() >= 5:  # Weekend
            return False
        
        current_time_only = current_time.time()
        return cls.PRE_MARKET_START <= current_time_only < cls.PRE_MARKET_END
    
    @classmethod
    def is_after_market(cls, current_time: Optional[datetime] = None) -> bool:
        """Check if it's after-market session"""
        if current_time is None:
            current_time = cls.get_current_ist_time()
        
        if current_time.weekday() >= 5:  # Weekend
            return False
        
        current_time_only = current_time.time()
        return cls.AFTER_MARKET_START <= current_time_only <= cls.AFTER_MARKET_END
    
    @classmethod
    def get_market_session(cls, current_time: Optional[datetime] = None) -> str:
        """Get current market session"""
        if current_time is None:
            current_time = cls.get_current_ist_time()
        
        if current_time.weekday() >= 5:
            return "CLOSED_WEEKEND"
        
        if cls.is_pre_market(current_time):
            return "PRE_MARKET"
        elif cls.is_market_open(current_time):
            return "MARKET_OPEN"
        elif cls.is_after_market(current_time):
            return "AFTER_MARKET"
        else:
            return "CLOSED"
    
    @classmethod
    def time_to_market_open(cls, current_time: Optional[datetime] = None) -> Optional[timedelta]:
        """Get time remaining until market opens"""
        if current_time is None:
            current_time = cls.get_current_ist_time()
        
        if cls.is_market_open(current_time):
            return timedelta(0)  # Market is already open
        
        # Find next market open time
        next_open = current_time.replace(
            hour=cls.MARKET_OPEN.hour,
            minute=cls.MARKET_OPEN.minute,
            second=0,
            microsecond=0
        )
        
        # If market opening time has passed today, move to next weekday
        if current_time.time() > cls.MARKET_OPEN or current_time.weekday() >= 5:
            next_open += timedelta(days=1)
            
            # Skip weekends
            while next_open.weekday() >= 5:
                next_open += timedelta(days=1)
        
        return next_open - current_time
    
    @classmethod
    def time_to_market_close(cls, current_time: Optional[datetime] = None) -> Optional[timedelta]:
        """Get time remaining until market closes"""
        if current_time is None:
            current_time = cls.get_current_ist_time()
        
        if not cls.is_market_open(current_time):
            return None  # Market is not open
        
        market_close = current_time.replace(
            hour=cls.MARKET_CLOSE.hour,
            minute=cls.MARKET_CLOSE.minute,
            second=0,
            microsecond=0
        )
        
        return market_close - current_time
    
    @classmethod
    def get_trading_days(cls, start_date: datetime, end_date: datetime) -> List[datetime]:
        """Get list of trading days between two dates"""
        trading_days = []
        current_date = start_date.date()
        end_date = end_date.date()
        
        while current_date <= end_date:
            # Check if it's a weekday
            if current_date.weekday() < 5:
                trading_days.append(datetime.combine(current_date, time()))
            current_date += timedelta(days=1)
        
        return trading_days
    
    @classmethod
    def is_trading_day(cls, date: datetime) -> bool:
        """Check if given date is a trading day"""
        return date.weekday() < 5  # Monday to Friday
    
    @classmethod
    def get_next_trading_day(cls, date: Optional[datetime] = None) -> datetime:
        """Get next trading day"""
        if date is None:
            date = cls.get_current_ist_time()
        
        next_day = date + timedelta(days=1)
        
        # Skip weekends
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        
        return next_day
    
    @classmethod
    def get_previous_trading_day(cls, date: Optional[datetime] = None) -> datetime:
        """Get previous trading day"""
        if date is None:
            date = cls.get_current_ist_time()
        
        prev_day = date - timedelta(days=1)
        
        # Skip weekends
        while prev_day.weekday() >= 5:
            prev_day -= timedelta(days=1)
        
        return prev_day
    
    @classmethod
    def format_time_duration(cls, td: timedelta) -> str:
        """Format timedelta to human readable string"""
        total_seconds = int(td.total_seconds())
        
        if total_seconds < 0:
            return "Past"
        
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 and hours == 0:  # Only show seconds if less than an hour
            parts.append(f"{seconds}s")
        
        return " ".join(parts) if parts else "0s"
    
    @classmethod
    def get_expiry_dates(cls, symbol: str, months_ahead: int = 3) -> List[datetime]:
        """Get option expiry dates for given symbol"""
        current_date = cls.get_current_ist_time()
        expiry_dates = []
        
        # For major indices, expiry is every Thursday
        if symbol.upper() in ['NIFTY', 'BANKNIFTY', 'FINNIFTY']:
            # Find next Thursday
            days_ahead = (3 - current_date.weekday()) % 7
            if days_ahead == 0 and current_date.time() > cls.MARKET_CLOSE:
                days_ahead = 7
            
            next_thursday = current_date + timedelta(days=days_ahead)
            
            # Get expiry dates for specified months
            for _ in range(months_ahead * 4):  # Approximately 4 weeks per month
                expiry_dates.append(next_thursday)
                next_thursday += timedelta(weeks=1)
        
        return expiry_dates
    
    @classmethod
    def get_session_info(cls, current_time: Optional[datetime] = None) -> TradingSession:
        """Get detailed session information"""
        if current_time is None:
            current_time = cls.get_current_ist_time()
        
        session_name = cls.get_market_session(current_time)
        
        if session_name == "PRE_MARKET":
            return TradingSession("Pre-Market", cls.PRE_MARKET_START, cls.PRE_MARKET_END, True)
        elif session_name == "MARKET_OPEN":
            return TradingSession("Market Hours", cls.MARKET_OPEN, cls.MARKET_CLOSE, True)
        elif session_name == "AFTER_MARKET":
            return TradingSession("After-Market", cls.AFTER_MARKET_START, cls.AFTER_MARKET_END, True)
        else:
            return TradingSession("Closed", time(0, 0), time(0, 0), False)
