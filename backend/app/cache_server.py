from fastapi import FastAPI, Request, Response, Header
from itertools import cycle 
import httpx
import time
from typing import Dict, Any, List, Optional
import json
from collections import Counter
import re

app = FastAPI()

#In-memory cache
#Structure: {request_key: {"data": response_data, "timestamp": timestamp}}
cache = {}

#Request counter for tracking load balancing
request_counter = Counter()

#Cache expiration time in seconds (1 minute)
CACHE_EXPIRATION = 60

#Maximum cache size (items)
MAX_CACHE_SIZE = 1000

#Database read endpoints to cache
DB_READ_PATHS = [
    r"^/users$",                  #Get all users
    r"^/users/\d+$",              #Get user by ID
    r"^/users/search",            #Search users
    r"^/tweets$",                 #Get all tweets
    r"^/tweets/\d+$",             #Get tweet by ID
    r"^/tweets/search",           #Search tweets
    
    r"^/likes/\d+$",              #Get likes for a tweet
]

#Mapping of write endpoints to related cached endpoints that should be invalidated
CACHE_INVALIDATION_MAP = {
    r"^/tweets$": [r"^/tweets$", r"^/users/\d+/tweets$"],  
    r"^/tweets/\d+$": [r"^/tweets$", r"^/tweets/\d+$", r"^/users/\d+/tweets$"],
    r"^/likes$": [r"^/likes/\d+$", r"^/tweets/\d+$"],
}

with open("servers.json") as f:
    servers = json.load(f)

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.pool = cycle(server["url"] for server in servers)

    def round_robin(self):
        return next(self.pool)

load_balancer = LoadBalancer(servers)

def is_db_read_request(method: str, path: str) -> bool:
    """Determine if a request is a database read operation we want to cache"""
    if method != "GET":
        return False
    
    #Check if path matches any of our defined DB read patterns
    for pattern in DB_READ_PATHS:
        if re.match(pattern, path):
            return True
    
    return False

def is_write_request(method: str) -> bool:
    """Check if this is a write operation"""
    return method in ["POST", "PUT", "DELETE", "PATCH"]

def get_paths_to_invalidate(method: str, path: str) -> List[str]:
    """Get a list of cache path patterns that should be invalidated for this write request"""
    if not is_write_request(method):
        return []
        
    paths_to_invalidate = []
    
    #Check each pattern to see if it matches the current path
    for pattern, invalidation_patterns in CACHE_INVALIDATION_MAP.items():
        if re.match(pattern, path):
            paths_to_invalidate.extend(invalidation_patterns)
    
    return paths_to_invalidate

def invalidate_cache_entries(patterns: List[str]):
    """Invalidate all cache entries matching the specified path patterns"""
    if not patterns:
        return
        
    keys_to_delete = []
    
    for cache_key in cache.keys():
        #Extract path from cache key (format: "METHOD:path:query:auth")
        parts = cache_key.split(":", 2)
        if len(parts) >= 2:
            cached_path = parts[1]
            
            #Check if this cached path matches any of our patterns to invalidate
            for pattern in patterns:
                if re.match(pattern, cached_path):
                    keys_to_delete.append(cache_key)
                    break
    
    #Delete the keys
    for key in keys_to_delete:
        del cache[key]
        print(f"Invalidated cache for {key}")

def generate_cache_key(request: Request, path: str) -> str:
    """Generate a unique cache key based on the request method, path, and query parameters."""
    query_string = request.url.query.decode() if request.url.query else ""
    auth_header = request.headers.get("Authorization", "")
    #Only use the token part, not the entire header
    if auth_header.startswith("Bearer "):
        auth_token = auth_header.split(" ")[1][:10]  #Just use first 10 chars as identifier
    else:
        auth_token = "noauth"
        
    return f"{request.method}:{path}:{query_string}:{auth_token}"

