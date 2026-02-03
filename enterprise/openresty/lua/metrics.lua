-- V-Player Enterprise Metrics Module
-- Professional Streaming Solution by Itassist Broadcast Solutions

local _M = {}

-- Prometheus metrics export
function _M.export_prometheus()
    local metrics = {
        "# HELP v_player_requests_total Total number of requests",
        "# TYPE v_player_requests_total counter",
        "v_player_requests_total " .. ngx.var.requests_total or "0",
        "",
        "# HELP v_player_connections_active Active connections",
        "# TYPE v_player_connections_active gauge", 
        "v_player_connections_active " .. ngx.var.connections_active or "0",
        "",
        "# HELP v_player_request_duration_seconds Request duration",
        "# TYPE v_player_request_duration_seconds histogram",
        "v_player_request_duration_seconds_sum " .. (ngx.var.request_time * 1000 or "0"),
        "v_player_request_duration_seconds_count " .. "1",
        "",
        "# HELP v_player_up V-Player server status",
        "# TYPE v_player_up gauge",
        "v_player_up 1"
    }
    
    ngx.say(table.concat(metrics, "\n"))
end

return _M
