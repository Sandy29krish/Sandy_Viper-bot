"""
Formatting utility functions for Sandy Viper Bot
Handles data formatting, display utilities, and output formatting
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal


class FormattingUtils:
    """Data formatting utilities"""
    
    @staticmethod
    def format_currency(amount: Union[int, float, Decimal], 
                       currency: str = "₹", decimal_places: int = 2) -> str:
        """Format currency with proper Indian number formatting"""
        try:
            # Convert to float
            amount_float = float(amount)
            
            # Handle negative values
            is_negative = amount_float < 0
            amount_float = abs(amount_float)
            
            # Format with commas (Indian style)
            if amount_float >= 10000000:  # 1 crore
                formatted = f"{amount_float/10000000:.{decimal_places}f} Cr"
            elif amount_float >= 100000:  # 1 lakh
                formatted = f"{amount_float/100000:.{decimal_places}f} L"
            elif amount_float >= 1000:  # 1 thousand
                formatted = f"{amount_float/1000:.{decimal_places}f} K"
            else:
                formatted = f"{amount_float:.{decimal_places}f}"
            
            # Add currency symbol and negative sign
            result = f"{currency}{formatted}"
            return f"-{result}" if is_negative else result
            
        except (ValueError, TypeError):
            return f"{currency}0.00"
    
    @staticmethod
    def format_percentage(value: Union[int, float, Decimal], 
                         decimal_places: int = 2, show_sign: bool = True) -> str:
        """Format percentage with proper sign"""
        try:
            pct_value = float(value)
            
            if show_sign and pct_value > 0:
                return f"+{pct_value:.{decimal_places}f}%"
            else:
                return f"{pct_value:.{decimal_places}f}%"
                
        except (ValueError, TypeError):
            return "0.00%"
    
    @staticmethod
    def format_number(value: Union[int, float, Decimal], 
                     decimal_places: int = 2, use_commas: bool = True) -> str:
        """Format number with optional commas"""
        try:
            num_value = float(value)
            
            if use_commas:
                # Indian numbering system
                if abs(num_value) >= 10000000:  # 1 crore
                    return f"{num_value/10000000:.{decimal_places}f} Cr"
                elif abs(num_value) >= 100000:  # 1 lakh
                    return f"{num_value/100000:.{decimal_places}f} L"
                elif abs(num_value) >= 1000:  # 1 thousand
                    return f"{num_value:,.{decimal_places}f}"
                else:
                    return f"{num_value:.{decimal_places}f}"
            else:
                return f"{num_value:.{decimal_places}f}"
                
        except (ValueError, TypeError):
            return "0"
    
    @staticmethod
    def format_datetime(dt: datetime, format_type: str = "default") -> str:
        """Format datetime in various formats"""
        if not isinstance(dt, datetime):
            return "Invalid Date"
        
        format_patterns = {
            "default": "%Y-%m-%d %H:%M:%S",
            "short": "%d/%m/%Y %H:%M",
            "date_only": "%d/%m/%Y",
            "time_only": "%H:%M:%S",
            "human": "%d %b %Y, %I:%M %p",
            "iso": "%Y-%m-%dT%H:%M:%S",
            "trading": "%d-%b-%Y %H:%M"
        }
        
        pattern = format_patterns.get(format_type, format_patterns["default"])
        return dt.strftime(pattern)
    
    @staticmethod
    def format_duration(td: timedelta) -> str:
        """Format timedelta to human readable string"""
        if not isinstance(td, timedelta):
            return "Invalid Duration"
        
        total_seconds = int(td.total_seconds())
        
        if total_seconds < 0:
            return "Past"
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 and days == 0 and hours == 0:  # Only show seconds if less than an hour
            parts.append(f"{seconds}s")
        
        return " ".join(parts) if parts else "0s"
    
    @staticmethod
    def format_option_symbol(symbol: str) -> str:
        """Format option symbol for display"""
        if not isinstance(symbol, str):
            return symbol
        
        # Parse option symbol components
        from utils.market_utils import MarketUtils
        parsed = MarketUtils.parse_option_symbol(symbol)
        
        if parsed:
            underlying = parsed['underlying']
            strike = parsed['strike']
            option_type = parsed['option_type']
            expiry_date = parsed['expiry_date']
            
            return f"{underlying} {strike} {option_type} (Exp: {expiry_date})"
        
        return symbol
    
    @staticmethod
    def format_pnl(pnl: Union[int, float], show_colors: bool = True) -> str:
        """Format P&L with colors"""
        try:
            pnl_float = float(pnl)
            formatted_amount = FormattingUtils.format_currency(abs(pnl_float))
            
            if show_colors:
                if pnl_float > 0:
                    return f"🟢 +{formatted_amount}"
                elif pnl_float < 0:
                    return f"🔴 -{formatted_amount}"
                else:
                    return f"⚪ {formatted_amount}"
            else:
                if pnl_float > 0:
                    return f"+{formatted_amount}"
                elif pnl_float < 0:
                    return f"-{formatted_amount}"
                else:
                    return formatted_amount
                    
        except (ValueError, TypeError):
            return "₹0.00"
    
    @staticmethod
    def format_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
        """Format data as ASCII table"""
        if not data:
            return "No data available"
        
        if headers is None:
            headers = list(data[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = len(str(header))
            for row in data:
                col_widths[header] = max(col_widths[header], len(str(row.get(header, ""))))
        
        # Create table
        table_lines = []
        
        # Header
        header_line = "| " + " | ".join(str(header).ljust(col_widths[header]) for header in headers) + " |"
        separator_line = "+" + "+".join("-" * (col_widths[header] + 2) for header in headers) + "+"
        
        table_lines.append(separator_line)
        table_lines.append(header_line)
        table_lines.append(separator_line)
        
        # Data rows
        for row in data:
            row_line = "| " + " | ".join(str(row.get(header, "")).ljust(col_widths[header]) for header in headers) + " |"
            table_lines.append(row_line)
        
        table_lines.append(separator_line)
        
        return "\n".join(table_lines)
    
    @staticmethod
    def format_position_summary(position: Dict[str, Any]) -> str:
        """Format position summary for display"""
        symbol = position.get('symbol', 'Unknown')
        quantity = position.get('quantity', 0)
        entry_price = position.get('entry_price', 0)
        current_price = position.get('current_price', entry_price)
        pnl = position.get('unrealized_pnl', 0)
        
        formatted_symbol = FormattingUtils.format_option_symbol(symbol)
        formatted_pnl = FormattingUtils.format_pnl(pnl)
        
        return f"{formatted_symbol}\nQty: {quantity} | Entry: ₹{entry_price:.2f} | LTP: ₹{current_price:.2f}\nP&L: {formatted_pnl}"
    
    @staticmethod
    def format_market_data(data: Dict[str, Any]) -> str:
        """Format market data for display"""
        lines = []
        
        if 'symbol' in data:
            lines.append(f"📊 {data['symbol']}")
        
        if 'ltp' in data:
            lines.append(f"LTP: ₹{data['ltp']:.2f}")
        
        if 'change' in data and 'change_percent' in data:
            change = data['change']
            change_pct = data['change_percent']
            
            if change > 0:
                lines.append(f"Change: 🟢 +₹{change:.2f} (+{change_pct:.2f}%)")
            elif change < 0:
                lines.append(f"Change: 🔴 ₹{change:.2f} ({change_pct:.2f}%)")
            else:
                lines.append(f"Change: ⚪ ₹{change:.2f} ({change_pct:.2f}%)")
        
        if 'volume' in data:
            volume = FormattingUtils.format_number(data['volume'], 0)
            lines.append(f"Volume: {volume}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_alert(alert: Dict[str, Any]) -> str:
        """Format alert message"""
        alert_type = alert.get('type', 'GENERAL')
        message = alert.get('message', 'No message')
        severity = alert.get('severity', 'INFO')
        timestamp = alert.get('timestamp', datetime.now().isoformat())
        
        # Choose emoji based on severity
        severity_emojis = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        
        emoji = severity_emojis.get(severity, 'ℹ️')
        formatted_time = FormattingUtils.format_datetime(
            datetime.fromisoformat(timestamp.replace('Z', '')), 
            "time_only"
        )
        
        return f"{emoji} [{alert_type}] {message}\n🕐 {formatted_time}"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text with suffix"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
