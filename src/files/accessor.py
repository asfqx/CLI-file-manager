from sqlalchemy import insert, delete, select, update
from src.files.files import Files
from src.core.databaseAccessor import db


class FileAccessor:
    async def create(self, file_in) -> Files:
        stmt = (
            insert(Files)
            .values(
                file_name=file_in.file_name,
                user_id=file_in.user_id,
                file_size=file_in.file_size,
            )
            .returning(Files)
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    async def delete(self, file_name):
        stmt = delete(Files).where(Files.file_name == file_name)
        await db.execute(stmt)

    async def fetch_by_name(self, file_name) -> Files | None:
        stmt = select(Files).where(Files.file_name == file_name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, file_size, file_name) -> Files | None:
        stmt = (
            update(Files)
            .where(Files.file_name == file_name)
            .values(file_size=file_size)
            .returning(Files)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


fileAccessor = FileAccessor()
