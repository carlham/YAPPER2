from fastapi import FastAPI
import uvicorn
from database import engine, Base
from routes import users, tweets, auth, logs
from middleware import RateLimitMiddleware, RequestCacheMiddleware
from fastapi.middleware.cors import CORSMiddleware
import os

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

# add middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestCacheMiddleware)

# include routers
app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(auth.router)
app.include_router(logs.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Twitter clone API!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
