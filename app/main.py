from fastapi import FastAPI, Response, status, HTTPException, Depends
from .database import engine, SessionLocal, get_db
from psycopg2.extras import RealDictCursor
from .schemas import PostCreate, Post
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from . import models
import psycopg2
import time


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        connection = psycopg2.connect(
            host = 'localhost', 
            database = 'fastapi', 
            user = 'postgres', 
            password = 'MA7MOUD7EFNY.',
            cursor_factory = RealDictCursor
        )
        cursor = connection.cursor()
        print("Connected successfully")
        break
    
    except Exception as error:
        print("Unable to connect")
        print("Error: ", error)
        time.sleep(2)


@app.get('/')
def root():
    greetings = {
        "message": "Welcome to my API!"
    }
    return greetings


@app.get('/posts', response_model=List[Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """
    #     INSERT INTO posts(title, content, published) VALUES (%s, %s, %s)
    #     RETURNING * ;
    #     """,
    #     (post.title, post.content, post.published)
    # )

    # new_post = cursor.fetchone()

    # connection.commit()
    new_post = models.Post(
        **post.dict()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.get("/posts/{id}", response_model=Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    # cursor.execute(
    #     f"""
    #     SELECT * from posts WHERE id = %s
    #     """,
    #     str(id)
    # )
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: \'{id}\' was not found'
        )
        
    return post    


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    # cursor.execute(
    #     """
    #     DELETE FROM posts WHERE id = %s RETURNING * 
    #     """,
    #     (str(id),)
    # )
    # deleted_post =  cursor.fetchone()    
    # connection.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"post with id: {id} does not exist"
        )

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=Post)
def update_post(id: int, updated_post: PostCreate, db: Session = Depends(get_db)):

    # cursor.execute(
    #     """
    #     UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *
    #     """,
    #     (post.title, post.content, post.published, str(id))
    # )

    # updated_post = cursor.fetchone()

    # connection.commit()
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )

    post_query.update(
        updated_post.dict(),
        synchronize_session=False
    )

    db.commit()

    return post_query.first()
