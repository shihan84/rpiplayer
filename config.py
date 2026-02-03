import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rpi-player-secret-key'
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    
    # FFmpeg settings
    FFMPEG_PATH = '/usr/bin/ffmpeg'
    FFMPEG_LOG_LEVEL = 'error'
    
    # Stream settings
    MAX_STREAMS = 4
    STREAM_TIMEOUT = 30  # seconds
    
    # Video output settings for Raspberry Pi
    VIDEO_CODEC = 'h264_v4l2m2m'
    AUDIO_CODEC = 'aac'
    
    # Hardware acceleration for RPi3
    HWACCEL = 'h264_mmal'
