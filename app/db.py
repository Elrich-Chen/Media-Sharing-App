from collections.abc import AsyncGenerator
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

#connecting to a local test databse
DATABASE_URL = "sqlite+aiosqlite:///./test_db"

#declarative base is pure sql alchemy
class Base(DeclarativeBase): #cannot directly inherit from declarative base
    pass

#inherits SQL's User Table that comes with prepopulated fields, + Base
class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    posts = relationship("Post", back_populates="user")


#data models (structure) | Defining the posts type
class Post(Base): #declarative base is for knowing it is a data model
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_id = Column(String, nullable=False)

    user = relationship("User", back_populates="posts")

engine = create_async_engine(DATABASE_URL)
async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)