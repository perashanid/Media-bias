import logging
import smtplib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
try:
    from email.mime.text import MIMEText as MimeText
    from email.mime.multipart import MIMEMultipart as MimeMultipart
except ImportError:
    from email.MIMEText import MIMEText as MimeText
    from email.MIMEMultipart import MIMEMultipart as MimeMultipart
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Represents a system alert"""
    alert_id: str
    level: str  # 'info', 'warning', 'error', 'critical'
    title: str
    message: str
    timestamp: datetime
    source: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    articles_scraped_last_hour: int
    articles_analyzed_last_hour: int
    scraping_success_rate: float
    analysis_success_rate: float
    database_size_mb: float
    response_time_ms: float
    error_count_last_hour: int


class MonitoringService:
    """Service for monitoring system health and sending alerts"""
    
    def __init__(self, config_file: str = 'config/monitoring_config.json'):
        self.alerts: List[Alert] = []
        self.metrics_history: List[SystemMetrics] = []
        self.config_file = config_file
        self.config = self._load_config()
        
        # Alert thresholds
        self.thresholds = {
            'scraping_success_rate_min': 80.0,
            'analysis_success_rate_min': 90.0,
            'response_time_max_ms': 5000,
            'error_count_max_per_hour': 50,
            'database_size_max_gb': 10.0
        }
        
        # Email configuration
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'localhost'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_username': os.getenv('SMTP_USERNAME', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('ALERT_FROM_EMAIL', 'alerts@mediabias.local'),
            'to_emails': os.getenv('ALERT_TO_EMAILS', '').split(',') if os.getenv('ALERT_TO_EMAILS') else []
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Loaded monitoring config from {self.config_file}")
                    return config
            else:
                logger.info("No monitoring config file found, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Failed to load monitoring config: {e}")
            return {}
    
    def _save_config(self):
        """Save monitoring configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'thresholds': self.thresholds,
                'email_enabled': self.config.get('email_enabled', False),
                'alert_retention_days': self.config.get('alert_retention_days', 30),
                'metrics_retention_days': self.config.get('metrics_retention_days', 7)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save monitoring config: {e}")
    
    def create_alert(self, level: str, title: str, message: str, source: str = 'system') -> str:
        """Create a new alert"""
        try:
            alert_id = f"{source}_{level}_{int(datetime.now().timestamp())}"
            
            alert = Alert(
                alert_id=alert_id,
                level=level,
                title=title,
                message=message,
                timestamp=datetime.now(),
                source=source
            )
            
            self.alerts.append(alert)
            
            # Log the alert
            log_level = getattr(logging, level.upper(), logging.INFO)
            logger.log(log_level, f"Alert created: {title} - {message}")
            
            # Send email notification if configured
            if self.config.get('email_enabled', False) and level in ['error', 'critical']:
                self._send_email_alert(alert)
            
            # Clean up old alerts
            self._cleanup_old_alerts()
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return ""
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    logger.info(f"Alert resolved: {alert.title}")
                    return True
            
            logger.warning(f"Alert {alert_id} not found or already resolved")
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) alerts"""
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        
        return [{
            'alert_id': alert.alert_id,
            'level': alert.level,
            'title': alert.title,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'source': alert.source
        } for alert in active_alerts]
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
        
        return [{
            'alert_id': alert.alert_id,
            'level': alert.level,
            'title': alert.title,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'source': alert.source,
            'resolved': alert.resolved,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
        } for alert in recent_alerts]
    
    def record_metrics(self, metrics: SystemMetrics):
        """Record system metrics and check for threshold violations"""
        try:
            self.metrics_history.append(metrics)
            
            # Check thresholds and create alerts if necessary
            self._check_metric_thresholds(metrics)
            
            # Clean up old metrics
            self._cleanup_old_metrics()
            
            logger.debug(f"Recorded metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
    
    def _check_metric_thresholds(self, metrics: SystemMetrics):
        """Check if metrics violate thresholds and create alerts"""
        try:
            # Check scraping success rate
            if metrics.scraping_success_rate < self.thresholds['scraping_success_rate_min']:
                self.create_alert(
                    'warning',
                    'Low Scraping Success Rate',
                    f'Scraping success rate is {metrics.scraping_success_rate:.1f}%, '
                    f'below threshold of {self.thresholds["scraping_success_rate_min"]}%',
                    'scraper'
                )
            
            # Check analysis success rate
            if metrics.analysis_success_rate < self.thresholds['analysis_success_rate_min']:
                self.create_alert(
                    'warning',
                    'Low Analysis Success Rate',
                    f'Analysis success rate is {metrics.analysis_success_rate:.1f}%, '
                    f'below threshold of {self.thresholds["analysis_success_rate_min"]}%',
                    'analyzer'
                )
            
            # Check response time
            if metrics.response_time_ms > self.thresholds['response_time_max_ms']:
                self.create_alert(
                    'warning',
                    'High Response Time',
                    f'Average response time is {metrics.response_time_ms:.0f}ms, '
                    f'above threshold of {self.thresholds["response_time_max_ms"]}ms',
                    'api'
                )
            
            # Check error count
            if metrics.error_count_last_hour > self.thresholds['error_count_max_per_hour']:
                self.create_alert(
                    'error',
                    'High Error Rate',
                    f'Error count in last hour is {metrics.error_count_last_hour}, '
                    f'above threshold of {self.thresholds["error_count_max_per_hour"]}',
                    'system'
                )
            
            # Check database size
            database_size_gb = metrics.database_size_mb / 1024
            if database_size_gb > self.thresholds['database_size_max_gb']:
                self.create_alert(
                    'warning',
                    'Large Database Size',
                    f'Database size is {database_size_gb:.2f}GB, '
                    f'above threshold of {self.thresholds["database_size_max_gb"]}GB',
                    'database'
                )
                
        except Exception as e:
            logger.error(f"Failed to check metric thresholds: {e}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            # Get recent metrics (last hour)
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= datetime.now() - timedelta(hours=1)
            ]
            
            if not recent_metrics:
                return {
                    'status': 'unknown',
                    'message': 'No recent metrics available'
                }
            
            # Calculate averages
            avg_scraping_success = sum(m.scraping_success_rate for m in recent_metrics) / len(recent_metrics)
            avg_analysis_success = sum(m.analysis_success_rate for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
            total_errors = sum(m.error_count_last_hour for m in recent_metrics)
            
            # Determine overall health status
            active_critical_alerts = len([a for a in self.alerts if not a.resolved and a.level == 'critical'])
            active_error_alerts = len([a for a in self.alerts if not a.resolved and a.level == 'error'])
            active_warning_alerts = len([a for a in self.alerts if not a.resolved and a.level == 'warning'])
            
            if active_critical_alerts > 0:
                status = 'critical'
                message = f'{active_critical_alerts} critical alerts active'
            elif active_error_alerts > 0:
                status = 'degraded'
                message = f'{active_error_alerts} error alerts active'
            elif active_warning_alerts > 0:
                status = 'warning'
                message = f'{active_warning_alerts} warning alerts active'
            elif (avg_scraping_success >= self.thresholds['scraping_success_rate_min'] and
                  avg_analysis_success >= self.thresholds['analysis_success_rate_min'] and
                  avg_response_time <= self.thresholds['response_time_max_ms']):
                status = 'healthy'
                message = 'All systems operating normally'
            else:
                status = 'warning'
                message = 'Some metrics below optimal thresholds'
            
            return {
                'status': status,
                'message': message,
                'metrics': {
                    'scraping_success_rate': avg_scraping_success,
                    'analysis_success_rate': avg_analysis_success,
                    'avg_response_time_ms': avg_response_time,
                    'total_errors_last_hour': total_errors
                },
                'alerts': {
                    'critical': active_critical_alerts,
                    'error': active_error_alerts,
                    'warning': active_warning_alerts
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                'status': 'error',
                'message': f'Failed to determine system health: {e}'
            }
    
    def _send_email_alert(self, alert: Alert):
        """Send email notification for alert"""
        try:
            if not self.email_config['to_emails'] or not self.email_config['smtp_server']:
                logger.debug("Email alerts not configured, skipping email notification")
                return
            
            # Create email message
            msg = MimeMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = f"[Media Bias Detector] {alert.level.upper()}: {alert.title}"
            
            body = f"""
