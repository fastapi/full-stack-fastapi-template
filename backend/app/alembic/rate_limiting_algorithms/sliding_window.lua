-- KEYS[1] = key
-- ARGV[1] = now_ms
-- ARGV[2] = window_ms
-- ARGV[3] = limit
-- ARGV[4] = member

local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]

local min_score = now - window

-- remove old entries
redis.call('ZREMRANGEBYSCORE', key, 0, min_score)

-- add current
redis.call('ZADD', key, now, member)

-- count
local cnt = redis.call('ZCARD', key)

-- expire same as window
redis.call('PEXPIRE', key, window)

-- fetch oldest
local earliest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
local oldest_ts = 0
if earliest ~= false and earliest ~= nil and #earliest >= 2 then
  oldest_ts = earliest[2]
end

return {cnt, oldest_ts}