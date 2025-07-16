# Rate Limiting Implementation

This document describes the rate limiting implementation for the FastAPI application.

## Overview

Rate limiting has been implemented using `slowapi` library with Redis as the backend storage. This helps prevent abuse and ensures fair usage of the API resources.

## Configuration

### Default Limits
- **200 requests per day** (global default)
- **50 requests per hour** (global default)

### Endpoint-Specific Limits
- **`/api/v2/qna`**: 10 requests per minute (most restrictive due to resource-intensive operations)
- **`/api/v1/health`**: 30 requests per minute (more lenient for monitoring)
- **`/`**: 20 requests per minute (root endpoint)

## Dependencies

- `slowapi==0.1.9` - FastAPI rate limiting library
- `redis` - Backend storage for rate limiting data

## Setup

### 1. Install Dependencies
```bash
pip install slowapi==0.1.9
```

### 2. Redis Setup
Make sure Redis is running on your system:
```bash
# On macOS with Homebrew
brew install redis
brew services start redis

# On Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# On Windows
# Download and install Redis from https://redis.io/download
```

### 3. Configuration
Rate limiting configuration is stored in `service/rate_limit_config.py`. You can modify:
- Default rate limits
- Endpoint-specific limits
- Redis connection settings

## Usage

### Rate Limit Headers
When rate limiting is active, the following headers are included in responses:
- `X-RateLimit-Limit`: The rate limit ceiling for the given request
- `X-RateLimit-Remaining`: The number of requests left for the time window
- `X-RateLimit-Reset`: The time when the rate limit window resets

### Rate Limit Exceeded Response
When rate limit is exceeded, the API returns:
- **Status Code**: 429 (Too Many Requests)
- **Headers**: Include `Retry-After` header indicating when to retry
- **Body**: JSON error message

Example response:
```json
{
  "error": "Rate limit exceeded",
  "detail": "10 per 1 minute"
}
```

## Testing

Use the provided test script to verify rate limiting:
```bash
python test_rate_limit.py
```

This script will:
1. Test the QnA endpoint rate limiting (10 requests/minute)
2. Test the health endpoint rate limiting (30 requests/minute)
3. Show success/failure counts

## Monitoring

### Redis Monitoring
You can monitor rate limiting data in Redis:
```bash
redis-cli
> KEYS "*"  # Show all rate limiting keys
> TTL <key>  # Check time-to-live for a specific key
```

### Application Logs
The application logs will show:
- Redis connection status
- Rate limiting events (if logging is enabled)

## Customization

### Changing Rate Limits
Modify `service/rate_limit_config.py`:
```python
ENDPOINT_LIMITS = {
    "/api/v2/qna": "5 per minute",  # More restrictive
    "/api/v1/health": "60 per minute",  # More lenient
}
```

### Custom Rate Limit Keys
You can implement custom key functions for different rate limiting strategies:
```python
def get_user_id(request: Request):
    # Rate limit by user ID instead of IP
    return request.headers.get("user-id", "anonymous")

limiter = Limiter(key_func=get_user_id, ...)
```

### Different Storage Backends
- **Redis**: `redis://localhost:6379` (recommended for production)
- **Memory**: `memory://` (for development/testing)
- **Memcached**: `memcached://localhost:11211`

## Production Considerations

1. **Redis High Availability**: Use Redis Cluster or Sentinel for production
2. **Rate Limit Strategy**: Consider different limits for authenticated vs anonymous users
3. **Monitoring**: Set up alerts for high rate limiting events
4. **Graceful Degradation**: Handle Redis failures gracefully
5. **Load Balancing**: Ensure rate limiting works correctly behind load balancers

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running
   - Check Redis configuration in `rate_limit_config.py`
   - Falls back to in-memory storage if Redis is unavailable

2. **Rate Limits Too Restrictive**
   - Adjust limits in `rate_limit_config.py`
   - Consider different limits for different user types

3. **Rate Limiting Not Working**
   - Check that SlowAPIMiddleware is properly added
   - Verify that endpoints have `@limiter.limit()` decorators
   - Ensure Request parameter is included in endpoint functions

### Debug Mode
To debug rate limiting, you can add logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Implementation Details

### Files Modified/Created:
- `service/api_main.py` - Main API file with rate limiting middleware
- `service/rate_limit_config.py` - Configuration file for rate limits
- `requirements.txt` - Added slowapi dependency
- `test_rate_limit.py` - Testing script for rate limiting
- `RATE_LIMITING.md` - This documentation file

### Key Components:
1. **Limiter Setup**: Configured with Redis backend and fallback to memory
2. **Middleware Integration**: SlowAPIMiddleware added to FastAPI app
3. **Endpoint Decorators**: Each endpoint decorated with specific rate limits
4. **Error Handling**: Custom error handler for rate limit exceeded responses
5. **Configuration Management**: Centralized configuration for easy modifications

## Next Steps

1. **Start Redis**: Ensure Redis is running on your system
2. **Test Implementation**: Use the test script to verify functionality
3. **Monitor Usage**: Set up monitoring for rate limiting metrics
4. **Adjust Limits**: Fine-tune rate limits based on actual usage patterns
5. **Production Setup**: Configure Redis clustering for production deployment
