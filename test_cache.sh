#!/bin/bash

# This script checks all three caching layers to ensure they're working properly
# For testing on macos later, remove after

echo "===== YAPPER2 CACHE TEST ====="
echo "Testing all caching layers with both header and performance-based metrics"

direct_url="http://localhost:8000/users"
nginx_url="http://localhost:8080/users"

echo -e "\n===== TESTING DB CACHE ====="
echo "Testing DB Cache (first request)..."
curl -s -w "\nResponse time: %{time_total}s\n" $direct_url > /dev/null
echo "Second request (should be faster if DB cache works):"
curl -s -w "\nResponse time: %{time_total}s\n" $direct_url > /dev/null

echo -e "\n===== TESTING REQUEST CACHE ====="
curl -i $direct_url | grep -i "X-RequestCache-Status"

echo -e "\n===== TESTING NGINX CACHE ====="
echo "First request through Nginx (expect cache miss)..."
curl -i $nginx_url | grep -i "X-Cache"

echo "Second request through Nginx (expect cache hit)..."
curl -i $nginx_url | grep -i "X-Cache"

# Performance-based verification for Windows compatibility
echo -e "\n===== VERIFYING CACHE WITH PERFORMANCE METRICS ====="
echo "First batch of requests:"
time1=$(date +%s.%N 2>/dev/null || date +%s)
curl -s $nginx_url > /dev/null
curl -s $nginx_url > /dev/null
curl -s $nginx_url > /dev/null
time2=$(date +%s.%N 2>/dev/null || date +%s)
duration1=$(echo "$time2 - $time1" | bc 2>/dev/null || echo "0")

if [[ $duration1 == "0" ]]; then
  # Fallback for systems without bc or proper date nanoseconds
  echo "Performance timing not available on this system"
else
  echo "Time taken: $duration1 seconds"
  
  echo "Second batch (should be faster if cache is working):"
  time3=$(date +%s.%N 2>/dev/null || date +%s)
  curl -s $nginx_url > /dev/null
  curl -s $nginx_url > /dev/null
  curl -s $nginx_url > /dev/null
  time4=$(date +%s.%N 2>/dev/null || date +%s)
  duration2=$(echo "$time4 - $time3" | bc)
  echo "Time taken: $duration2 seconds"
  
  # Calculate improvement if possible
  improvement=$(echo "($duration1 - $duration2) / $duration1 * 100" | bc -l)
  printf "Performance improvement: %.1f%%\n" $improvement
  
  if (( $(echo "$improvement > 20" | bc -l) )); then
    echo "✓ Cache appears to be working correctly!"
    echo "  Significant performance improvement detected."
  else
    echo "⚠ Cache may not be working optimally."
    echo "  Performance improvement is less than expected."
  fi
fi

echo -e "\n===== CACHE STATISTICS ====="
echo -e "\nDB Cache Stats:"
curl -s $direct_url/debug/db-cache-stats | python -m json.tool 2>/dev/null || curl -s $direct_url/debug/db-cache-stats

echo -e "\nRequest Cache Stats:"
curl -s $direct_url/debug/cache-stats | python -m json.tool 2>/dev/null || curl -s $direct_url/debug/cache-stats

echo -e "\n===== ADDITIONAL TOOLS ====="
echo "For more detailed tests, run:"
echo "  python backend/app/cache_diagnostic.py"
echo "  python backend/app/cache_performance_monitor.py"
echo "  python backend/app/ongoing_cache_monitor.py"
