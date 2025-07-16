"""
Different rate limiting strategies for the API
"""
from fastapi import Request
from slowapi.util import get_remote_address

def get_ip_address(request: Request):
    """Rate limit by IP address (current default)"""
    return get_remote_address(request)

def get_global_key(request: Request):
    """Rate limit globally across all users"""
    return "global"

def get_user_id_key(request: Request):
    """Rate limit by user ID (requires authentication)"""
    # Example: Get user ID from JWT token or session
    user_id = request.headers.get("user-id", "anonymous")
    return f"user:{user_id}"

def get_api_key(request: Request):
    """Rate limit by API key"""
    api_key = request.headers.get("x-api-key", "no-key")
    return f"api_key:{api_key}"

def get_combined_key(request: Request):
    """Rate limit by combination of IP and user (more restrictive)"""
    ip = get_remote_address(request)
    user_id = request.headers.get("user-id", "anonymous")
    return f"ip:{ip}:user:{user_id}"

def get_endpoint_specific_key(request: Request):
    """Rate limit by endpoint and IP combination"""
    ip = get_remote_address(request)
    endpoint = request.url.path
    return f"endpoint:{endpoint}:ip:{ip}"
