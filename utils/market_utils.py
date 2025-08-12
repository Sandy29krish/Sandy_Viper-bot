"""
Market utility functions for Sandy Viper Bot
Handles market-specific calculations and data processing
"""

from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import re


class MarketUtils:
    """Market-related utility functions"""
    
    # Lot sizes for major instruments
    LOT_SIZES = {
        'NIFTY': 50,
        'BANKNIFTY': 15,
        'FINNIFTY': 40,
        'MIDCPNIFTY': 75,
        'SENSEX': 10,
        'BANKEX': 15,
        'NIFTYIT': 25,
        'NIFTYPHARMA': 30
    }
    
    # Strike price intervals
    STRIKE_INTERVALS = {
        'NIFTY': 50,
        'BANKNIFTY': 100,
        'FINNIFTY': 50,
        'MIDCPNIFTY': 25
    }
    
    # Option symbols pattern
    OPTION_PATTERN = re.compile(r'^(\w+)(\d{2})(\w{3})(\d{2})(\d+)(CE|PE)$')
    
    @classmethod
    def parse_option_symbol(cls, symbol: str) -> Optional[Dict[str, Union[str, int]]]:
        """Parse option symbol to extract components"""
        match = cls.OPTION_PATTERN.match(symbol.upper())
        
        if not match:
            return None
        
        underlying, year, month, day, strike, option_type = match.groups()
        
        # Convert month abbreviation to number
        month_map = {
            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
        }
        
        return {
            'underlying': underlying,
            'year': 2000 + int(year),
            'month': month_map.get(month.upper(), 0),
            'day': int(day),
            'strike': int(strike),
            'option_type': option_type,
            'expiry_date': f"20{year}-{month_map.get(month.upper(), 1):02d}-{day}"
        }
    
    @classmethod
    def build_option_symbol(cls, underlying: str, expiry: datetime, 
                           strike: int, option_type: str) -> str:
        """Build option symbol from components"""
        month_names = [
            'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
            'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'
        ]
        
        year_suffix = str(expiry.year)[-2:]
        month_name = month_names[expiry.month - 1]
        day = f"{expiry.day:02d}"
        
        return f"{underlying.upper()}{year_suffix}{month_name}{day}{strike}{option_type.upper()}"
    
    @classmethod
    def get_lot_size(cls, symbol: str) -> int:
        """Get lot size for a symbol"""
        # Extract base symbol
        base_symbol = symbol.split('_')[0] if '_' in symbol else symbol
        
        # For options, extract underlying
        parsed = cls.parse_option_symbol(base_symbol)
        if parsed:
            base_symbol = parsed['underlying']
        
        return cls.LOT_SIZES.get(base_symbol.upper(), 1)
    
    @classmethod
    def get_strike_interval(cls, symbol: str) -> int:
        """Get strike price interval for a symbol"""
        base_symbol = symbol.split('_')[0] if '_' in symbol else symbol
        
        # For options, extract underlying
        parsed = cls.parse_option_symbol(base_symbol)
        if parsed:
            base_symbol = parsed['underlying']
        
        return cls.STRIKE_INTERVALS.get(base_symbol.upper(), 50)
    
    @classmethod
    def round_to_strike(cls, price: float, symbol: str) -> int:
        """Round price to nearest strike price"""
        interval = cls.get_strike_interval(symbol)
        return int(round(price / interval) * interval)
    
    @classmethod
    def get_atm_strike(cls, spot_price: float, symbol: str) -> int:
        """Get At-The-Money strike price"""
        return cls.round_to_strike(spot_price, symbol)
    
    @classmethod
    def get_otm_strikes(cls, spot_price: float, symbol: str, 
                       num_strikes: int = 5) -> Tuple[List[int], List[int]]:
        """Get Out-of-The-Money strike prices"""
        atm_strike = cls.get_atm_strike(spot_price, symbol)
        interval = cls.get_strike_interval(symbol)
        
        # Call strikes (above ATM)
        call_strikes = [atm_strike + (i * interval) for i in range(1, num_strikes + 1)]
        
        # Put strikes (below ATM)
        put_strikes = [atm_strike - (i * interval) for i in range(1, num_strikes + 1)]
        put_strikes.reverse()  # Arrange in ascending order
        
        return put_strikes, call_strikes
    
    @classmethod
    def get_strike_chain(cls, spot_price: float, symbol: str, 
                        range_percent: float = 0.1) -> List[int]:
        """Get complete strike chain within percentage range"""
        range_amount = spot_price * range_percent
        lower_bound = spot_price - range_amount
        upper_bound = spot_price + range_amount
        
        interval = cls.get_strike_interval(symbol)
        
        # Find strikes within range
        strikes = []
        strike = cls.round_to_strike(lower_bound, symbol)
        
        while strike <= upper_bound:
            strikes.append(strike)
            strike += interval
        
        return strikes
    
    @classmethod
    def calculate_option_moneyness(cls, spot_price: float, strike_price: int, 
                                  option_type: str) -> Dict[str, Union[float, str]]:
        """Calculate option moneyness"""
        if option_type.upper() == 'CE':  # Call option
            intrinsic_value = max(0, spot_price - strike_price)
            if spot_price > strike_price:
                moneyness = "ITM"  # In-The-Money
            elif spot_price == strike_price:
                moneyness = "ATM"  # At-The-Money
            else:
                moneyness = "OTM"  # Out-of-The-Money
        else:  # Put option
            intrinsic_value = max(0, strike_price - spot_price)
            if spot_price < strike_price:
                moneyness = "ITM"
            elif spot_price == strike_price:
                moneyness = "ATM"
            else:
                moneyness = "OTM"
        
        return {
            'intrinsic_value': intrinsic_value,
            'moneyness': moneyness,
            'distance_from_spot': abs(spot_price - strike_price),
            'percentage_distance': abs(spot_price - strike_price) / spot_price * 100
        }
    
    @classmethod
    def get_expiry_day_strikes(cls, symbol: str) -> Dict[str, List[int]]:
        """Get typical expiry day strike ranges"""
        if symbol.upper() == 'NIFTY':
            return {
                'tight_range': list(range(18000, 19100, 50)),  # Example range
                'wide_range': list(range(17500, 19500, 50))
            }
        elif symbol.upper() == 'BANKNIFTY':
            return {
                'tight_range': list(range(44000, 46000, 100)),
                'wide_range': list(range(43000, 47000, 100))
            }
        
        return {'tight_range': [], 'wide_range': []}
    
    @classmethod
    def calculate_theta_decay(cls, days_to_expiry: int, option_price: float) -> float:
        """Estimate theta decay (simplified calculation)"""
        if days_to_expiry <= 0:
            return 0.0
        
        # Simplified theta calculation
        # Real theta requires Black-Scholes model
        time_value = option_price  # Assuming entire premium is time value
        theta_per_day = time_value / days_to_expiry
        
        # Theta decay accelerates closer to expiry
        if days_to_expiry <= 7:
            theta_per_day *= 1.5
        elif days_to_expiry <= 30:
            theta_per_day *= 1.2
        
        return theta_per_day
    
    @classmethod
    def is_liquid_strike(cls, spot_price: float, strike_price: int, 
                        option_type: str, max_distance_percent: float = 5.0) -> bool:
        """Check if strike is likely to be liquid"""
        distance_percent = abs(spot_price - strike_price) / spot_price * 100
        return distance_percent <= max_distance_percent
    
    @classmethod
    def get_liquid_strikes(cls, spot_price: float, symbol: str, 
                          option_type: str = 'BOTH') -> List[int]:
        """Get list of liquid strikes"""
        strikes = cls.get_strike_chain(spot_price, symbol, 0.05)  # 5% range
        
        if option_type.upper() == 'CE':
            # For calls, focus on ATM and OTM
            atm_strike = cls.get_atm_strike(spot_price, symbol)
            return [s for s in strikes if s >= atm_strike]
        elif option_type.upper() == 'PE':
            # For puts, focus on ATM and OTM
            atm_strike = cls.get_atm_strike(spot_price, symbol)
            return [s for s in strikes if s <= atm_strike]
        else:
            return strikes
    
    @classmethod
    def calculate_margin_requirement(cls, symbol: str, quantity: int, 
                                   option_price: float, spot_price: float,
                                   option_type: str) -> Dict[str, float]:
        """Calculate approximate margin requirement"""
        # SPAN margin calculation (simplified)
        lot_size = cls.get_lot_size(symbol)
        lots = quantity / lot_size
        
        # Base margin percentage (varies by volatility)
        base_margin_percent = 0.10  # 10% for options
        
        margin_amount = lots * lot_size * spot_price * base_margin_percent
        premium_received = lots * lot_size * option_price
        
        # For option selling
        if option_type in ['SHORT_CE', 'SHORT_PE']:
            net_margin = margin_amount - premium_received
        else:
            net_margin = premium_received  # For buying options
        
        return {
            'margin_required': margin_amount,
            'premium_amount': premium_received,
            'net_margin': max(0, net_margin),  # Cannot be negative
            'lots': lots
        }
