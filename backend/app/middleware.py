from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict

# Global cache dictionary for storing responses
# Structure: {request_key: {"response": response_data, "timestamp": timestamp}}
cache = {}

# Rate limiting middleware to limit the number of requests from a client withing specified time window
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_records = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP as identifier
        client_id = request.client.host
        
        # Only rate limit POST/PUT/DELETE requests to tweets
        if request.url.path.startswith("/tweets") and request.method in ["POST", "PUT", "DELETE"]:
            current_time = time.time()
            
            # Clean up old records
            self.request_records[client_id] = [
                timestamp for timestamp in self.request_records[client_id]
                if current_time - timestamp < self.window_seconds
            ]
            
            # Check if rate limit exceeded
            if len(self.request_records[client_id]) >= self.max_requests:
                return Response(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=f"Rate limit exceeded. Try again in {self.window_seconds} seconds."
                )
                
            # Add current request
            self.request_records[client_id].append(current_time)
        
        # Process the request
        response = await call_next(request)
        return response

# Request caching middleware 
# This middleware will cache GET requests to reduce unnecessary API calls
class RequestCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Initialize the cache dictionary for storing responses
        global cache
        self.cache_expiration = 60
    
    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            return await call_next(request)
            
        # Generate a cache key for this request
        cache_key = self._generate_cache_key(request)
        
        # Check if we have a valid cached response
        if cache_key in cache:
            cached_item = cache[cache_key]
            current_time = time.time()
              # Check if the cached response is still valid
            if current_time - cached_item["timestamp"] < self.cache_expiration:
                print(f"Cache hit for {request.url.path}")
                # Return the cached response
                response = Response(
                    content=cached_item["content"],
                    status_code=cached_item["status_code"],
                    headers=cached_item["headers"],
                    media_type=cached_item["media_type"]
                )
                
                # Ensure the cache header is present even when returning cached response
                response.headers["X-RequestCache-Status"] = "HIT"
                print(f"Request cache: Serving {cache_key} from cache")
                print(f"Response headers include X-RequestCache-Status: HIT")
                
                return response
        
        response = await call_next(request)
        
        # Only cache successful responses
        if 200 <= response.status_code < 300:
            content = b""
            async for chunk in response.body_iterator:
                content += chunk
            
            new_response = Response(
                content=content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            cache[cache_key] = {
                "content": content,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type,
                "timestamp": time.time()
            }
            
            # Add cache header to indicate this response was cached
            new_response.headers["X-RequestCache-Status"] = "CACHED"
            
            # Debug print
            print(f"Request cache: Added {cache_key} to cache")
            print(f"Response headers will include X-RequestCache-Status: CACHED")
            
            return new_response
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate a unique cache key based on method, path, and query params."""
        path = request.url.path
        query = request.url.query.decode() if request.url.query else ""
        
        # Include authorization in key to prevent data leakage between users
        auth = request.headers.get("Authorization", "noauth")
        
        return f"{request.method}:{path}:{query}:{auth}"