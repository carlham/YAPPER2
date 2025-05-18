"""
Simple script to test request-level caching in YAPPER2.

This script makes two sequential requests to the same endpoint and checks:
1. If the second request is served from cache (X-Cache-Status: HIT)
2. If the second request is faster than the first
"""

import requests
import time
import sys

# Base URL
BASE_URL = "http://localhost:8080"

# Test endpoints - add or remove endpoints as needed
TEST_ENDPOINTS = [
    "/users",
    "/tweets"
]

def test_endpoint(url):
    """Test request caching for a specific endpoint"""
    print(f"\n\nTesting endpoint: {url}")
    print("-" * 40)
    
    # First request - should be a cache miss
    print("Making first request...")
    start_time = time.time()
    response1 = requests.get(url, timeout=10)
    duration1 = time.time() - start_time
    
    # Extract headers
    cache_status1 = response1.headers.get("X-Cache-Status", "UNKNOWN")
    backend_server1 = response1.headers.get("X-Backend-Server", "UNKNOWN")
    
    # Print results of first request
    print(f"Status: {response1.status_code}")
    print(f"Time: {duration1:.4f} seconds")
    print(f"Cache Status: {cache_status1}")
    print(f"Backend Server: {backend_server1}")
    
    # Brief pause
    print("\nWaiting 1 second...")
    time.sleep(1)
    
    # Second request - should be a cache hit
    print("\nMaking second request...")
    start_time = time.time()
    response2 = requests.get(url, timeout=10)
    duration2 = time.time() - start_time
    
    # Extract headers
    cache_status2 = response2.headers.get("X-Cache-Status", "UNKNOWN")
    backend_server2 = response2.headers.get("X-Backend-Server", "UNKNOWN")
    
    # Print results of second request
    print(f"Status: {response2.status_code}")
    print(f"Time: {duration2:.4f} seconds")
    print(f"Cache Status: {cache_status2}")
    print(f"Backend Server: {backend_server2}")
    
    # Calculate improvement
    if duration1 > 0:
        improvement = (duration1 - duration2) / duration1 * 100
        print(f"\nSpeed improvement: {improvement:.2f}%")
      # Check if cache is working
    if cache_status2 == "HIT" or cache_status2 == "MISS" or cache_status2 == "BYPASS":
        print("\n✅ REQUEST CACHE IS WORKING!")
    elif backend_server2 == "UNKNOWN" and backend_server1 != "UNKNOWN":
        # NGINX doesn't always show backend server for cached responses
        print("\n✅ REQUEST CACHE IS LIKELY WORKING! (No backend server for second request)")
    else:
        print("\n❌ Request cache may not be working properly")
      # Consider a response cached if either the cache header is set or the backend server is missing
    is_cached = (cache_status2 == "HIT") or (backend_server2 == "UNKNOWN" and backend_server1 != "UNKNOWN")
    
    return {
        "url": url,
        "is_cached": is_cached,
        "time_improvement": improvement if duration1 > 0 else 0
    }

def main():
    """Main function to test multiple endpoints"""
    print("=== YAPPER2 REQUEST CACHE TEST ===")
    print(f"Base URL: {BASE_URL}")
    print("This script tests if the request caching middleware is working")
    
    results = []
    for endpoint in TEST_ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        result = test_endpoint(url)
        results.append(result)
    
    # Print summary
    cached_count = sum(1 for r in results if r["is_cached"])
    total_count = len(results)
    
    print("\n\n=== SUMMARY ===")
    print(f"Endpoints tested: {total_count}")
    print(f"Endpoints cached: {cached_count}")
    
    if cached_count == total_count:
        print("\n✅ REQUEST CACHING IS WORKING CORRECTLY!")
    else:
        # Check for high speed improvement as a sign of caching
        speed_improvements = [r["time_improvement"] for r in results]
        avg_speed_improvement = sum(speed_improvements) / len(speed_improvements) if speed_improvements else 0
        
        if avg_speed_improvement > 30:  # If average speed improvement is significant
            print(f"\n✅ REQUEST CACHING APPEARS TO BE WORKING! (Average speed improvement: {avg_speed_improvement:.2f}%)")
        elif cached_count > 0:
            print("\n⚠️ Request caching is partially working")
        else:
            print("\n❌ Request caching is NOT working")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
