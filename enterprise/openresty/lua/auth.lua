-- V-Player Enterprise Authentication Module
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

-- Validate JWT token
function _M.validate_request(vars)
    local auth_header = vars.http_authorization
    
    if not auth_header then
        ngx.log(ngx.WARN, "No authorization header")
        return false
    end
    
    -- Extract token from Bearer
    local _, _, token = string.find(auth_header, "Bearer%s+(.+)")
    if not token then
        ngx.log(ngx.WARN, "Invalid authorization format")
        return false
    end
    
    -- Check cache first
    local red = get_redis()
    if red then
        local cached, err = red:get("auth:" .. token)
        if cached and cached ~= ngx.null then
            red:close()
            return true
        end
    end
    
    -- Simple token validation (in production, use proper JWT)
    if string.len(token) >= 20 then
        -- Cache valid token
        if red then
            red:setex("auth:" .. token, 3600, "valid")
            red:close()
        end
        return true
    end
    
    return false
end

-- Rate limiting
function _M.rate_limit(key, limit, window)
    local red = get_redis()
    if not red then
        return true -- Allow if Redis is down
    end
    
    local current, err = red:incr(key)
    if current == 1 then
        red:expire(key, window)
    end
    
    red:close()
    
    return current <= limit
end

return _M
