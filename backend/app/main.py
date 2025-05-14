from fastapi import FastAPI, Request, Response
import uvicorn
import os
import time
import sys
from pathlib import Path
from database import engine, Base
from routes import users, tweets, auth, logs, likes
from middleware import RateLimitMiddleware, RequestCacheMiddleware
from routes.logs import log_api_call
from fastapi.middleware.cors import CORSMiddleware

#Add the parent directory to sys.path to make local imports work
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir.parent))


Base.metadata.create_all(bind=engine)

debug = os.environ.get("DEBUG", "True").lower() == "true"
app = FastAPI(debug=debug)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://yapper-4qux.onrender.com",
    "https://yapper-zwai.onrender.com"
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Log middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the request details
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    
    # Log the API call
    log_api_call(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        execution_time=end_time - start_time
    )
    
    return response

# add middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestCacheMiddleware)

# include routers
app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(auth.router)
app.include_router(logs.router)
app.include_router(likes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Twitter clone API!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