def maintain_cache_size():
    """Remove oldest items if cache exceeds maximum size"""
    if len(cache) > MAX_CACHE_SIZE:
        #Get the keys sorted by timestamp (oldest first)
        sorted_keys = sorted(cache.keys(), key=lambda k: cache[k]["timestamp"])
        #Remove oldest entries to get back to 75% of max size
        to_remove = len(cache) - int(MAX_CACHE_SIZE * 0.75)
        for _ in range(to_remove):
            if sorted_keys:
                del cache[sorted_keys.pop(0)]

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request, path: str, response: Response):
    #Check if this is a cacheable database read request
    is_db_read = is_db_read_request(request.method, path)
    
    #Generate a cache key for this request
    cache_key = generate_cache_key(request, path)
    
    #Check if we have a valid cached response for db reads
    current_time = time.time()
    cache_status = "MISS"
    
    #Check if this is a write operation that should invalidate cache entries
    if is_write_request(request.method):
        paths_to_invalidate = get_paths_to_invalidate(request.method, path)
        invalidate_cache_entries(paths_to_invalidate)
        cache_status = "BYPASS"  #This request is bypassing cache
    #For GET requests, check cache
    elif is_db_read and cache_key in cache:
        cached_data = cache[cache_key]
        if current_time - cached_data["timestamp"] < CACHE_EXPIRATION:
            print(f"Cache hit for {path}")
            cache_status = "HIT"
            #Set cache status header
            response.headers["X-Cache-Status"] = cache_status
            return cached_data["data"]
        else:
            #Cache expired, remove it
            print(f"Cache expired for {path}")
            cache_status = "EXPIRED"
            del cache[cache_key]
    
    #Get the next server from the load balancer
    backend_url = load_balancer.round_robin()
    url = f"{backend_url}/{path}"
    request_counter[backend_url] += 1
    
    #Print detailed request and balance information
    print(f"Forwarding request to: {url} for {request.method} {path}")
    print(f"Current load distribution: {dict(request_counter)}")
    
    try:
        async with httpx.AsyncClient() as client:
            #Forward the request to the backend
            backend_response = await client.request(
                request.method, 
                url, 
                headers=dict(request.headers.items()),
                content=await request.body(),
                params=dict(request.query_params)
            )
            
            #Get content type and check if it's JSON
            content_type = backend_response.headers.get("content-type", "")            #Copy headers from backend response to our response
            for header_name, header_value in backend_response.headers.items():
                #Skip content-length as FastAPI will set it
                if header_name.lower() != "content-length":
                    response.headers[header_name] = header_value
              #Never override the X-Cache-Status from Nginx
            #Instead, we'll add our own status with a different name
            response.headers["X-Proxy-Cache-Status"] = cache_status
            
            #If we don't see an Nginx cache status, explicitly note that
            if "X-Cache-Status" not in backend_response.headers:
                response.headers["X-Cache-Status-Note"] = "Not set by Nginx"
            
            #Add more detailed cache information for debugging
            if is_db_read:
                response.headers["X-Cache-Type"] = "DB_READ"
                response.headers["X-Cache-Key"] = cache_key
            
            #Set status code from backend
            response.status_code = backend_response.status_code
            
            #Only cache successful DB read requests with JSON responses
            if (is_db_read and 
                backend_response.status_code == 200 and 
                "application/json" in content_type):
                try:
                    response_data = backend_response.json()
                    
                    #Cache the response
                    cache[cache_key] = {
                        "data": response_data,
                        "timestamp": current_time
                    }
                    print(f"Cached response for {path}")
                    
                    #Maintain cache size
                    maintain_cache_size()
                    
                    return response_data
                except Exception as json_error:
                    print(f"Error parsing JSON response: {str(json_error)}")
                    return Response(content=backend_response.content, status_code=backend_response.status_code)
            
            #For non-JSON responses, return the raw content
            return Response(content=backend_response.content, status_code=backend_response.status_code)
            
    except Exception as e:
        print(f"Error forwarding request: {str(e)}")
        response.status_code = 500
        return {"error": str(e)}
