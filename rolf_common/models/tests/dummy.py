from rolf_common.models.base import SQLModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class DummyModel(SQLModel):
    __tablename__ = "dummy"

    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(255), nullable=True)