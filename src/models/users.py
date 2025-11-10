from src.core.models.models import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.config import config
import typing

if typing.TYPE_CHECKING:
    from src.models.files import Files
    from src.models.operations import Operations


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
