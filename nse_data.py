"""
NSE data module for Sandy Viper Bot
Handles NSE market data fetching and processing for Indian markets
All timings are in Indian Standard Time (IST)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
from kite_api import kite_api
from trade_logger import trade_logger


class NSEData:
    """NSE market data handler for Indian markets"""
    
    def __init__(self):
        # NSE India API configuration
        self.nse_base_url = "https://www.nseindia.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # Indian market indices
        self.indices = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'NIFTYIT', 'NIFTYPHARMA']
        
        # Indian Standard Time
        self.ist = pytz.timezone('Asia/Kolkata')
        
        # Indian market timings (IST)
        self.market_open_time = "09:15"
        self.market_close_time = "15:30"
        self.pre_market_start = "09:00"
        self.pre_market_end = "09:15"
    
    def get_current_ist_time(self) -> datetime:
        """Get current time in IST"""
        return datetime.now(self.ist)
    
    def is_market_open_now(self) -> bool:
        """Check if Indian market is currently open"""
        current_time = self.get_current_ist_time()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if current_time.weekday() >= 5:  # Saturday or Sunday
            return False
        
        current_time_str = current_time.strftime("%H:%M")
        return self.market_open_time <= current_time_str <= self.market_close_time
    
    def _get_nse_data(self, endpoint: str) -> Optional[Dict]:
        """Fetch data from NSE India API"""
        try:
            url = f"{self.nse_base_url}{endpoint}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Log successful API call with IST timestamp
            current_time = self.get_current_ist_time()
            trade_logger.log_info(f"NSE API call successful at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {endpoint}")
            
            return response.json()
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"NSE API error at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')} for {endpoint}: {str(e)}")
            return None
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current Indian market status with IST timing"""
        try:
            current_time = self.get_current_ist_time()
            data = self._get_nse_data("/marketStatus")
            
            if data:
                market_open = any(market.get("marketStatus") == "Open" 
                                for market in data.get("marketState", []))
                
                return {
                    "market_open": market_open,
                    "current_time_ist": current_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                    "is_trading_day": current_time.weekday() < 5,
                    "market_session": self._get_market_session_name(current_time),
                    "market_data": data
                }
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"Market status error at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {str(e)}")
        
        return {
            "market_open": False, 
            "current_time_ist": self.get_current_ist_time().strftime('%Y-%m-%d %H:%M:%S IST'),
            "is_trading_day": False,
            "market_session": "CLOSED",
            "market_data": {}
        }
    
    def _get_market_session_name(self, current_time: datetime) -> str:
        """Get current market session name based on IST time"""
        if current_time.weekday() >= 5:  # Weekend
            return "WEEKEND_CLOSED"
        
        time_str = current_time.strftime("%H:%M")
        
        if self.pre_market_start <= time_str < self.pre_market_end:
            return "PRE_MARKET"
        elif self.market_open_time <= time_str <= self.market_close_time:
            return "MARKET_HOURS"
        elif time_str > self.market_close_time:
            return "POST_MARKET_CLOSED"
        else:
            return "PRE_MARKET_CLOSED"
    
    def get_index_data(self, index_name: str = "NIFTY 50") -> Dict[str, Any]:
        """Get Indian index data with IST timestamps"""
        try:
            if index_name not in self.indian_indices:
                trade_logger.log_warning(f"Index {index_name} not in supported Indian indices")
                return {}
                
            data = self._get_nse_data(f"/live-analysis/gainers-losers/{index_name.replace(' ', '%20')}")
            
            if data:
                current_time = self.get_current_ist_time()
                data["timestamp_ist"] = current_time.strftime('%Y-%m-%d %H:%M:%S IST')
                data["market_session"] = self._get_market_session_name(current_time)
                
            return data
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"Index data error for {index_name} at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {str(e)}")
            return {}
    
    def get_option_chain(self, symbol: str) -> Optional[Dict]:
        """Get option chain data for Indian stocks/indices with IST timestamps"""
        try:
            current_time = self.get_current_ist_time()
            
            # Determine correct endpoint for Indian markets
            if symbol.upper() in ['NIFTY', 'BANKNIFTY']:
                endpoint = f"/option-chain-indices?symbol={symbol.upper()}"
            else:
                endpoint = f"/option-chain-equities?symbol={symbol.upper()}"
            
            data = self._get_nse_data(endpoint)
            
            if data:
                data["timestamp_ist"] = current_time.strftime('%Y-%m-%d %H:%M:%S IST')
                data["market_session"] = self._get_market_session_name(current_time)
                data["symbol"] = symbol.upper()
                
            return data
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"Option chain error for {symbol} at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {str(e)}")
            return None
    
    def get_expiry_dates(self, symbol: str) -> List[str]:
        """Get expiry dates for options with IST timezone consideration"""
        try:
            current_time = self.get_current_ist_time()
            option_data = self.get_option_chain(symbol)
            if option_data and "records" in option_data:
                expiry_dates = option_data["records"].get("expiryDates", [])
                
                # Log retrieval with IST timestamp
                trade_logger.log_info(f"Retrieved {len(expiry_dates)} expiry dates for {symbol} at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
                return expiry_dates
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"Expiry dates error for {symbol} at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {str(e)}")
        
        return []
    
    def get_strike_prices(self, symbol: str, expiry: str) -> List[float]:
        """Get strike prices for a given expiry with IST timezone consideration"""
        try:
            current_time = self.get_current_ist_time()
            option_data = self.get_option_chain(symbol)
            if option_data and "records" in option_data:
                data = option_data["records"].get("data", [])
                strikes = set()
                
                for item in data:
                    if item.get("expiryDate") == expiry:
                        strikes.add(item.get("strikePrice", 0))
                
                strike_list = sorted(list(strikes))
                trade_logger.log_info(f"Retrieved {len(strike_list)} strike prices for {symbol} {expiry} at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
                return strike_list
                
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"Strike prices error for {symbol} at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {str(e)}")
        
        return []
    
    def get_vix_data(self) -> Optional[Dict]:
        """Get VIX data with IST timestamps (India VIX)"""
        try:
            current_time = self.get_current_ist_time()
            data = self._get_nse_data("/live-analysis/vix")
            
            if data:
                data["timestamp_ist"] = current_time.strftime('%Y-%m-%d %H:%M:%S IST')
                data["market_session"] = self._get_market_session_name(current_time)
                
            return data
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"VIX data error at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {str(e)}")
            return None
    
    def get_top_gainers_losers(self, category: str = "gainers") -> Optional[List]:
        """Get top gainers or losers with IST timestamps"""
        try:
            current_time = self.get_current_ist_time()
            
            if category.lower() not in ["gainers", "losers"]:
                trade_logger.log_warning(f"Invalid category '{category}' requested at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
                return None
            
            endpoint = f"/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
            data = self._get_nse_data(endpoint)
            
            if data:
                # Add IST timestamp to the data
                data["timestamp_ist"] = current_time.strftime('%Y-%m-%d %H:%M:%S IST')
                data["market_session"] = self._get_market_session_name(current_time)
                
                if "data" in data:
                    sorted_data = sorted(
                        data["data"], 
                        key=lambda x: x.get("pChange", 0), 
                        reverse=(category.lower() == "gainers")
                    )
                    top_10 = sorted_data[:10]  # Top 10
                    trade_logger.log_info(f"Retrieved top 10 {category} at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
                    return top_10
                
        except Exception as e:
            current_time = self.get_current_ist_time()
            trade_logger.log_error(f"Top {category} error at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}: {str(e)}")
        
        return []
    
    def get_live_price_kite(self, symbol: str) -> Optional[float]:
        """Get live price using Kite API"""
        try:
            instruments = [symbol]
            response = kite_api.get_ltp(instruments)
            
            if response.get("status") == "success":
                data = response.get("data", {})
                return data.get(symbol, {}).get("last_price")
                
        except Exception as e:
            trade_logger.log_error(f"Live price error for {symbol}: {str(e)}")
        
        return None
    
    def get_historical_data_kite(self, instrument_token: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Get historical data using Kite API"""
        try:
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            data = kite_api.get_historical_data(instrument_token, from_date, to_date, "day")
            
            if data:
                df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df['date'] = pd.to_datetime(df['date'])
                return df
                
        except Exception as e:
            trade_logger.log_error(f"Historical data error: {str(e)}")
        
        return None
    
    def calculate_volatility(self, symbol: str, days: int = 20) -> Optional[float]:
        """Calculate historical volatility"""
        try:
            # This would need instrument token - simplified for now
            trade_logger.log_info(f"Calculating volatility for {symbol} over {days} days")
            # Implementation would require instrument token lookup
            return None
            
        except Exception as e:
            trade_logger.log_error(f"Volatility calculation error: {str(e)}")
            return None
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get comprehensive market summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "market_status": self.get_market_status(),
            "indices": {},
            "vix": self.get_vix_data(),
            "top_gainers": self.get_top_gainers_losers("gainers"),
            "top_losers": self.get_top_gainers_losers("losers")
        }
        
        # Get data for all major indices
        for index in self.indices:
            summary["indices"][index] = self.get_index_data(index)
        
        return summary


# Global NSE data instance
nse_data = NSEData()

# Lightweight snapshot types for strategy usage
from dataclasses import dataclass
from typing import NamedTuple

@dataclass
class StrikeSnap:
    strike: int
    side: str  # 'CE' or 'PE'
    oi: float
    vol: float

@dataclass
class Snapshot:
    symbol: str
    fut_ltp: float
    atm: int
    strikes: list

def _nearest_step(price: float, step: int) -> int:
    try:
        return int(round(float(price)/step)*step)
    except Exception:
        return int(price)

def fetch_snapshot(symbol: str, band_points: int = 5) -> Snapshot:
    """Build a minimal snapshot around ATM from NSE option chain.
    band_points counts 50/100 steps around ATM for CE/PE aggregation.
    """
    data = nse_data.get_option_chain(symbol)
    # Underlying
    fut_ltp = 0.0
    try:
        fut_ltp = float(((data or {}).get('records') or {}).get('underlyingValue') or 0.0)
    except Exception:
        fut_ltp = 0.0
    # Strike step
    step = 50
    if symbol.upper() == 'BANKNIFTY':
        step = 100
    elif symbol.upper() == 'MIDCPNIFTY':
        step = 25
    atm = _nearest_step(fut_ltp, step) if fut_ltp else 0
    snaps = []
    try:
        records = (data or {}).get('records', {})
        rows = records.get('data', [])
        # Filter same expiry as first row
        target_exp = rows[0].get('expiryDate') if rows else None
        for row in rows:
            if target_exp and row.get('expiryDate') != target_exp:
                continue
            sp = int(row.get('strikePrice', 0) or 0)
            if atm and abs(sp - atm) > band_points*step:
                continue
            ce = row.get('CE') or {}
            pe = row.get('PE') or {}
            if ce:
                snaps.append(StrikeSnap(sp, 'CE', float(ce.get('openInterest') or 0), float(ce.get('totalTradedVolume') or 0)))
            if pe:
                snaps.append(StrikeSnap(sp, 'PE', float(pe.get('openInterest') or 0), float(pe.get('totalTradedVolume') or 0)))
    except Exception:
        pass
    return Snapshot(symbol=symbol.upper(), fut_ltp=fut_ltp, atm=atm, strikes=snaps)
