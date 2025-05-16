import httpx
import asyncio
import time

#URL of your Nginx cache server
CACHE_SERVER_URL = "http://localhost:8080"

#Test endpoints
TEST_ENDPOINTS = [
    "/users",
    "/tweets",
    "/users/1",
    "/tweets/1"   
]

async def make_request(endpoint, session_id):
    """Make a request to the cache server and measure response time."""
    start_time = time.time()
    url = f"{CACHE_SERVER_URL}{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            duration = time.time() - start_time
            status = response.status_code
            cache_status = response.headers.get("X-Cache-Status", "UNKNOWN")
            
            #Try to parse response as JSON, but handle case where it's not JSON
            try:
                data_preview = str(response.json())[:50] + "..." if len(str(response.json())) > 50 else str(response.json())
            except:
                data_preview = str(response.text)[:50] + "..." if len(response.text) > 50 else response.text
                
            print(f"Session {session_id} | {endpoint} | Status: {status} | Cache: {cache_status} | Time: {duration:.4f}s | Response: {data_preview}")
            return duration, status, cache_status
    except Exception as e:
        duration = time.time() - start_time
        print(f"Session {session_id} | {endpoint} | Error: {str(e)} | Time: {duration:.4f}s")
        return duration, None, "ERROR"

async def test_session(session_id, iterations=3):
    """Simulate a user session with multiple requests."""
    print(f"Starting session {session_id}")
    
    cache_hits = 0
    cache_misses = 0
    total_requests = 0
    
    for i in range(iterations):
        for endpoint in TEST_ENDPOINTS:
            duration, status, cache_status = await make_request(endpoint, session_id)
            total_requests += 1
            
            if cache_status == "HIT":
                cache_hits += 1
            elif cache_status in ["MISS", "EXPIRED"]:
                cache_misses += 1
                
            #Small delay between requests
            await asyncio.sleep(0.5)
    
    hit_rate = (cache_hits / total_requests) * 100 if total_requests > 0 else 0
    print(f"Session {session_id} completed | Cache Hit Rate: {hit_rate:.1f}% ({cache_hits}/{total_requests})")

async def main():
    """Run multiple concurrent user sessions to test load balancing and caching."""
    print("Starting Nginx cache server test")
    print(f"Cache Server URL: {CACHE_SERVER_URL}")
    print("Test will run multiple concurrent sessions, each making repeated requests to test caching")
    print("--------------------------------------------------------------------")
    
    num_sessions = 3
    
    #Run multiple sessions concurrently
    tasks = [test_session(i) for i in range(num_sessions)]
    await asyncio.gather(*tasks)
    
    print("--------------------------------------------------------------------")
    print("Test completed")
    print("If you see 'Cache: HIT' in the output, the Nginx cache is working correctly!")
    print("If you see fast response times on repeated requests, the caching is effective.")

if __name__ == "__main__":
    asyncio.run(main())
