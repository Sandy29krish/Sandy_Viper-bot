"""
Lot manager module for Sandy Viper Bot
Handles position sizing, risk management, and lot calculations
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
from config import config
from trade_logger import trade_logger
from kite_api import kite_api


class LotManager:
    """Position and lot size manager"""
    
    def __init__(self):
        self.config = config
        self.daily_pnl = 0.0
        self.open_positions = {}
        self.lot_sizes = {
            'NIFTY': 50,
            'BANKNIFTY': 15,
            'FINNIFTY': 40,
            'MIDCPNIFTY': 75,
            'SENSEX': 10,
            'BANKEX': 15
        }
    
    def get_lot_size(self, symbol: str) -> int:
        """Get lot size for a symbol"""
        # Extract base symbol
        base_symbol = symbol.split('_')[0] if '_' in symbol else symbol
        return self.lot_sizes.get(base_symbol.upper(), 1)
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss: float, risk_amount: Optional[float] = None) -> int:
        """Calculate optimal position size based on risk"""
        try:
            if risk_amount is None:
                risk_amount = self.config.trading.max_position_size * self.config.trading.risk_per_trade
            
            price_diff = abs(entry_price - stop_loss)
            if price_diff == 0:
                trade_logger.log_warning("Stop loss same as entry price")
                return 0
            
            lot_size = self.get_lot_size(symbol)
            risk_per_share = price_diff
            max_quantity = int(risk_amount / risk_per_share)
            
            # Round down to nearest lot
            lots = max_quantity // lot_size
            quantity = lots * lot_size
            
            trade_logger.log_info(f"Position size calculation for {symbol}: "
                                f"Risk: {risk_amount}, Lots: {lots}, Quantity: {quantity}")
            
            return quantity
            
        except Exception as e:
            trade_logger.log_error(f"Position size calculation error: {str(e)}")
            return 0
    
    def check_risk_limits(self, symbol: str, quantity: int, price: float) -> bool:
        """Check if trade is within risk limits"""
        try:
            # Check position value limit
            position_value = quantity * price
            if position_value > self.config.trading.max_position_size:
                trade_logger.log_warning(f"Position value {position_value} exceeds limit")
                return False
            
            # Check daily loss limit
            if self.daily_pnl < -self.config.trading.max_daily_loss:
                trade_logger.log_warning(f"Daily loss limit exceeded: {self.daily_pnl}")
                return False
            
            # Check margin requirements
            if not self._check_margin_availability(position_value):
                trade_logger.log_warning("Insufficient margin for position")
                return False
            
            return True
            
        except Exception as e:
            trade_logger.log_error(f"Risk check error: {str(e)}")
            return False
    
    def _check_margin_availability(self, required_amount: float) -> bool:
        """Check if sufficient margin is available"""
        try:
            margins = kite_api.get_margins()
            if margins.get("status") == "success":
                equity_margin = margins["data"]["equity"]["available"]["live_balance"]
                commodity_margin = margins["data"]["commodity"]["available"]["live_balance"]
                
                total_available = equity_margin + commodity_margin
                return total_available >= required_amount
            
            return False
            
        except Exception as e:
            trade_logger.log_error(f"Margin check error: {str(e)}")
            return False
    
    def add_position(self, symbol: str, quantity: int, entry_price: float, 
                    order_type: str, strategy: str = "manual") -> bool:
        """Add a new position to tracking"""
        try:
            position_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.open_positions[position_id] = {
                'symbol': symbol,
                'quantity': quantity,
                'entry_price': entry_price,
                'order_type': order_type,
                'strategy': strategy,
                'entry_time': datetime.now(),
                'unrealized_pnl': 0.0
            }
            
            trade_logger.log_info(f"Position added: {position_id}")
            return True
            
        except Exception as e:
            trade_logger.log_error(f"Add position error: {str(e)}")
            return False
    
    def remove_position(self, position_id: str, exit_price: float) -> Optional[float]:
        """Remove position and calculate P&L"""
        try:
            if position_id not in self.open_positions:
                trade_logger.log_warning(f"Position not found: {position_id}")
                return None
            
            position = self.open_positions[position_id]
            quantity = position['quantity']
            entry_price = position['entry_price']
            
            # Calculate P&L
            if position['order_type'].upper() == 'BUY':
                pnl = (exit_price - entry_price) * quantity
            else:
                pnl = (entry_price - exit_price) * quantity
            
            # Update daily P&L
            self.daily_pnl += pnl
            
            # Remove position
            del self.open_positions[position_id]
            
            trade_logger.log_info(f"Position closed: {position_id}, P&L: {pnl}")
            return pnl
            
        except Exception as e:
            trade_logger.log_error(f"Remove position error: {str(e)}")
            return None
    
    def update_unrealized_pnl(self) -> Dict[str, float]:
        """Update unrealized P&L for all open positions"""
        total_unrealized = 0.0
        position_pnls = {}
        
        try:
            for position_id, position in self.open_positions.items():
                symbol = position['symbol']
                current_price = kite_api.get_ltp([symbol])
                
                if current_price and current_price.get("status") == "success":
                    ltp = current_price["data"][symbol]["last_price"]
                    quantity = position['quantity']
                    entry_price = position['entry_price']
                    
                    if position['order_type'].upper() == 'BUY':
                        unrealized_pnl = (ltp - entry_price) * quantity
                    else:
                        unrealized_pnl = (entry_price - ltp) * quantity
                    
                    position['unrealized_pnl'] = unrealized_pnl
                    position_pnls[position_id] = unrealized_pnl
                    total_unrealized += unrealized_pnl
            
            return position_pnls
            
        except Exception as e:
            trade_logger.log_error(f"Update unrealized P&L error: {str(e)}")
            return {}
    
    def get_position_summary(self) -> Dict:
        """Get summary of all positions"""
        try:
            # Update unrealized P&L
            self.update_unrealized_pnl()
            
            total_unrealized = sum(pos['unrealized_pnl'] for pos in self.open_positions.values())
            total_positions = len(self.open_positions)
            
            return {
                'total_positions': total_positions,
                'daily_realized_pnl': self.daily_pnl,
                'total_unrealized_pnl': total_unrealized,
                'net_pnl': self.daily_pnl + total_unrealized,
                'open_positions': self.open_positions,
                'risk_utilization': self._calculate_risk_utilization()
            }
            
        except Exception as e:
            trade_logger.log_error(f"Position summary error: {str(e)}")
            return {}
    
    def _calculate_risk_utilization(self) -> float:
        """Calculate current risk utilization percentage"""
        try:
            total_risk = 0.0
            for position in self.open_positions.values():
                position_value = position['quantity'] * position['entry_price']
                total_risk += position_value
            
            max_risk = self.config.trading.max_position_size
            return (total_risk / max_risk) * 100 if max_risk > 0 else 0.0
            
        except Exception as e:
            trade_logger.log_error(f"Risk utilization error: {str(e)}")
            return 0.0
    
    def can_take_new_position(self, position_value: float) -> bool:
        """Check if new position can be taken"""
        current_utilization = self._calculate_risk_utilization()
        new_utilization = ((position_value / self.config.trading.max_position_size) * 100)
        
        return (current_utilization + new_utilization) <= 80.0  # 80% max utilization
    
    def get_optimal_exit_price(self, symbol: str, entry_price: float, 
                              target_profit: float = 0.02) -> Tuple[float, float]:
        """Calculate optimal exit prices (stop loss and target)"""
        try:
            # Simple percentage-based exit levels
            stop_loss = entry_price * (1 - self.config.trading.risk_per_trade)
            target = entry_price * (1 + target_profit)
            
            return stop_loss, target
            
        except Exception as e:
            trade_logger.log_error(f"Exit price calculation error: {str(e)}")
            return entry_price * 0.98, entry_price * 1.02
    
    def reset_daily_pnl(self) -> None:
        """Reset daily P&L (call at market open)"""
        trade_logger.log_info(f"Resetting daily P&L. Previous: {self.daily_pnl}")
        self.daily_pnl = 0.0


# Global lot manager instance
lot_manager = LotManager()
