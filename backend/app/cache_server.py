from fastapi import FastAPI, Request, Response
from itertools import cycle 
import httpx
import time
from typing import Dict, Any
import json
from collections import Counter

app = FastAPI()

#In-memory cache
#Structure: {request_key: {"data": response_data, "timestamp": timestamp}}
cache = {}

#Request counter for tracking load balancing
request_counter = Counter()

#Cache expiration time in seconds (1 minute)
CACHE_EXPIRATION = 60

with open ("servers.json") as f:
    servers = json.load(f)
class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.pool = cycle(server["url"] for server in servers)

    def round_robin(self):
        return next(self.pool)

#Implement a cache server

load_balancer = LoadBalancer(servers)


def generate_cache_key(request: Request, path: str) -> str:
    """Generate a unique cache key based on the request method, path, and query parameters."""
    query_string = request.url.query.decode() if request.url.query else ""
    return f"{request.method}:{path}:{query_string}"

@app.get("/{path:path}")
async def proxy(request: Request, path: str, response: Response):
    #Generate a cache key for this request
    cache_key = generate_cache_key(request, path)
    
    #Check if we have a valid cached response
    current_time = time.time()
    if request.method == "GET" and cache_key in cache:
        cached_data = cache[cache_key]
        if current_time - cached_data["timestamp"] < CACHE_EXPIRATION:
            print(f"Cache hit for {path}")
            return cached_data["data"]
        else:
            #Cache expired, remove it
            print(f"Cache expired for {path}")
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
            response = await client.request(
                request.method, 
                url, 
                headers=dict(request.headers.items()),
                content=await request.body(),
                params=dict(request.query_params)
            )
            
            #Parse the response
            response_data = response.json()
            
            #Cache the response if it's a GET request
            if request.method == "GET":
                cache[cache_key] = {
                    "data": response_data,
                    "timestamp": current_time
                }
                print(f"Cached response for {path}")
            
            return response_data
    except Exception as e:
        print(f"Error forwarding request: {str(e)}")
        return {"error": str(e)}

