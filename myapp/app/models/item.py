from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)