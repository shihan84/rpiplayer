"""
Telegram Configuration for V-Player Enterprise

Copyright © 2026 ITAssist Broadcast Solutions
All rights reserved.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TelegramConfig:
    """Configuration for Telegram bot integration"""
    
    # Bot Configuration
    bot_token: str = ""
    chat_id: str = ""
    
    # Notification Settings
    enable_notifications: bool = True
    notify_on_stream_drop: bool = True
    notify_on_stream_recovery: bool = True
    notify_on_quality_change: bool = True
    notify_on_system_alerts: bool = True
    
    # Rate Limiting
    notification_cooldown: int = 300  # 5 minutes
    max_notifications_per_hour: int = 20
    
    # Quiet Hours
    enable_quiet_hours: bool = False
    quiet_hours_start: str = "22:00"  # 10 PM
    quiet_hours_end: str = "08:00"    # 8 AM
    
    # Message Templates
    stream_drop_template: str = "🚨 *Stream Alert*\n\nStream '{stream_name}' has dropped!\n\n📊 Details:\n• URL: {url}\n• Duration: {duration}\n• Time: {time}"
    stream_recovery_template: str = "✅ *Stream Recovery*\n\nStream '{stream_name}' is back online!\n\n📊 Details:\n• URL: {url}\n• Downtime: {downtime}\n• Time: {time}"
    quality_change_template: str = "📊 *Quality Change*\n\nStream '{stream_name}' quality changed!\n\n📈 Details:\n• From: {old_quality}\n• To: {new_quality}\n• Time: {time}"
    system_alert_template: str = "⚠️ *System Alert*\n\n{alert_type}\n\n📊 Details:\n• Message: {message}\n• Time: {time}"
    
    # Command Permissions
    allowed_users: List[str] = None  # List of Telegram user IDs
    admin_users: List[str] = None     # Admin user IDs with full access
    
    # Stream Management
    allow_stream_management: bool = True
    max_streams_per_user: int = 5
    allow_quality_control: bool = True
    
    def __post_init__(self):
        """Initialize default values"""
        if self.allowed_users is None:
            self.allowed_users = []
        if self.admin_users is None:
            self.admin_users = []
    
    @classmethod
    def from_env(cls) -> 'TelegramConfig':
        """Load configuration from environment variables"""
        return cls(
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            chat_id=os.getenv('TELEGRAM_CHAT_ID', ''),
            enable_notifications=os.getenv('TELEGRAM_ENABLE_NOTIFICATIONS', 'true').lower() == 'true',
            notify_on_stream_drop=os.getenv('TELEGRAM_NOTIFY_STREAM_DROP', 'true').lower() == 'true',
            notify_on_stream_recovery=os.getenv('TELEGRAM_NOTIFY_STREAM_RECOVERY', 'true').lower() == 'true',
            notify_on_quality_change=os.getenv('TELEGRAM_NOTIFY_QUALITY_CHANGE', 'true').lower() == 'true',
            notify_on_system_alerts=os.getenv('TELEGRAM_NOTIFY_SYSTEM_ALERTS', 'true').lower() == 'true',
            notification_cooldown=int(os.getenv('TELEGRAM_NOTIFICATION_COOLDOWN', '300')),
            max_notifications_per_hour=int(os.getenv('TELEGRAM_MAX_NOTIFICATIONS_PER_HOUR', '20')),
            enable_quiet_hours=os.getenv('TELEGRAM_ENABLE_QUIET_HOURS', 'false').lower() == 'true',
            quiet_hours_start=os.getenv('TELEGRAM_QUIET_HOURS_START', '22:00'),
            quiet_hours_end=os.getenv('TELEGRAM_QUIET_HOURS_END', '08:00'),
            allowed_users=os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',') if os.getenv('TELEGRAM_ALLOWED_USERS') else [],
            admin_users=os.getenv('TELEGRAM_ADMIN_USERS', '').split(',') if os.getenv('TELEGRAM_ADMIN_USERS') else [],
            allow_stream_management=os.getenv('TELEGRAM_ALLOW_STREAM_MANAGEMENT', 'true').lower() == 'true',
            max_streams_per_user=int(os.getenv('TELEGRAM_MAX_STREAMS_PER_USER', '5')),
            allow_quality_control=os.getenv('TELEGRAM_ALLOW_QUALITY_CONTROL', 'true').lower() == 'true'
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'TelegramConfig':
        """Load configuration from dictionary"""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'bot_token': self.bot_token,
            'chat_id': self.chat_id,
            'enable_notifications': self.enable_notifications,
            'notify_on_stream_drop': self.notify_on_stream_drop,
            'notify_on_stream_recovery': self.notify_on_stream_recovery,
            'notify_on_quality_change': self.notify_on_quality_change,
            'notify_on_system_alerts': self.notify_on_system_alerts,
            'notification_cooldown': self.notification_cooldown,
            'max_notifications_per_hour': self.max_notifications_per_hour,
            'enable_quiet_hours': self.enable_quiet_hours,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'stream_drop_template': self.stream_drop_template,
            'stream_recovery_template': self.stream_recovery_template,
            'quality_change_template': self.quality_change_template,
            'system_alert_template': self.system_alert_template,
            'allowed_users': self.allowed_users,
            'admin_users': self.admin_users,
            'allow_stream_management': self.allow_stream_management,
            'max_streams_per_user': self.max_streams_per_user,
            'allow_quality_control': self.allow_quality_control
        }
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self.bot_token and self.chat_id)
    
    def is_user_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to use the bot"""
        return not self.allowed_users or user_id in self.allowed_users
    
    def is_user_admin(self, user_id: str) -> bool:
        """Check if user is an admin"""
        return user_id in self.admin_users
    
    def get_stream_protocols(self) -> List[str]:
        """Get supported streaming protocols"""
        return ['srt', 'rtmp', 'udp', 'hls', 'rtsp']
    
    def get_resolutions(self) -> List[str]:
        """Get supported resolutions"""
        return ['3840x2160', '1920x1080', '1280x720', '854x480', '640x360']
    
    def get_bitrates(self) -> List[str]:
        """Get supported bitrates"""
        return ['25000k', '10000k', '5000k', '2500k', '1000k', '500k']

# Default configuration
DEFAULT_CONFIG = TelegramConfig()

# Configuration validation
def validate_config(config: TelegramConfig) -> List[str]:
    """Validate Telegram configuration and return list of errors"""
    errors = []
    
    if not config.bot_token:
        errors.append("Bot token is required")
    
    if not config.chat_id:
        errors.append("Chat ID is required")
    
    if config.notification_cooldown < 0:
        errors.append("Notification cooldown must be non-negative")
    
    if config.max_notifications_per_hour < 1:
        errors.append("Max notifications per hour must be at least 1")
    
    if config.max_streams_per_user < 1:
        errors.append("Max streams per user must be at least 1")
    
    return errors