Alert Details:
- Level: {alert.level.upper()}
- Title: {alert.title}
- Message: {alert.message}
- Source: {alert.source}
- Timestamp: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

This is an automated alert from the Media Bias Detector monitoring system.
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            
            if self.email_config['smtp_username']:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for: {alert.title}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _cleanup_old_alerts(self):
        """Remove old alerts based on retention policy"""
        try:
            retention_days = self.config.get('alert_retention_days', 30)
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            initial_count = len(self.alerts)
            self.alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
            
            removed_count = initial_count - len(self.alerts)
            if removed_count > 0:
                logger.debug(f"Cleaned up {removed_count} old alerts")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {e}")
    
    def _cleanup_old_metrics(self):
        """Remove old metrics based on retention policy"""
        try:
            retention_days = self.config.get('metrics_retention_days', 7)
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            initial_count = len(self.metrics_history)
            self.metrics_history = [metric for metric in self.metrics_history if metric.timestamp >= cutoff_time]
            
            removed_count = initial_count - len(self.metrics_history)
            if removed_count > 0:
                logger.debug(f"Cleaned up {removed_count} old metrics")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
    
    def update_threshold(self, metric_name: str, value: float) -> bool:
        """Update a monitoring threshold"""
        try:
            if metric_name in self.thresholds:
                old_value = self.thresholds[metric_name]
                self.thresholds[metric_name] = value
                self._save_config()
                
                logger.info(f"Updated threshold {metric_name}: {old_value} -> {value}")
                return True
            else:
                logger.warning(f"Unknown threshold metric: {metric_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update threshold {metric_name}: {e}")
            return False
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [metric for metric in self.metrics_history if metric.timestamp >= cutoff_time]
        
        return [{
            'timestamp': metric.timestamp.isoformat(),
            'articles_scraped_last_hour': metric.articles_scraped_last_hour,
            'articles_analyzed_last_hour': metric.articles_analyzed_last_hour,
            'scraping_success_rate': metric.scraping_success_rate,
            'analysis_success_rate': metric.analysis_success_rate,
            'database_size_mb': metric.database_size_mb,
            'response_time_ms': metric.response_time_ms,
            'error_count_last_hour': metric.error_count_last_hour
        } for metric in recent_metrics]