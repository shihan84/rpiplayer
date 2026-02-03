import subprocess
import threading
import time
import logging
import re
from config import Config

class StreamDecoder:
    def __init__(self):
        self.active_streams = {}
        self.logger = logging.getLogger(__name__)
        
    def start_stream(self, stream_id, stream_url, stream_type):
        """Start decoding a stream using FFmpeg"""
        if stream_id in self.active_streams:
            self.stop_stream(stream_id)
            
        try:
            # Build FFmpeg command based on stream type
            ffmpeg_cmd = self._build_ffmpeg_command(stream_url, stream_type, stream_id)
            
            # Start FFmpeg process
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            # Store stream info
            self.active_streams[stream_id] = {
                'process': process,
                'url': stream_url,
                'type': stream_type,
                'start_time': time.time(),
                'status': 'starting'
            }
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_stream,
                args=(stream_id,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.logger.info(f"Started stream {stream_id} from {stream_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start stream {stream_id}: {str(e)}")
            return False
    
    def stop_stream(self, stream_id):
        """Stop a running stream"""
        if stream_id not in self.active_streams:
            return False
            
        stream_info = self.active_streams[stream_id]
        process = stream_info['process']
        
        try:
            process.terminate()
            # Give it a moment to terminate gracefully
            time.sleep(1)
            if process.poll() is None:
                process.kill()
                
            del self.active_streams[stream_id]
            self.logger.info(f"Stopped stream {stream_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping stream {stream_id}: {str(e)}")
            return False
    
    def _build_ffmpeg_command(self, stream_url, stream_type, stream_id):
        """Build FFmpeg command based on stream type"""
        base_cmd = [
            Config.FFMPEG_PATH,
            '-loglevel', Config.FFMPEG_LOG_LEVEL,
            '-stimeout', str(Config.STREAM_TIMEOUT * 1000000),  # microseconds
        ]
        
        # Input options based on stream type
        if stream_type.lower() == 'srt':
            input_opts = ['-i', f'srt://{stream_url}']
        elif stream_type.lower() == 'rtmp':
            input_opts = ['-i', f'rtmp://{stream_url}']
        elif stream_type.lower() == 'udp':
            input_opts = ['-i', f'udp://{stream_url}']
        else:
            # Default treat as URL
            input_opts = ['-i', stream_url]
        
        # Output options for Raspberry Pi hardware acceleration
        output_opts = [
            '-c:v', Config.VIDEO_CODEC,
            '-c:a', Config.AUDIO_CODEC,
            '-f', 'hls',
            '-hls_time', '2',
            '-hls_list_size', '3',
            '-hls_flags', 'delete_segments',
            f'/tmp/stream_{stream_id}.m3u8'
        ]
        
        return base_cmd + input_opts + output_opts
    
    def _monitor_stream(self, stream_id):
        """Monitor stream status and update"""
        stream_info = self.active_streams.get(stream_id)
        if not stream_info:
            return
            
        process = stream_info['process']
        
        while stream_id in self.active_streams:
            # Check if process is still running
            if process.poll() is not None:
                # Process has ended
                stream_info['status'] = 'stopped'
                break
                
            # Parse stderr for errors/info
            try:
                line = process.stderr.readline()
                if line:
                    self._parse_ffmpeg_output(stream_id, line.decode().strip())
            except:
                pass
                
            time.sleep(0.1)
    
    def _parse_ffmpeg_output(self, stream_id, line):
        """Parse FFmpeg output for status information"""
        stream_info = self.active_streams.get(stream_id)
        if not stream_info:
            return
            
        # Look for stream information
        if 'Stream #' in line and 'Video:' in line:
            stream_info['status'] = 'playing'
            
        # Look for errors
        if 'Error' in line or 'Failed' in line:
            stream_info['status'] = 'error'
            self.logger.error(f"Stream {stream_id} error: {line}")
    
    def get_stream_status(self, stream_id):
        """Get current status of a stream"""
        if stream_id not in self.active_streams:
            return {'status': 'not_found'}
            
        stream_info = self.active_streams[stream_id]
        process = stream_info['process']
        
        if process.poll() is not None:
            return {'status': 'stopped'}
            
        return {
            'status': stream_info['status'],
            'url': stream_info['url'],
            'type': stream_info['type'],
            'duration': time.time() - stream_info['start_time']
        }
    
    def get_all_streams(self):
        """Get status of all active streams"""
        return {
            stream_id: self.get_stream_status(stream_id)
            for stream_id in self.active_streams
        }
