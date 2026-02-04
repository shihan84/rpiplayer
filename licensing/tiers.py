"""
V-Player Enterprise License Tiers

Copyright © 2026 ITAssist Broadcast Solutions
All rights reserved.
"""

from enum import Enum
from typing import Dict, List, Any
from datetime import datetime, timedelta

class LicenseType(Enum):
    """License types available for V-Player Enterprise"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"

class LicenseTier:
    """License tier configuration and feature management"""
    
    def __init__(self, license_type: LicenseType):
        self.license_type = license_type
        self.features = self._get_features_for_tier()
        self.limits = self._get_limits_for_tier()
        self.pricing = self._get_pricing_for_tier()
        
    def _get_features_for_tier(self) -> Dict[str, bool]:
        """Get available features for each license tier"""
        features_map = {
            LicenseType.TRIAL: {
                "streaming": True,
                "basic_outputs": True,
                "network_config": True,
                "system_monitoring": True,
                "api_access": True,
                "telegram_notifications": False,
                "advanced_outputs": False,
                "cloudflare_integration": False,
                "multi_stream": False,
                "hd_streaming": True,
                "4k_streaming": False,
                "commercial_use": False,
                "priority_support": False,
                "custom_branding": False,
                "advanced_analytics": False,
                "remote_management": False,
                "license_transfer": False
            },
            LicenseType.BASIC: {
                "streaming": True,
                "basic_outputs": True,
                "network_config": True,
                "system_monitoring": True,
                "api_access": True,
                "telegram_notifications": False,
                "advanced_outputs": False,
                "cloudflare_integration": False,
                "multi_stream": False,
                "hd_streaming": True,
                "4k_streaming": False,
                "commercial_use": False,
                "priority_support": False,
                "custom_branding": False,
                "advanced_analytics": False,
                "remote_management": False,
                "license_transfer": True
            },
            LicenseType.PROFESSIONAL: {
                "streaming": True,
                "basic_outputs": True,
                "network_config": True,
                "system_monitoring": True,
                "api_access": True,
                "telegram_notifications": True,
                "advanced_outputs": True,
                "cloudflare_integration": True,
                "multi_stream": True,
                "hd_streaming": True,
                "4k_streaming": False,
                "commercial_use": True,
                "priority_support": True,
                "custom_branding": False,
                "advanced_analytics": True,
                "remote_management": True,
                "license_transfer": True
            },
            LicenseType.ENTERPRISE: {
                "streaming": True,
                "basic_outputs": True,
                "network_config": True,
                "system_monitoring": True,
                "api_access": True,
                "telegram_notifications": True,
                "advanced_outputs": True,
                "cloudflare_integration": True,
                "multi_stream": True,
                "hd_streaming": True,
                "4k_streaming": True,
                "commercial_use": True,
                "priority_support": True,
                "custom_branding": True,
                "advanced_analytics": True,
                "remote_management": True,
                "license_transfer": True
            }
        }
        return features_map.get(self.license_type, {})
    
    def _get_limits_for_tier(self) -> Dict[str, Any]:
        """Get limits for each license tier"""
        limits_map = {
            LicenseType.TRIAL: {
                "max_streams": 2,
                "max_outputs": 1,
                "max_resolution": "1920x1080",
                "max_bitrate": "5000k",
                "trial_days": 30,
                "max_users": 1,
                "api_rate_limit": 100,
                "storage_limit": "1GB"
            },
            LicenseType.BASIC: {
                "max_streams": 3,
                "max_outputs": 2,
                "max_resolution": "1920x1080",
                "max_bitrate": "5000k",
                "trial_days": None,
                "max_users": 2,
                "api_rate_limit": 500,
                "storage_limit": "5GB"
            },
            LicenseType.PROFESSIONAL: {
                "max_streams": 10,
                "max_outputs": 5,
                "max_resolution": "1920x1080",
                "max_bitrate": "10000k",
                "trial_days": None,
                "max_users": 10,
                "api_rate_limit": 2000,
                "storage_limit": "50GB"
            },
            LicenseType.ENTERPRISE: {
                "max_streams": -1,  # Unlimited
                "max_outputs": -1,  # Unlimited
                "max_resolution": "3840x2160",  # 4K
                "max_bitrate": "25000k",
                "trial_days": None,
                "max_users": -1,  # Unlimited
                "api_rate_limit": -1,  # Unlimited
                "storage_limit": "-1"  # Unlimited
            }
        }
        return limits_map.get(self.license_type, {})
    
    def _get_pricing_for_tier(self) -> Dict[str, Any]:
        """Get pricing information for each license tier"""
        pricing_map = {
            LicenseType.TRIAL: {
                "monthly": 0,
                "yearly": 0,
                "perpetual": None,
                "setup_fee": 0,
                "currency": "USD"
            },
            LicenseType.BASIC: {
                "monthly": 29,
                "yearly": 290,
                "perpetual": 599,
                "setup_fee": 0,
                "currency": "USD"
            },
            LicenseType.PROFESSIONAL: {
                "monthly": 99,
                "yearly": 990,
                "perpetual": 1999,
                "setup_fee": 0,
                "currency": "USD"
            },
            LicenseType.ENTERPRISE: {
                "monthly": 299,
                "yearly": 2990,
                "perpetual": 5999,
                "setup_fee": 500,
                "currency": "USD"
            }
        }
        return pricing_map.get(self.license_type, {})
    
    def has_feature(self, feature: str) -> bool:
        """Check if the license tier has a specific feature"""
        return self.features.get(feature, False)
    
    def get_limit(self, limit_name: str) -> Any:
        """Get a specific limit for this license tier"""
        return self.limits.get(limit_name, 0)
    
    def can_add_stream(self, current_streams: int) -> bool:
        """Check if we can add more streams"""
        max_streams = self.get_limit("max_streams")
        if max_streams == -1:  # Unlimited
            return True
        return current_streams < max_streams
    
    def can_use_resolution(self, resolution: str) -> bool:
        """Check if the license tier supports a specific resolution"""
        max_res = self.get_limit("max_resolution")
        if max_res == "3840x2160":  # 4K supports all
            return True
        elif max_res == "1920x1080":  # 1080p max
            return resolution in ["1920x1080", "1280x720", "854x480", "640x360"]
        else:
            return resolution == max_res
    
    def get_tier_name(self) -> str:
        """Get human-readable tier name"""
        names = {
            LicenseType.TRIAL: "Trial",
            LicenseType.BASIC: "Basic",
            LicenseType.PROFESSIONAL: "Professional",
            LicenseType.ENTERPRISE: "Enterprise"
        }
        return names.get(self.license_type, "Unknown")
    
    def get_description(self) -> str:
        """Get description of the license tier"""
        descriptions = {
            LicenseType.TRIAL: "30-day trial with basic features for evaluation",
            LicenseType.BASIC: "Essential features for small-scale streaming",
            LicenseType.PROFESSIONAL: "Advanced features for professional broadcasting",
            LicenseType.ENTERPRISE: "Complete solution with unlimited capabilities and priority support"
        }
        return descriptions.get(self.license_type, "No description available")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert license tier to dictionary"""
        return {
            "type": self.license_type.value,
            "name": self.get_tier_name(),
            "description": self.get_description(),
            "features": self.features,
            "limits": self.limits,
            "pricing": self.pricing
        }

# License tier factory
def get_license_tier(license_type: str) -> LicenseTier:
    """Get license tier by type string"""
    try:
        license_enum = LicenseType(license_type.lower())
        return LicenseTier(license_enum)
    except ValueError:
        return LicenseTier(LicenseType.BASIC)  # Default to basic

def get_all_tiers() -> List[Dict[str, Any]]:
    """Get all available license tiers"""
    return [LicenseTier(tier_type).to_dict() for tier_type in LicenseType]
