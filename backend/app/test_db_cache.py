"""
Simple script to test database-level caching in YAPPER2.

This script tests if database query caching is working by:
1. Making a request to the DB cache test endpoint
2. Analyzing the results to see if the second query was faster
"""

import requests
import json

# Test endpoint for database caching
TEST_URL = "http://localhost:8080/cache-test/test-db-cache"

# DB cache stats endpoint
STATS_URL = "http://localhost:8080/debug/db-cache-stats"

def test_db_cache():
    """Test database query caching"""
    print("=== YAPPER2 DATABASE CACHE TEST ===")
    print(f"Testing endpoint: {TEST_URL}\n")
    
    try:
        # Get current cache stats before test
        print("Getting initial cache stats...")
        stats_response = requests.get(STATS_URL, timeout=10)
        if stats_response.status_code == 200:
            before_stats = stats_response.json()
            print("Initial cache stats:")
            print(json.dumps(before_stats, indent=2))
        else:
            print(f"⚠️ Could not get cache stats. Status: {stats_response.status_code}")
            before_stats = None
            
        print("\nMaking request to test endpoint...")
        response = requests.get(TEST_URL, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Test failed with status code: {response.status_code}")
            return
        
        # Parse results
        data = response.json()
        print("\nTest results:")
        
        # Print key metrics
        cache_working = data.get("cache_working", False)
        first_time = data.get("first_query_time_ms", 0)
        second_time = data.get("second_query_time_ms", 0)
        improvement = data.get("speed_improvement_percent", 0)
        record_count = data.get("record_count", 0)
        
        print(f"Records retrieved: {record_count}")
        print(f"First query time: {first_time} ms")
        print(f"Second query time: {second_time} ms")
        print(f"Speed improvement: {improvement:.2f}%")
        
        # Check before/after cache stats
        before_hits = data.get("before_stats", {}).get("hits", 0)
        after_hits = data.get("after_stats", {}).get("hits", 0)
        hits_added = after_hits - before_hits
        
        print(f"Cache hits: {before_hits} → {after_hits} (+{hits_added})")
        
        # Display conclusion
        if cache_working:
            print("\n✅ DATABASE CACHE IS WORKING!")
            print(f"Second query was {improvement:.2f}% faster")
        else:
            print("\n❌ Database cache is NOT working")
            
        # Get current cache stats after test
        print("\nGetting current cache stats...")
        stats_response = requests.get(STATS_URL, timeout=10)
        if stats_response.status_code == 200:
            current_stats = stats_response.json()
            print("Current cache stats:")
            print(json.dumps(current_stats, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_db_cache()
