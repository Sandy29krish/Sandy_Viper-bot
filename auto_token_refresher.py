"""
Auto token refresher module for Sandy Viper Bot
Handles automatic token refresh and session management
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable
from zerodha_auth import zerodha_auth
from trade_logger import trade_logger


class AutoTokenRefresher:
    """Automatic token refresh manager"""
    
    def __init__(self, check_interval: int = 300):  # Check every 5 minutes
        self.check_interval = check_interval
        self.is_running = False
        self.refresh_thread: Optional[threading.Thread] = None
        self.callbacks: list = []
        self.last_check: Optional[datetime] = None
        self.session_expiry_buffer = timedelta(minutes=30)  # Refresh 30 min before expiry
    
    def add_callback(self, callback: Callable) -> None:
        """Add callback to be called when token is refreshed"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable) -> None:
        """Remove callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self) -> None:
        """Notify all callbacks about token refresh"""
        for callback in self.callbacks:
            try:
                callback()
            except Exception as e:
                trade_logger.log_error(f"Callback error: {str(e)}")
    
    def check_token_validity(self) -> bool:
        """Check if current token is valid"""
        try:
            return zerodha_auth.validate_session()
        except Exception as e:
            trade_logger.log_error(f"Token validation error: {str(e)}")
            return False
    
    def refresh_token(self) -> bool:
        """Refresh access token"""
        try:
            if not zerodha_auth.is_authenticated():
                trade_logger.log_warning("No valid session found. Manual authentication required.")
                return False
            
            # For Kite Connect, we need to re-authenticate manually
            # This is a limitation of the API - tokens expire daily
            trade_logger.log_warning("Token refresh required. Please re-authenticate manually.")
            return False
            
        except Exception as e:
            trade_logger.log_error(f"Token refresh error: {str(e)}")
            return False
    
    def _refresh_loop(self) -> None:
        """Main refresh loop"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check token validity
                if not self.check_token_validity():
                    trade_logger.log_warning("Invalid token detected. Attempting refresh...")
                    
                    if self.refresh_token():
                        trade_logger.log_info("Token refreshed successfully")
                        self._notify_callbacks()
                    else:
                        trade_logger.log_error("Token refresh failed. Manual intervention required.")
                
                self.last_check = current_time
                time.sleep(self.check_interval)
                
            except Exception as e:
                trade_logger.log_error(f"Refresh loop error: {str(e)}")
                time.sleep(self.check_interval)
    
    def start(self) -> None:
        """Start the auto refresh service"""
        if self.is_running:
            trade_logger.log_warning("Auto refresher is already running")
            return
        
        self.is_running = True
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()
        
        trade_logger.log_info("Auto token refresher started")
    
    def stop(self) -> None:
        """Stop the auto refresh service"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.refresh_thread and self.refresh_thread.is_alive():
            self.refresh_thread.join(timeout=5)
        
        trade_logger.log_info("Auto token refresher stopped")
    
    def get_status(self) -> dict:
        """Get refresher status"""
        return {
            "is_running": self.is_running,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "check_interval": self.check_interval,
            "token_valid": self.check_token_validity(),
            "callbacks_count": len(self.callbacks)
        }
    
    def force_check(self) -> bool:
        """Force an immediate token check"""
        trade_logger.log_info("Forcing token validation check")
        
        if not self.check_token_validity():
            trade_logger.log_warning("Token invalid. Attempting refresh...")
            return self.refresh_token()
        
        trade_logger.log_info("Token is valid")
        return True


# Global refresher instance
auto_refresher = AutoTokenRefresher()
