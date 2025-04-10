from fastapi import FastAPI
import uvicorn
from database import engine, Base
from routes import users, tweets, auth
from middleware import RateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000"
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

# include users router
app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Twitter clone API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
