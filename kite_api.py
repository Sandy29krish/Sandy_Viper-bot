"""
Kite API module for Sandy Viper Bot
Provides interface to Zerodha Kite Connect API
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from zerodha_auth import zerodha_auth
from trade_logger import trade_logger, TradeLog
from config import config


class KiteAPI:
    """Kite Connect API wrapper"""
    
    def __init__(self):
        self.base_url = "https://api.kite.trade"
        self.auth = zerodha_auth
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request with authentication"""
        if not self.auth.is_authenticated():
            raise Exception("Not authenticated. Please login first.")
        
        url = f"{self.base_url}{endpoint}"
        headers = self.auth.get_auth_headers()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, data=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, data=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            trade_logger.log_error(f"API request failed: {str(e)}")
            raise
    
    def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        return self._make_request("GET", "/user/profile")
    
    def get_margins(self) -> Dict[str, Any]:
        """Get account margins"""
        return self._make_request("GET", "/user/margins")
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        return self._make_request("GET", "/portfolio/positions")
    
    def get_holdings(self) -> Dict[str, Any]:
        """Get holdings"""
        return self._make_request("GET", "/portfolio/holdings")
    
    def get_orders(self) -> Dict[str, Any]:
        """Get order history"""
        return self._make_request("GET", "/orders")
    
    def get_trades(self) -> Dict[str, Any]:
        """Get trade history"""
        return self._make_request("GET", "/trades")
    
    def place_order(self, symbol: str, quantity: int, order_type: str, 
                   transaction_type: str, product: str, price: Optional[float] = None,
                   trigger_price: Optional[float] = None, validity: str = "DAY") -> Dict[str, Any]:
        """Place an order"""
        data = {
            "tradingsymbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "transaction_type": transaction_type,
            "product": product,
            "validity": validity
        }
        
        if price:
            data["price"] = price
        if trigger_price:
            data["trigger_price"] = trigger_price
        
        try:
            response = self._make_request("POST", "/orders/regular", data=data)
            
            # Log the trade
            trade_log = TradeLog(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                action=transaction_type,
                quantity=quantity,
                price=price or 0.0,
                order_id=response.get("data", {}).get("order_id", ""),
                strategy="manual",
                status="PLACED"
            )
            trade_logger.log_trade(trade_log)
            
            return response
            
        except Exception as e:
            trade_logger.log_error(f"Order placement failed: {str(e)}")
            raise
    
    def modify_order(self, order_id: str, **kwargs) -> Dict[str, Any]:
        """Modify an existing order"""
        return self._make_request("PUT", f"/orders/regular/{order_id}", data=kwargs)
    
    def cancel_order(self, order_id: str, variety: str = "regular") -> Dict[str, Any]:
        """Cancel an order"""
        return self._make_request("DELETE", f"/orders/{variety}/{order_id}")
    
    def get_quote(self, instruments: List[str]) -> Dict[str, Any]:
        """Get market quotes"""
        params = {"i": instruments}
        return self._make_request("GET", "/quote", params=params)
    
    def get_ltp(self, instruments: List[str]) -> Dict[str, Any]:
        """Get last traded price"""
        params = {"i": instruments}
        return self._make_request("GET", "/quote/ltp", params=params)
    
    def get_ohlc(self, instruments: List[str]) -> Dict[str, Any]:
        """Get OHLC data"""
        params = {"i": instruments}
        return self._make_request("GET", "/quote/ohlc", params=params)
    
    def get_historical_data(self, instrument_token: str, from_date: str, to_date: str,
                           interval: str = "day") -> List[List]:
        """Get historical data"""
        params = {
            "from": from_date,
            "to": to_date,
            "interval": interval
        }
        response = self._make_request("GET", f"/instruments/historical/{instrument_token}/", params=params)
        return response.get("data", {}).get("candles", [])
    
    def get_instruments(self, exchange: Optional[str] = None) -> List[Dict]:
        """Get instruments list"""
        if exchange:
            endpoint = f"/instruments/{exchange}"
        else:
            endpoint = "/instruments"
        
        # This endpoint returns CSV, so we need special handling
        url = f"{self.base_url}{endpoint}"
        headers = self.auth.get_auth_headers()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse CSV response
        lines = response.text.strip().split('\n')
        headers_line = lines[0].split(',')
        
        instruments = []
        for line in lines[1:]:
            values = line.split(',')
            instrument = dict(zip(headers_line, values))
            instruments.append(instrument)
        
        return instruments
    
    def search_instruments(self, query: str, exchange: Optional[str] = None) -> List[Dict]:
        """Search for instruments"""
        instruments = self.get_instruments(exchange)
        return [inst for inst in instruments if query.upper() in inst.get('tradingsymbol', '').upper()]


# Global API instance
kite_api = KiteAPI()
