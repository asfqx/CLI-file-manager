from src.core.models.models import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.config import config
from passlib.context import CryptContext
import typing

if typing.TYPE_CHECKING:
    from src.files.files import Files
    from src.operations.operations import Operations

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(config.static.USERNAME_MAX_LENGTH), nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(config.static.PASSWORD_MAX_LENGTH), nullable=False
    )

    files: Mapped[list["Files"]] = relationship(back_populates="user")
    operations: Mapped[list["Operations"]] = relationship(back_populates="user")

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        return pwd_context.verify(password, hashed)
