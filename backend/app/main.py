from fastapi import FastAPI, Depends
import uvicorn
from database import engine, Base
from routes import users, tweets

Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

# include users router
app.include_router(users.router)
app.include_router(tweets.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Twitter clone API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)