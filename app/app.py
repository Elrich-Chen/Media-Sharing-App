#the fast api app is coded here in app.py
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PostCreate, UserCreate, UserRead, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.types import file_upload_response 
import uuid

from app.users import auth_backend, current_Active_user, fastapi_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#auth connections
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), #Fast API data types
    caption: str = Form(""),
    user: User = Depends(current_Active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Read the uploaded file content into memory
        file_content = await file.read()
        
        # Upload to ImageKit using the new SDK v5.0.0 syntax
        # No need for UploadFileRequestOptions, just pass parameters directly
        upload_result: file_upload_response = imagekit.files.upload(
            file=file_content,                  # Pass bytes directly, no temp file needed
            file_name=file.filename,            # Original filename from the upload
            use_unique_file_name=True,          # Parameter passed directly, not in options object
            tags=["backend-upload"],            # Tags passed directly as a list
            folder="/uploads"                   # Organize uploads in a folder
        )
        
        # If we get here, upload succeeded (exceptions would be raised on failure)
        # Create the database record with the ImageKit URL
        post = Post(
            user_id=user.id,
            caption=caption,
            url=upload_result.url,              # ImageKit CDN URL for the uploaded file
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=upload_result.name,        # Use the actual name from ImageKit response (no quotes!)
            file_id= upload_result.file_id   # ImageKit's unique file ID
        )
        
        session.add(post)
        await session.commit()
        await session.refresh(post)
        
        return {
            "post_id": str(post.id),
            "url": upload_result.url,
            "file_id": upload_result.file_id,   # ImageKit's unique file ID
            "caption": post.caption
        }
        
    except Exception as e:
        # If anything goes wrong, raise an HTTP exception
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_Active_user)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unkown")
            }
        )

    return {"posts": posts_data}

################## DELETING A POST ########################
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession=Depends(get_async_session), user: User = Depends(current_Active_user)):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first() #convert rows into python objects

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You dont have permission to delete this post")
        
        imagekit.files.delete(file_id=post.file_id)
        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




#storing our text blogs
text_posts = {
    1: {"title": "New Post", "content": "New post content goes here."},
    2: {"title": "FastAPI Basics", "content": "A quick start with FastAPI routes."},
    3: {"title": "Python Tips", "content": "Small habits that improve readability."},
    4: {"title": "Async Notes", "content": "When to use async in web APIs."},
    5: {"title": "Testing", "content": "Why tests save time long-term."},
}

#returning our text posts
#using query parameters
@app.get("/posts")
def get_all_posts(limit: int = None):
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts

#get_posts_by_id
#making use of path parameters
@app.get("/posts/{id}")
def get_post_by_id(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_posts.get(id)

@app.get("/hello-world")
def hello_world():
    return {"message", "hello world"}


####################################################
# POST METHODS
@app.post("/posts")
def create_post(post: PostCreate) -> PostCreate:
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys())+1] = new_post
    return new_post
