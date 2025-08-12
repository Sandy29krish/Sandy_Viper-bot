"""
Zerodha authentication module for Sandy Viper Bot
Handles Kite Connect API authentication and token management
"""

import hashlib
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from config import config
from trade_logger import trade_logger


class ZerodhaAuth:
    """Zerodha authentication handler"""
    
    def __init__(self):
        self.api_key = config.kite.api_key
        self.api_secret = config.kite.api_secret
        self.access_token = config.kite.access_token
        self.public_token = config.kite.public_token
        self.login_url = "https://kite.zerodha.com/connect/login"
        self.session_url = "https://api.kite.trade/session/token"
        self.profile_url = "https://api.kite.trade/user/profile"
    
    def generate_checksum(self, api_key: str, request_token: str, api_secret: str) -> str:
        """Generate checksum for authentication"""
        data = api_key + request_token + api_secret
        return hashlib.sha256(data.encode()).hexdigest()
    
    def get_login_url(self) -> str:
        """Get Zerodha login URL"""
        return f"{self.login_url}?api_key={self.api_key}&v=3"
    
    def generate_session(self, request_token: str) -> Dict[str, Any]:
        """Generate session using request token"""
        try:
            checksum = self.generate_checksum(self.api_key, request_token, self.api_secret)
            
            data = {
                "api_key": self.api_key,
                "request_token": request_token,
                "checksum": checksum
            }
            
            response = requests.post(self.session_url, data=data)
            response.raise_for_status()
            
            session_data = response.json()
            
            if session_data.get("status") == "success":
                self.access_token = session_data["data"]["access_token"]
                self.public_token = session_data["data"]["public_token"]
                
                # Update config
                config.kite.access_token = self.access_token
                config.kite.public_token = self.public_token
                
                trade_logger.log_info(f"Authentication successful. Access token generated.")
                return session_data["data"]
            else:
                raise Exception(f"Authentication failed: {session_data}")
                
        except Exception as e:
            trade_logger.log_error(f"Authentication error: {str(e)}")
            raise
    
    def validate_session(self) -> bool:
        """Validate current session"""
        if not self.access_token:
            return False
        
        try:
            headers = {
                "Authorization": f"token {self.api_key}:{self.access_token}",
                "X-Kite-Version": "3"
            }
            
            response = requests.get(self.profile_url, headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                if profile_data.get("status") == "success":
                    trade_logger.log_info("Session validation successful")
                    return True
            
            trade_logger.log_warning("Session validation failed")
            return False
            
        except Exception as e:
            trade_logger.log_error(f"Session validation error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.access_token:
            raise Exception("No access token available. Please authenticate first.")
        
        return {
            "Authorization": f"token {self.api_key}:{self.access_token}",
            "X-Kite-Version": "3",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def logout(self) -> bool:
        """Logout and invalidate session"""
        try:
            if not self.access_token:
                return True
            
            logout_url = "https://api.kite.trade/session/token"
            headers = self.get_auth_headers()
            
            response = requests.delete(logout_url, headers=headers)
            
            if response.status_code == 200:
                self.access_token = None
                self.public_token = None
                config.kite.access_token = ""
                config.kite.public_token = ""
                
                trade_logger.log_info("Logout successful")
                return True
            
            return False
            
        except Exception as e:
            trade_logger.log_error(f"Logout error: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return bool(self.access_token) and self.validate_session()


# Global auth instance
zerodha_auth = ZerodhaAuth()
