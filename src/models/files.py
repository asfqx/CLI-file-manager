from src.core.models.models import BaseModel
from sqlalchemy import String, DateTime, BigInteger, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.config import config
import typing

if typing.TYPE_CHECKING:
    from src.models.users import User
    from src.models.operations import Operations


class Files(BaseModel):
    __tablename__ = "files"

    file_name: Mapped[str] = mapped_column(String(config.static.FILE_NAME_MAX_LENGTH))
    created_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    file_size: Mapped[int] = mapped_column()
    user_id: Mapped[BigInteger] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(back_populates="files")
    operations: Mapped[list["Operations"]] = relationship(back_populates="file")
