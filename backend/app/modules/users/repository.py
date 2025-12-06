"""This is the Users repository module"""

from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from sqlalchemy.future import select
from .models import UserCreate, UserUpdate

class UserRepository:
    """Repository class for user-related database operations"""
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int):
        """Fetch a user by their ID"""
        user = select(User).where(User.id == user_id)
        result = await db.execute(user)
        return result.scalars().first()
    
    async def create_user(self, db: AsyncSession, user_create: UserCreate):
        """Create a new user in the database"""
        new_user = User(**user_create.model_dump())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user