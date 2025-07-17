"""
Rate limiting configuration for the API
"""

# Rate limiting strategy options:
# - "ip": Rate limit by IP address (default)
# - "global": Rate limit globally across all users
# - "user_id": Rate limit by user ID (requires authentication)
# - "api_key": Rate limit by API key
# - "combined": Rate limit by combination of IP and user
# - "endpoint_specific": Rate limit by endpoint and IP combination
RATE_LIMIT_STRATEGY = "ip"  # Change this to switch strategies

# Default rate limits
DEFAULT_LIMITS = ["200 per day", "50 per hour"]

# Endpoint-specific rate limits for IP-based limiting
IP_ENDPOINT_LIMITS = {
    "/api/v2/qna": "10 per minute",  # QnA endpoint - more restrictive per IP
    "/api/v1/health": "30 per minute",  # Health check - more lenient per IP
    "/": "20 per minute",  # Root endpoint per IP
}

# Global rate limits (applied across all users)
GLOBAL_ENDPOINT_LIMITS = {
    "/api/v2/qna": "100 per minute",  # QnA endpoint - global limit
    "/api/v1/health": "500 per minute",  # Health check - global limit
    "/": "200 per minute",  # Root endpoint - global limit
}

# User-based rate limits (per authenticated user)
USER_ENDPOINT_LIMITS = {
    "/api/v2/qna": "20 per minute",  # QnA endpoint - per user
    "/api/v1/health": "60 per minute",  # Health check - per user
    "/": "40 per minute",  # Root endpoint - per user
}

# API key-based rate limits
API_KEY_ENDPOINT_LIMITS = {
    "/api/v2/qna": "50 per minute",  # QnA endpoint - per API key
    "/api/v1/health": "100 per minute",  # Health check - per API key
    "/": "80 per minute",  # Root endpoint - per API key
}

# Get the appropriate limits based on strategy
def get_endpoint_limits():
    if RATE_LIMIT_STRATEGY == "global":
        return GLOBAL_ENDPOINT_LIMITS
    elif RATE_LIMIT_STRATEGY == "user_id":
        return USER_ENDPOINT_LIMITS
    elif RATE_LIMIT_STRATEGY == "api_key":
        return API_KEY_ENDPOINT_LIMITS
    else:  # Default to IP-based
        return IP_ENDPOINT_LIMITS

# Redis configuration
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}

# Rate limit messages
RATE_LIMIT_MESSAGE = {
    "error": "Rate limit exceeded",
    "message": "Too many requests. Please try again in few mins.",
    "retry_after": "Check the Retry-After header for when to retry"
}
