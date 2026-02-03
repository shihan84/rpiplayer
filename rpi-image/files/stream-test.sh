#!/bin/bash

# RPI Player Stream Testing Script
# Test various stream protocols and configurations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STREAMS_DIR="$SCRIPT_DIR/streams"
LOG_FILE="$SCRIPT_DIR/logs/stream-test.log"

# Create directories
mkdir -p "$STREAMS_DIR"
mkdir -p "$SCRIPT_DIR/logs"

show_help() {
    echo "RPI Player Stream Testing"
    echo "Usage: $0 [protocol] [test_type]"
    echo ""
    echo "Protocols:"
    echo "  srt       - Test SRT streams"
    echo "  rtmp      - Test RTMP streams"
    echo "  udp       - Test UDP streams"
    echo "  hls       - Test HLS streams"
    echo "  rtp       - Test RTP streams"
    echo "  all       - Test all protocols"
    echo ""
    echo "Test types:"
    echo "  receive   - Test receiving streams (default)"
    echo "  send      - Test sending streams"
    echo "  loopback  - Test loopback (send and receive)"
    echo ""
    echo "Examples:"
    echo "  $0 srt receive"
    echo "  $0 rtmp send"
    echo "  $0 all loopback"
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

test_srt_receive() {
    log "Testing SRT receive..."
    
    # Test with public SRT stream
    ffmpeg -y -i "srt://fms.rtl.be:1936/live/rtl-2" \
        -c:v h264_v4l2m2m -c:a aac \
        -f hls -hls_time 2 -hls_list_size 3 \
        "$STREAMS_DIR/srt_test.m3u8" \
        -t 30 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "SRT receive test: SUCCESS"
    else
        log "SRT receive test: FAILED"
    fi
}

test_srt_send() {
    log "Testing SRT send..."
    
    # Generate test video and send via SRT
    ffmpeg -y -f lavfi -i testsrc=duration=30:size=640x480:rate=25 \
        -f lavfi -i sine=frequency=1000:duration=30 \
        -c:v h264_v4l2m2m -c:a aac \
        -f srt "srt://127.0.0.1:1234" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "SRT send test: SUCCESS"
    else
        log "SRT send test: FAILED"
    fi
}

test_rtmp_receive() {
    log "Testing RTMP receive..."
    
    # Test with public RTMP stream
    ffmpeg -y -i "rtmp://live.twitch.tv/live/test" \
        -c:v h264_v4l2m2m -c:a aac \
        -f hls -hls_time 2 -hls_list_size 3 \
        "$STREAMS_DIR/rtmp_test.m3u8" \
        -t 30 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "RTMP receive test: SUCCESS"
    else
        log "RTMP receive test: FAILED"
    fi
}

test_rtmp_send() {
    log "Testing RTMP send..."
    
    # Generate test video and send via RTMP
    ffmpeg -y -f lavfi -i testsrc=duration=30:size=640x480:rate=25 \
        -f lavfi -i sine=frequency=1000:duration=30 \
        -c:v h264_v4l2m2m -c:a aac \
        -f flv "rtmp://127.0.0.1:1935/live/test" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "RTMP send test: SUCCESS"
    else
        log "RTMP send test: FAILED"
    fi
}

test_udp_receive() {
    log "Testing UDP receive..."
    
    # Test UDP stream
    ffmpeg -y -i "udp://239.0.0.1:1234" \
        -c:v h264_v4l2m2m -c:a aac \
        -f hls -hls_time 2 -hls_list_size 3 \
        "$STREAMS_DIR/udp_test.m3u8" \
        -t 30 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "UDP receive test: SUCCESS"
    else
        log "UDP receive test: FAILED"
    fi
}

test_udp_send() {
    log "Testing UDP send..."
    
    # Generate test video and send via UDP
    ffmpeg -y -f lavfi -i testsrc=duration=30:size=640x480:rate=25 \
        -f lavfi -i sine=frequency=1000:duration=30 \
        -c:v h264_v4l2m2m -c:a aac \
        -f mpegts "udp://239.0.0.1:1234" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "UDP send test: SUCCESS"
    else
        log "UDP send test: FAILED"
    fi
}

test_hls_receive() {
    log "Testing HLS receive..."
    
    # Test with public HLS stream
    ffmpeg -y -i "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" \
        -c:v h264_v4l2m2m -c:a aac \
        -f hls -hls_time 2 -hls_list_size 3 \
        "$STREAMS_DIR/hls_test.m3u8" \
        -t 30 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "HLS receive test: SUCCESS"
    else
        log "HLS receive test: FAILED"
    fi
}

test_hls_send() {
    log "Testing HLS send..."
    
    # Generate test video and create HLS
    ffmpeg -y -f lavfi -i testsrc=duration=30:size=640x480:rate=25 \
        -f lavfi -i sine=frequency=1000:duration=30 \
        -c:v h264_v4l2m2m -c:a aac \
        -f hls -hls_time 2 -hls_list_size 3 \
        "$STREAMS_DIR/hls_output.m3u8" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "HLS send test: SUCCESS"
    else
        log "HLS send test: FAILED"
    fi
}

test_rtp_receive() {
    log "Testing RTP receive..."
    
    # Test RTP stream
    ffmpeg -y -i "rtp://127.0.0.1:5004" \
        -c:v h264_v4l2m2m -c:a aac \
        -f hls -hls_time 2 -hls_list_size 3 \
        "$STREAMS_DIR/rtp_test.m3u8" \
        -t 30 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "RTP receive test: SUCCESS"
    else
        log "RTP receive test: FAILED"
    fi
}

test_rtp_send() {
    log "Testing RTP send..."
    
    # Generate test video and send via RTP
    ffmpeg -y -f lavfi -i testsrc=duration=30:size=640x480:rate=25 \
        -f lavfi -i sine=frequency=1000:duration=30 \
        -c:v h264_v4l2m2m -c:a aac \
        -f rtp "rtp://127.0.0.1:5004" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "RTP send test: SUCCESS"
    else
        log "RTP send test: FAILED"
    fi
}

cleanup() {
    log "Cleaning up test files..."
    rm -f "$STREAMS_DIR"/*_test.*
    log "Cleanup complete"
}

# Main script logic
PROTOCOL="${1:-all}"
TEST_TYPE="${2:-receive}"

log "Starting stream tests: $PROTOCOL ($TEST_TYPE)"

case "$PROTOCOL" in
    srt)
        case "$TEST_TYPE" in
            receive) test_srt_receive ;;
            send) test_srt_send ;;
            loopback) test_srt_send && sleep 2 && test_srt_receive ;;
        esac
        ;;
    rtmp)
        case "$TEST_TYPE" in
            receive) test_rtmp_receive ;;
            send) test_rtmp_send ;;
            loopback) test_rtmp_send && sleep 2 && test_rtmp_receive ;;
        esac
        ;;
    udp)
        case "$TEST_TYPE" in
            receive) test_udp_receive ;;
            send) test_udp_send ;;
            loopback) test_udp_send && sleep 2 && test_udp_receive ;;
        esac
        ;;
    hls)
        case "$TEST_TYPE" in
            receive) test_hls_receive ;;
            send) test_hls_send ;;
            loopback) test_hls_send && sleep 2 && test_hls_receive ;;
        esac
        ;;
    rtp)
        case "$TEST_TYPE" in
            receive) test_rtp_receive ;;
            send) test_rtp_send ;;
            loopback) test_rtp_send && sleep 2 && test_rtp_receive ;;
        esac
        ;;
    all)
        test_srt_receive
        test_rtmp_receive
        test_udp_receive
        test_hls_receive
        test_rtp_receive
        
        if [ "$TEST_TYPE" = "loopback" ]; then
            test_srt_send
            test_rtmp_send
            test_udp_send
            test_hls_send
            test_rtp_send
        fi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown protocol: $PROTOCOL"
        show_help
        exit 1
        ;;
esac

cleanup
log "Stream testing complete"
