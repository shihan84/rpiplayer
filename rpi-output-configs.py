#!/usr/bin/env python3
"""
V-Player Raspberry Pi Output Configuration
Professional Streaming Solution by Itassist Broadcast Solutions

This module provides Raspberry Pi specific video output configurations
that match the hardware capabilities of different Raspberry Pi models.
"""

import subprocess
import os
from typing import Dict, List, Tuple

class RaspberryPiOutputConfig:
    """Raspberry Pi video output configuration manager"""
    
    def __init__(self):
        self.config_file = "/boot/config.txt"
        self.cmdline_file = "/boot/cmdline.txt"
        self.supported_modes = self._get_supported_modes()
    
    def _get_supported_modes(self) -> Dict[str, List[Dict]]:
        """Get supported video modes for different Raspberry Pi outputs"""
        return {
            "hdmi": [
                # Official CEA Modes (hdmi_group=1) - TV Standards
                {"resolution": "640x480", "refresh": 60, "mode": "CEA 1", "description": "VGA (640x480)", "standard": "computer", "scan": "progressive"},
                {"resolution": "720x480", "refresh": 60, "mode": "CEA 2", "description": "480p (4:3)", "standard": "ntsc", "scan": "progressive"},
                {"resolution": "720x480", "refresh": 60, "mode": "CEA 3", "description": "480p (16:9)", "standard": "ntsc", "scan": "progressive"},
                {"resolution": "1280x720", "refresh": 60, "mode": "CEA 4", "description": "720p60 (ATSC)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 60, "mode": "CEA 5", "description": "1080i60 (ATSC)", "standard": "broadcast", "scan": "interlaced"},
                {"resolution": "720x480", "refresh": 60, "mode": "CEA 6", "description": "480i (4:3)", "standard": "ntsc", "scan": "interlaced"},
                {"resolution": "720x480", "refresh": 60, "mode": "CEA 7", "description": "480i (16:9)", "standard": "ntsc", "scan": "interlaced"},
                {"resolution": "1920x1080", "refresh": 60, "mode": "CEA 16", "description": "1080p60 (ATSC)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "720x576", "refresh": 50, "mode": "CEA 17", "description": "576p (4:3)", "standard": "pal", "scan": "progressive"},
                {"resolution": "720x576", "refresh": 50, "mode": "CEA 18", "description": "576p (16:9)", "standard": "pal", "scan": "progressive"},
                {"resolution": "1280x720", "refresh": 50, "mode": "CEA 19", "description": "720p50 (EBU)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 50, "mode": "CEA 20", "description": "1080i50 (EBU)", "standard": "broadcast", "scan": "interlaced"},
                {"resolution": "720x576", "refresh": 50, "mode": "CEA 21", "description": "576i (4:3)", "standard": "pal", "scan": "interlaced"},
                {"resolution": "720x576", "refresh": 50, "mode": "CEA 22", "description": "576i (16:9)", "standard": "pal", "scan": "interlaced"},
                {"resolution": "1920x1080", "refresh": 50, "mode": "CEA 31", "description": "1080p50 (EBU)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 24, "mode": "CEA 32", "description": "1080p24 (Cinema)", "standard": "cinema", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 25, "mode": "CEA 33", "description": "1080p25 (European Cinema)", "standard": "cinema", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 30, "mode": "CEA 34", "description": "1080p30 (North American Cinema)", "standard": "cinema", "scan": "progressive"},
                
                # Official DMT Modes (hdmi_group=2) - Computer Monitor Standards
                {"resolution": "640x480", "refresh": 60, "mode": "DMT 4", "description": "VGA 60Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "640x480", "refresh": 75, "mode": "DMT 6", "description": "VGA 75Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "800x600", "refresh": 60, "mode": "DMT 9", "description": "SVGA 60Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "800x600", "refresh": 75, "mode": "DMT 11", "description": "SVGA 75Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "1024x768", "refresh": 60, "mode": "DMT 16", "description": "XGA 60Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "1024x768", "refresh": 75, "mode": "DMT 18", "description": "XGA 75Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "1280x1024", "refresh": 60, "mode": "DMT 35", "description": "SXGA 60Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "1366x768", "refresh": 60, "mode": "DMT 81", "description": "HD 1366x768 60Hz", "standard": "computer", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 60, "mode": "DMT 82", "description": "Full HD 1080p60", "standard": "computer", "scan": "progressive"},
                {"resolution": "1280x720", "refresh": 60, "mode": "DMT 85", "description": "HD 720p60", "standard": "computer", "scan": "progressive"},
            ],
            "composite": [
                # Composite (RCA) - PAL/NTSC Standards
                {"resolution": "720x576", "refresh": 50, "mode": "PAL", "description": "PAL 625 (EBU)", "standard": "broadcast", "scan": "interlaced"},
                {"resolution": "720x480", "refresh": 60, "mode": "NTSC", "description": "NTSC 525 (ATSC)", "standard": "broadcast", "scan": "interlaced"},
            ],
            "dsi": [
                # DSI LCD Displays
                {"resolution": "800x480", "refresh": 60, "mode": "DSI", "description": "Official 7\" LCD", "standard": "display", "scan": "progressive"},
                {"resolution": "1024x600", "refresh": 60, "mode": "DSI", "description": "Waveshare 10\"", "standard": "display", "scan": "progressive"},
                {"resolution": "1280x800", "refresh": 60, "mode": "DSI", "description": "Waveshare 10.1\"", "standard": "display", "scan": "progressive"},
                {"resolution": "1280x400", "refresh": 60, "mode": "DSI", "description": "Waveshare 7.9\"", "standard": "display", "scan": "progressive"},
            ],
            "dpi": [
                # DPI LCD Panels
                {"resolution": "800x480", "refresh": 60, "mode": "DPI", "description": "Generic DPI LCD", "standard": "display", "scan": "progressive"},
                {"resolution": "1024x768", "refresh": 60, "mode": "DPI", "description": "Generic DPI LCD", "standard": "display", "scan": "progressive"},
                {"resolution": "1280x800", "refresh": 60, "mode": "DPI", "description": "Generic DPI LCD", "standard": "display", "scan": "progressive"},
                {"resolution": "1280x1024", "refresh": 60, "mode": "DPI", "description": "Generic DPI LCD", "standard": "display", "scan": "progressive"},
            ],
            "broadcast": [
                # Professional Broadcast Standards (via HDMI-SDI converters)
                {"resolution": "1920x1080", "refresh": 50, "mode": "CEA 20", "description": "1080i50 - HD-SDI (EBU/SMPTE 292M)", "standard": "broadcast", "scan": "interlaced"},
                {"resolution": "1920x1080", "refresh": 60, "mode": "CEA 5", "description": "1080i60 - HD-SDI (SMPTE 292M)", "standard": "broadcast", "scan": "interlaced"},
                {"resolution": "1920x1080", "refresh": 50, "mode": "CEA 31", "description": "1080p50 - 3G-SDI (SMPTE 424M)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 60, "mode": "CEA 16", "description": "1080p60 - 3G-SDI (SMPTE 424M)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "1280x720", "refresh": 50, "mode": "CEA 19", "description": "720p50 - HD-SDI (SMPTE 292M)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "1280x720", "refresh": 60, "mode": "CEA 4", "description": "720p60 - HD-SDI (SMPTE 292M)", "standard": "broadcast", "scan": "progressive"},
                {"resolution": "720x576", "refresh": 50, "mode": "CEA 21", "description": "625i50 - SD-SDI (EBU/SMPTE 259M)", "standard": "broadcast", "scan": "interlaced"},
                {"resolution": "720x480", "refresh": 60, "mode": "CEA 6", "description": "525i60 - SD-SDI (SMPTE 259M)", "standard": "broadcast", "scan": "interlaced"},
                {"resolution": "1920x1080", "refresh": 24, "mode": "CEA 32", "description": "1080p24 - Cinema (24fps)", "standard": "cinema", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 25, "mode": "CEA 33", "description": "1080p25 - European Cinema", "standard": "cinema", "scan": "progressive"},
                {"resolution": "1920x1080", "refresh": 30, "mode": "CEA 34", "description": "1080p30 - North American Cinema", "standard": "cinema", "scan": "progressive"},
            ]
        }
    
    def get_hdmi_group_mode(self, resolution: str, refresh: int) -> Tuple[str, str]:
        """Get HDMI group and mode for given resolution and refresh rate"""
        for mode in self.supported_modes["hdmi"]:
            if mode["resolution"] == resolution and mode["refresh"] == refresh:
                if "CEA" in mode["mode"]:
                    return "1", mode["mode"].split(" ")[1]  # CEA group
                else:
                    return "2", mode["mode"].split(" ")[1]  # DMT group
        return "1", "31"  # Default to 1080p60
    
    def configure_hdmi_output(self, resolution: str, refresh: int) -> bool:
        """Configure HDMI output with specified resolution and refresh rate"""
        try:
            group, mode = self.get_hdmi_group_mode(resolution, refresh)
            
            config_lines = [
                "# HDMI Output Configuration",
                f"hdmi_group={group}",
                f"hdmi_mode={mode}",
                "hdmi_drive=2",
                "hdmi_force_hotplug=1",
                "config_hdmi_boost=4",
                f"# {resolution} @ {refresh}Hz",
            ]
            
            return self._write_config(config_lines)
        except Exception as e:
            print(f"Error configuring HDMI output: {e}")
            return False
    
    def configure_composite_output(self, standard: str = "PAL") -> bool:
        """Configure composite (RCA) output"""
        try:
            config_lines = [
                "# Composite Output Configuration",
                "enable_overscan=1" if standard == "PAL" else "disable_overscan=1",
                "overscan_left=24" if standard == "PAL" else "overscan_left=0",
                "overscan_right=24" if standard == "PAL" else "overscan_right=0",
                "overscan_top=24" if standard == "PAL" else "overscan_top=0",
                "overscan_bottom=24" if standard == "PAL" else "overscan_bottom=0",
                f"# {standard} Standard",
            ]
            
            return self._write_config(config_lines)
        except Exception as e:
            print(f"Error configuring composite output: {e}")
            return False
    
    def configure_dsi_output(self, resolution: str) -> bool:
        """Configure DSI LCD output"""
        try:
            config_lines = [
                "# DSI LCD Configuration",
                "dtoverlay=vc4-kms-v3d",
                f"# DSI LCD {resolution}",
            ]
            
            # Add specific DSI configurations based on resolution
            if resolution == "800x480":
                config_lines.extend([
                    "dtoverlay=vc4-kms-dsi-7inch",
                    "dtparam=touch=1",
                ])
            
            return self._write_config(config_lines)
        except Exception as e:
            print(f"Error configuring DSI output: {e}")
            return False
    
    def configure_dpi_output(self, resolution: str, **kwargs) -> bool:
        """Configure DPI LCD output"""
        try:
            width, height = map(int, resolution.split('x'))
            
            config_lines = [
                "# DPI LCD Configuration",
                "dtoverlay=dpi24",
                f"dtparam=width={width}",
                f"dtparam=height={height}",
                "dtparam=depth=24",
                "dtparam=rgb_order=0",
                f"# DPI LCD {resolution}",
            ]
            
            # Add DPI specific parameters
            config_lines.extend([
                "dtparam=clkfreq=32000000",
                "dtparam=de-active=1",
                "dtparam=hsync-active=0",
                "dtparam=vsync-active=0",
                "dtparam=pwm-active=1",
                "dtparam=invert-pwm=1",
            ])
            
            return self._write_config(config_lines)
        except Exception as e:
            print(f"Error configuring DPI output: {e}")
            return False
    
    def configure_audio_output(self, output_type: str) -> bool:
        """Configure audio output"""
        try:
            config_lines = []
            
            if output_type == "hdmi":
                config_lines.extend([
                    "# HDMI Audio Configuration",
                    "dtparam=audio=on",
                    "hdmi_drive=2",
                ])
            elif output_type == "analog":
                config_lines.extend([
                    "# Analog Audio Configuration",
                    "dtparam=audio=on",
                    "hdmi_ignore_edid_audio=1",
                ])
            
            return self._write_config(config_lines)
        except Exception as e:
            print(f"Error configuring audio output: {e}")
            return False
    
    def _write_config(self, config_lines: List[str]) -> bool:
        """Write configuration lines to config.txt"""
        try:
            # Backup current config
            if os.path.exists(self.config_file):
                subprocess.run(['sudo', 'cp', self.config_file, f"{self.config_file}.backup"], 
                             check=True)
            
            # Read existing config
            existing_config = []
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    existing_config = f.readlines()
            
            # Remove existing output configurations
            filtered_config = []
            skip_output_config = False
            
            for line in existing_config:
                line_lower = line.lower().strip()
                if any(keyword in line_lower for keyword in [
                    "# hdmi output configuration",
                    "# composite output configuration", 
                    "# dsi lcd configuration",
                    "# dpi lcd configuration",
                    "# hdmi audio configuration",
                    "# analog audio configuration",
                    "hdmi_group=",
                    "hdmi_mode=",
                    "enable_overscan=",
                    "overscan_",
                    "dtoverlay=vc4-kms-dsi",
                    "dtoverlay=dpi24",
                    "dtparam=width=",
                    "dtparam=height=",
                    "hdmi_ignore_edid_audio="
                ]):
                    continue
                filtered_config.append(line)
            
            # Add new configuration
            filtered_config.extend(['\n'] + [line + '\n' for line in config_lines])
            
            # Write new config
            with open('/tmp/config.txt', 'w') as f:
                f.writelines(filtered_config)
            
            # Copy to system location
            subprocess.run(['sudo', 'cp', '/tmp/config.txt', self.config_file], check=True)
            
            return True
            
        except Exception as e:
            print(f"Error writing config: {e}")
            return False
    
    def get_current_config(self) -> Dict:
        """Get current video configuration"""
        config = {
            "output_type": "unknown",
            "resolution": "unknown",
            "refresh": 0,
            "audio": "unknown"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    content = f.read()
                
                # Parse current configuration
                if "dtoverlay=vc4-kms-dsi" in content:
                    config["output_type"] = "dsi"
                elif "dtoverlay=dpi24" in content:
                    config["output_type"] = "dpi"
                elif "hdmi_group=" in content:
                    config["output_type"] = "hdmi"
                elif "enable_overscan=1" in content:
                    config["output_type"] = "composite"
                
                # Extract HDMI mode if present
                if "hdmi_group=1" in content and "hdmi_mode=" in content:
                    for line in content.split('\n'):
                        if 'hdmi_mode=' in line:
                            mode_num = line.split('=')[1].strip()
                            # Map mode to resolution
                            for mode in self.supported_modes["hdmi"]:
                                if mode["mode"].endswith(mode_num):
                                    config["resolution"] = mode["resolution"]
                                    config["refresh"] = mode["refresh"]
                                    break
                
                # Audio configuration
                if "hdmi_ignore_edid_audio=1" in content:
                    config["audio"] = "analog"
                elif "dtparam=audio=on" in content:
                    config["audio"] = "hdmi"
        
        except Exception as e:
            print(f"Error reading current config: {e}")
        
        return config
    
    def apply_output_settings(self, settings: Dict) -> bool:
        """Apply complete output settings"""
        try:
            output_type = settings.get("video", "hdmi")
            
            # Configure video output
            if output_type == "hdmi":
                resolution = settings.get("hdmi_resolution", "1920x1080 @ 60Hz")
                res_part, refresh_part = resolution.split(" @ ")
                refresh = int(refresh_part.replace("Hz", ""))
                self.configure_hdmi_output(res_part, refresh)
            
            elif output_type == "composite":
                standard = settings.get("composite_standard", "PAL")
                self.configure_composite_output(standard)
            
            elif output_type == "dsi":
                resolution = settings.get("dsi_resolution", "800x480 @ 60Hz")
                res_part = resolution.split(" @ ")[0]
                self.configure_dsi_output(res_part)
            
            elif output_type == "dpi":
                resolution = settings.get("dpi_resolution", "800x480 @ 60Hz")
                res_part = resolution.split(" @ ")[0]
                self.configure_dpi_output(res_part)
            
            # Configure audio output
            audio_output = settings.get("audio", "hdmi")
            self.configure_audio_output(audio_output)
            
            return True
            
        except Exception as e:
            print(f"Error applying output settings: {e}")
            return False
    
    def reboot_required(self) -> bool:
        """Check if reboot is required for configuration changes"""
        return True  # Most video output changes require reboot
    
    def get_supported_outputs(self) -> Dict:
        """Get all supported output configurations"""
        return {
            "hdmi": {
                "name": "HDMI Output",
                "modes": self.supported_modes["hdmi"],
                "description": "High-definition digital output"
            },
            "composite": {
                "name": "Composite (RCA)",
                "modes": self.supported_modes["composite"],
                "description": "Analog standard definition output"
            },
            "dsi": {
                "name": "DSI Display",
                "modes": self.supported_modes["dsi"],
                "description": "Raspberry Pi official LCD displays"
            },
            "dpi": {
                "name": "DPI LCD Panel",
                "modes": self.supported_modes["dpi"],
                "description": "Generic DPI LCD panels"
            }
        }

# Example usage and testing
if __name__ == "__main__":
    config = RaspberryPiOutputConfig()
    
    # Get supported outputs
    outputs = config.get_supported_outputs()
    print("Supported Outputs:")
    for output_type, output_info in outputs.items():
        print(f"  {output_type}: {output_info['name']}")
        for mode in output_info['modes'][:2]:  # Show first 2 modes
            print(f"    - {mode['description']}")
    
    # Get current configuration
    current = config.get_current_config()
    print(f"\nCurrent Configuration: {current}")
    
    # Example: Configure HDMI 1080p60
    if config.configure_hdmi_output("1920x1080", 60):
        print("HDMI 1080p60 configured successfully")
    else:
        print("Failed to configure HDMI output")
