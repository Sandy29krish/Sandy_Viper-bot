"""
Validation utility functions for Sandy Viper Bot
Handles data validation, input sanitization, and error checking
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation


class ValidationUtils:
    """Data validation utilities"""
    
    # Regex patterns
    SYMBOL_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')
    OPTION_SYMBOL_PATTERN = re.compile(r'^[A-Z]+\d{2}[A-Z]{3}\d{2}\d+(CE|PE)$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,15}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Order types
    VALID_ORDER_TYPES = ['MARKET', 'LIMIT', 'SL', 'SL-M']
    VALID_TRANSACTION_TYPES = ['BUY', 'SELL']
    VALID_PRODUCT_TYPES = ['CNC', 'MIS', 'NRML']
    VALID_VALIDITY_TYPES = ['DAY', 'IOC', 'TTL']
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """Validate trading symbol format"""
        if not isinstance(symbol, str):
            return False
        
        return bool(cls.SYMBOL_PATTERN.match(symbol.upper()))
    
    @classmethod
    def validate_option_symbol(cls, symbol: str) -> bool:
        """Validate option symbol format"""
        if not isinstance(symbol, str):
            return False
        
        return bool(cls.OPTION_SYMBOL_PATTERN.match(symbol.upper()))
    
    @classmethod
    def validate_price(cls, price: Union[int, float, str], min_price: float = 0.05) -> bool:
        """Validate price value"""
        try:
            price_val = float(price)
            return price_val >= min_price and price_val <= 1000000  # Max 10L
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_quantity(cls, quantity: Union[int, str], min_qty: int = 1) -> bool:
        """Validate quantity value"""
        try:
            qty_val = int(quantity)
            return qty_val >= min_qty and qty_val <= 100000  # Max 1L quantity
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> bool:
        """Validate order type"""
        return order_type.upper() in cls.VALID_ORDER_TYPES
    
    @classmethod
    def validate_transaction_type(cls, transaction_type: str) -> bool:
        """Validate transaction type"""
        return transaction_type.upper() in cls.VALID_TRANSACTION_TYPES
    
    @classmethod
    def validate_product_type(cls, product_type: str) -> bool:
        """Validate product type"""
        return product_type.upper() in cls.VALID_PRODUCT_TYPES
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        if not isinstance(email, str):
            return False
        
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number format"""
        if not isinstance(phone, str):
            return False
        
        return bool(cls.PHONE_PATTERN.match(phone))
    
    @classmethod
    def validate_date_range(cls, start_date: date, end_date: date) -> bool:
        """Validate date range"""
        try:
            return start_date <= end_date
        except (TypeError, AttributeError):
            return False
    
    @classmethod
    def validate_percentage(cls, value: Union[int, float, str], 
                           min_val: float = 0, max_val: float = 100) -> bool:
        """Validate percentage value"""
        try:
            pct_val = float(value)
            return min_val <= pct_val <= max_val
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_order_params(cls, order_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate complete order parameters"""
        errors = {}
        
        # Required fields
        required_fields = ['symbol', 'quantity', 'order_type', 'transaction_type', 'product']
        
        for field in required_fields:
            if field not in order_data or order_data[field] is None:
                errors.setdefault('missing_fields', []).append(field)
        
        # Validate individual fields
        if 'symbol' in order_data:
            if not cls.validate_symbol(order_data['symbol']):
                errors.setdefault('invalid_fields', []).append('symbol')
        
        if 'quantity' in order_data:
            if not cls.validate_quantity(order_data['quantity']):
                errors.setdefault('invalid_fields', []).append('quantity')
        
        if 'order_type' in order_data:
            if not cls.validate_order_type(order_data['order_type']):
                errors.setdefault('invalid_fields', []).append('order_type')
        
        if 'transaction_type' in order_data:
            if not cls.validate_transaction_type(order_data['transaction_type']):
                errors.setdefault('invalid_fields', []).append('transaction_type')
        
        if 'product' in order_data:
            if not cls.validate_product_type(order_data['product']):
                errors.setdefault('invalid_fields', []).append('product')
        
        # Validate price for limit orders
        if order_data.get('order_type', '').upper() in ['LIMIT', 'SL']:
            if 'price' not in order_data or not cls.validate_price(order_data['price']):
                errors.setdefault('invalid_fields', []).append('price')
        
        # Validate trigger price for stop loss orders
        if order_data.get('order_type', '').upper() in ['SL', 'SL-M']:
            if 'trigger_price' not in order_data or not cls.validate_price(order_data['trigger_price']):
                errors.setdefault('invalid_fields', []).append('trigger_price')
        
        return errors
    
    @classmethod
    def sanitize_string(cls, value: Any, max_length: int = 100) -> str:
        """Sanitize string input"""
        if value is None:
            return ""
        
        # Convert to string and strip whitespace
        sanitized = str(value).strip()
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        # Truncate to max length
        return sanitized[:max_length]
    
    @classmethod
    def sanitize_numeric(cls, value: Any, decimal_places: int = 2) -> Optional[float]:
        """Sanitize numeric input"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point and minus
                value = re.sub(r'[^\d\.\-]', '', value)
            
            num_val = float(value)
            return round(num_val, decimal_places)
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def validate_api_key(cls, api_key: str) -> bool:
        """Validate API key format"""
        if not isinstance(api_key, str):
            return False
        
        # Basic validation - should be alphanumeric and of reasonable length
        return len(api_key) >= 8 and api_key.replace('_', '').replace('-', '').isalnum()
    
    @classmethod
    def validate_token(cls, token: str) -> bool:
        """Validate access token format"""
        if not isinstance(token, str):
            return False
        
        # Tokens are usually longer and contain various characters
        return len(token) >= 16 and len(token) <= 512
    
    @classmethod
    def validate_chat_id(cls, chat_id: Union[str, int]) -> bool:
        """Validate Telegram chat ID"""
        try:
            chat_id_int = int(chat_id)
            # Telegram chat IDs can be negative (for groups) or positive (for users)
            return abs(chat_id_int) > 0
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_risk_parameters(cls, risk_params: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate risk management parameters"""
        errors = {}
        
        if 'max_position_size' in risk_params:
            if not cls.sanitize_numeric(risk_params['max_position_size']) or \
               float(risk_params['max_position_size']) <= 0:
                errors.setdefault('invalid_fields', []).append('max_position_size')
        
        if 'risk_per_trade' in risk_params:
            if not cls.validate_percentage(risk_params['risk_per_trade'], 0, 10):  # Max 10%
                errors.setdefault('invalid_fields', []).append('risk_per_trade')
        
        if 'max_daily_loss' in risk_params:
            if not cls.sanitize_numeric(risk_params['max_daily_loss']) or \
               float(risk_params['max_daily_loss']) <= 0:
                errors.setdefault('invalid_fields', []).append('max_daily_loss')
        
        return errors
    
    @classmethod
    def is_valid_instrument_token(cls, token: Union[str, int]) -> bool:
        """Validate instrument token"""
        try:
            token_int = int(token)
            return token_int > 0
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_time_range(cls, start_time: str, end_time: str) -> bool:
        """Validate time range format (HH:MM)"""
        time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
        
        if not time_pattern.match(start_time) or not time_pattern.match(end_time):
            return False
        
        # Convert to minutes for comparison
        start_minutes = int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1])
        end_minutes = int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1])
        
        return start_minutes < end_minutes
    
    @classmethod
    def validate_config(cls, config_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate complete configuration"""
        errors = {}
        
        # Validate Kite API config
        kite_config = config_data.get('kite', {})
        if 'api_key' in kite_config and not cls.validate_api_key(kite_config['api_key']):
            errors.setdefault('kite', []).append('invalid_api_key')
        
        # Validate Telegram config
        telegram_config = config_data.get('telegram', {})
        if 'chat_id' in telegram_config and not cls.validate_chat_id(telegram_config['chat_id']):
            errors.setdefault('telegram', []).append('invalid_chat_id')
        
        # Validate trading config
        trading_config = config_data.get('trading', {})
        risk_errors = cls.validate_risk_parameters(trading_config)
        if risk_errors:
            errors['trading'] = risk_errors.get('invalid_fields', [])
        
        return errors
