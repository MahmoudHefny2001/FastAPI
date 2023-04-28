from .routers import post, user, auth, vote
from .database import engine    
from .config import settings
from fastapi import FastAPI
from . import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def root():
    homeAPI = {
        "message": "Welcome to my API!"
    }
    return homeAPI


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

