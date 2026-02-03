-- V-Player Enterprise Stream Handler
-- Professional Streaming Solution by Itassist Broadcast Solutions

local cjson = require "cjson"
local redis = require "resty.redis"

local _M = {}

-- Redis connection
local function get_redis()
    local red = redis:new()
    red:set_timeout(1000)
    
    local ok, err = red:connect("127.0.0.1", 6379)
    if not ok then
        ngx.log(ngx.ERR, "Failed to connect to Redis: ", err)
        return nil
    end
    
    return red
end

-- Handle stream requests
function _M.handle_stream_request(vars)
    local uri = vars.uri
    local args = ngx.req.get_uri_args()
    local stream_id = args.id
    
    if not stream_id then
        ngx.status = 400
        ngx.say("Stream ID required")
        ngx.exit(400)
    end
    
    -- Get stream info from cache
    local red = get_redis()
    if not red then
        ngx.status = 500
        ngx.say("Internal server error")
        ngx.exit(500)
    end
    
    local stream_info, err = red:get("stream:" .. stream_id)
    if not stream_info or stream_info == ngx.null then
        red:close()
        ngx.status = 404
        ngx.say("Stream not found")
        ngx.exit(404)
    end
    
    -- Parse stream info
    local stream = cjson.decode(stream_info)
    
    -- Add CORS headers
    ngx.header["Access-Control-Allow-Origin"] = "*"
    ngx.header["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    ngx.header["Access-Control-Allow-Headers"] = "Range"
    ngx.header["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    -- Handle different stream types
    if string.find(uri, "%.m3u8$") then
        -- HLS playlist
        ngx.header["Content-Type"] = "application/vnd.apple.mpegurl"
        ngx.exec("/internal/hls/" .. stream_id .. "/playlist.m3u8")
    elseif string.find(uri, "%.ts$") then
        -- HLS segment
        ngx.header["Content-Type"] = "video/MP2T"
        ngx.exec("/internal/hls/" .. stream_id .. "/" .. ngx.var.uri)
    elseif string.find(uri, "%.mpd$") then
        -- DASH manifest
        ngx.header["Content-Type"] = "application/dash+xml"
        ngx.exec("/internal/dash/" .. stream_id .. "/manifest.mpd")
    else
        -- Direct stream proxy
        ngx.exec("/internal/stream/" .. stream_id)
    end
    
    red:close()
end

return _M
