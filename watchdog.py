"""
Watchdog module for Sandy Viper Bot
Monitors system health, trading performance, and handles alerts
"""

import psutil
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
from trade_logger import trade_logger
from lot_manager import lot_manager
from nse_data import nse_data


class SystemWatchdog:
    """System monitoring and alerting"""
    
    def __init__(self, check_interval: int = 60):  # Check every minute
        self.check_interval = check_interval
        self.is_running = False
        self.watchdog_thread = None
        self.alerts: List[Dict] = []
        self.alert_callbacks: List[Callable] = []
        
        # Thresholds
        self.cpu_threshold = 80.0  # CPU usage %
        self.memory_threshold = 80.0  # Memory usage %
        self.disk_threshold = 90.0  # Disk usage %
        self.max_loss_threshold = -5000.0  # Max daily loss
        self.connection_timeout = 30  # Seconds
        
        # Status tracking
        self.last_health_check = None
        self.system_status = "UNKNOWN"
        self.trading_status = "UNKNOWN"
        self.api_status = "UNKNOWN"
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Add callback for alerts"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable) -> None:
        """Remove alert callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def _send_alert(self, alert_type: str, message: str, severity: str = "WARNING") -> None:
        """Send alert to all registered callbacks"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        
        self.alerts.append(alert)
        trade_logger.log_warning(f"ALERT [{alert_type}]: {message}")
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                trade_logger.log_error(f"Alert callback error: {str(e)}")
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'disk_usage': disk.percent,
                'disk_free': disk.free,
                'timestamp': datetime.now().isoformat()
            }
            
            # Check thresholds
            if cpu_percent > self.cpu_threshold:
                self._send_alert("SYSTEM", f"High CPU usage: {cpu_percent:.1f}%", "WARNING")
            
            if memory.percent > self.memory_threshold:
                self._send_alert("SYSTEM", f"High memory usage: {memory.percent:.1f}%", "WARNING")
            
            if disk.percent > self.disk_threshold:
                self._send_alert("SYSTEM", f"High disk usage: {disk.percent:.1f}%", "CRITICAL")
            
            self.system_status = "HEALTHY" if all([
                cpu_percent < self.cpu_threshold,
                memory.percent < self.memory_threshold,
                disk.percent < self.disk_threshold
            ]) else "DEGRADED"
            
            return system_info
            
        except Exception as e:
            trade_logger.log_error(f"System check error: {str(e)}")
            self.system_status = "ERROR"
            return {}
    
    def check_trading_performance(self) -> Dict[str, Any]:
        """Check trading performance and risk metrics"""
        try:
            position_summary = lot_manager.get_position_summary()
            
            performance = {
                'daily_pnl': position_summary.get('daily_realized_pnl', 0),
                'unrealized_pnl': position_summary.get('total_unrealized_pnl', 0),
                'net_pnl': position_summary.get('net_pnl', 0),
                'open_positions': position_summary.get('total_positions', 0),
                'risk_utilization': position_summary.get('risk_utilization', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Check risk thresholds
            if performance['daily_pnl'] < self.max_loss_threshold:
                self._send_alert("TRADING", 
                               f"Daily loss threshold breached: {performance['daily_pnl']}", 
                               "CRITICAL")
            
            if performance['risk_utilization'] > 90:
                self._send_alert("TRADING", 
                               f"High risk utilization: {performance['risk_utilization']:.1f}%", 
                               "WARNING")
            
            self.trading_status = "ACTIVE" if performance['open_positions'] > 0 else "IDLE"
            
            return performance
            
        except Exception as e:
            trade_logger.log_error(f"Trading performance check error: {str(e)}")
            self.trading_status = "ERROR"
            return {}
    
    def check_api_connectivity(self) -> Dict[str, Any]:
        """Check API connectivity and response times"""
        try:
            start_time = time.time()
            
            # Test market data API
            market_status = nse_data.get_market_status()
            nse_response_time = time.time() - start_time
            
            # Test Kite API (if authenticated)
            kite_response_time = None
            kite_status = "NOT_AUTHENTICATED"
            
            try:
                from zerodha_auth import zerodha_auth
                if zerodha_auth.is_authenticated():
                    start_time = time.time()
                    from kite_api import kite_api
                    margins = kite_api.get_margins()
                    kite_response_time = time.time() - start_time
                    kite_status = "CONNECTED" if margins.get("status") == "success" else "ERROR"
                    # Flush any queued orders on restored connectivity
                    if kite_status == "CONNECTED":
                        try:
                            from kite_api import flush_queue
                            res = flush_queue()
                            if res.get('placed'):
                                trade_logger.log_info(f"Flushed queued orders: {res}")
                        except Exception as _e:
                            trade_logger.log_warning(f"Queue flush failed: {_e}")
            except Exception:
                kite_status = "ERROR"
            
            connectivity = {
                'nse_api': {
                    'status': 'CONNECTED' if market_status else 'ERROR',
                    'response_time': nse_response_time
                },
                'kite_api': {
                    'status': kite_status,
                    'response_time': kite_response_time
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Check response times
            if nse_response_time > self.connection_timeout:
                self._send_alert("API", f"Slow NSE API response: {nse_response_time:.2f}s", "WARNING")
            
            if kite_response_time and kite_response_time > self.connection_timeout:
                self._send_alert("API", f"Slow Kite API response: {kite_response_time:.2f}s", "WARNING")
            
            self.api_status = "CONNECTED" if all([
                connectivity['nse_api']['status'] == 'CONNECTED',
                kite_status in ['CONNECTED', 'NOT_AUTHENTICATED']
            ]) else "ERROR"
            
            return connectivity
            
        except Exception as e:
            trade_logger.log_error(f"API connectivity check error: {str(e)}")
            self.api_status = "ERROR"
            return {}
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'system': self.check_system_resources(),
            'trading': self.check_trading_performance(),
            'connectivity': self.check_api_connectivity(),
            'overall_status': self._determine_overall_status()
        }
        
        self.last_health_check = datetime.now()
        
        return health_data
    
    def _determine_overall_status(self) -> str:
        """Determine overall system status"""
        if all(status in ["HEALTHY", "CONNECTED", "ACTIVE", "IDLE"] 
               for status in [self.system_status, self.api_status, self.trading_status]):
            return "HEALTHY"
        elif any(status == "ERROR" 
                for status in [self.system_status, self.api_status, self.trading_status]):
            return "ERROR"
        else:
            return "DEGRADED"
    
    def _watchdog_loop(self) -> None:
        """Main watchdog monitoring loop"""
        while self.is_running:
            try:
                self.perform_health_check()
                time.sleep(self.check_interval)
                
            except Exception as e:
                trade_logger.log_error(f"Watchdog loop error: {str(e)}")
                time.sleep(self.check_interval)
    
    def start(self) -> None:
        """Start the watchdog service"""
        if self.is_running:
            trade_logger.log_warning("Watchdog is already running")
            return
        
        self.is_running = True
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.watchdog_thread.start()
        
        trade_logger.log_info("Watchdog service started")
    
    def stop(self) -> None:
        """Stop the watchdog service"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.watchdog_thread and self.watchdog_thread.is_alive():
            self.watchdog_thread.join(timeout=5)
        
        trade_logger.log_info("Watchdog service stopped")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent alerts"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = []
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time > cutoff_time:
                recent_alerts.append(alert)
        
        return recent_alerts
    
    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self.alerts.clear()
        trade_logger.log_info("Alerts cleared")
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get status summary"""
        return {
            'overall_status': self._determine_overall_status(),
            'system_status': self.system_status,
            'trading_status': self.trading_status,
            'api_status': self.api_status,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'is_running': self.is_running,
            'recent_alerts_count': len(self.get_recent_alerts(1)),  # Last hour
            'total_alerts': len(self.alerts)
        }


# Global watchdog instance
watchdog = SystemWatchdog()
