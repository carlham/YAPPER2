from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_records = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP as identifier
        client_id = request.client.host
        
        # Only rate limit POST/PUT requests to tweets
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