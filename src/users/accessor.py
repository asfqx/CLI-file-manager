from src.users.users import User
from sqlalchemy import insert, select
from src.core.databaseAccessor import db


class UserAccessor:
    async def create(self, user_in) -> User:
        stmt = (
            insert(User)
            .values(
                username=user_in.username,
                password=User.hash_password(user_in.password),
            )
            .returning(User)
        )
        result = await db.execute(stmt)
        user = result.scalar_one()
        return user

    async def fetch_by_id(self, user_id) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def fetch_by_username(self, username) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


userAccessor = UserAccessor()
