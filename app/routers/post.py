from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..schemas import PostCreate, Post, UserCreate, UserOut, PostOut
from ..database import engine, SessionLocal, get_db
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func
from typing import List


router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

# @router.get('/', response_model=List[Post])
@router.get('/')
# @router.get('/', response_model=List[PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):


    posts = (
        db.query(
            models.Post, 
            func.count(models.Vote.post_id).label("votes")
        )
        .join(
            models.Vote, 
            models.Vote.post_id == models.Post.id, 
            isouter=True
        )
        .group_by(
            models.Post.id
        )
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    posts = [
        {
            "Post":{
                **post.__dict__,
                "votes": votes,
                "user":  {
                    "id": post.user.id,
                    "email": post.user.email,
                    "created_at": post.user.created_at
                },
            }
        }    
        for post, votes in posts
    ]

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_posts(
    post: PostCreate,
    db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user)
):

    new_post = models.Post(
        user_id = current_user.id,
        **post.dict()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    print(current_user.email)

    return new_post


# @router.get("/{id}", response_model=Post)
@router.get("/{id}",)
def get_post(
    id: int, 
    response: Response, 
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):

    try:
        post, votes = (
            db.query(
                models.Post, 
                func.count(models.Vote.post_id).label("votes")
            )
            .join(
                models.Vote, 
                models.Vote.post_id == models.Post.id, 
                isouter=True
            )
            .group_by(
                models.Post.id
            )
            .filter(
                models.Post.id == id
            )
            .first()
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Post with id \'{id}\' not found'
        )

    post_dictionary = {
        "Post": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "published": post.published,
            "created_at": post.created_at,
            "user_id": post.user_id,
            "user": {
                "id": post.user.id,
                "email": post.user.email,
                "created_at": post.user.created_at,
            },
            "votes": votes,
        }
    }


    return post_dictionary    


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user)
):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"post with id: {id} does not exist"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = f"Not authorized to perform requested action"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=Post)
def update_post(
    id: int, 
    updated_post: PostCreate, 
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = f"Not authorized to perform requested action"
        )

    post_query.update(
        updated_post.dict(),
        synchronize_session=False
    )

    db.commit()

    return post_query.first()
