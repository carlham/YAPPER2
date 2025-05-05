from fastapi import FastAPI, Request, Response
import httpx
import time
from typing import Dict, Any
import json

app = FastAPI()

# In-memory cache
# Structure: {request_key: {"data": response_data, "timestamp": timestamp}}
cache = {}

# Cache expiration time in seconds (1 minute)
CACHE_EXPIRATION = 60

# API endpoint (this will be the actual backend API)
API_URL = "http://localhost:8000"

# Implement a cache server