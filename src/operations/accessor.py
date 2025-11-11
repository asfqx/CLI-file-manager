from sqlalchemy.orm import selectinload

from src.operations.operations import Operations
from sqlalchemy import insert, select
from src.core.databaseAccessor import db


class OperationAccessor:
    async def create(self, operation_in) -> Operations:
        stmt = (
            insert(Operations)
            .values(
                type=operation_in.type,
                file_id=operation_in.file_id,
                user_id=operation_in.user_id,
            )
            .returning(Operations)
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    async def fetch_all(self) -> list[Operations] | None:
        stmt = select(Operations).options(
            selectinload(Operations.file), selectinload(Operations.user)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


operationsAccessor = OperationAccessor()
