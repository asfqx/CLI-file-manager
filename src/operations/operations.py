from src.core.models.models import BaseModel
from sqlalchemy import DateTime, func, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.operations.enum import OperationType

import typing

if typing.TYPE_CHECKING:
    from src.files.files import Files
    from src.users.users import User


class Operations(BaseModel):
    __tablename__ = "operations"

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    type: Mapped[OperationType]
    file_id: Mapped[BigInteger] = mapped_column(
        BigInteger, ForeignKey("files.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[BigInteger] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    file: Mapped["Files"] = relationship(back_populates="operations")
    user: Mapped["User"] = relationship(back_populates="operations")
