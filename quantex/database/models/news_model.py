from datetime import datetime
from typing import Literal

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Integer, DateTime

from quantex.database.base import Base

TERM = Literal["short", "long"]
RESULT = Literal["positive", "negative", "neutral"]


class NewsModel(Base):
    __tablename__ = "news"

    id: Mapped[Integer] = mapped_column(
        Integer(),
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(),
        nullable=False,
        default=datetime.utcnow,
    )
    term: Mapped[TERM] = mapped_column(
        sqlalchemy.Enum("short", "long", name="term"),
        nullable=False,
    )
    ticker: Mapped[String] = mapped_column(
        String(length=8),
        nullable=False,
    )
    headline: Mapped[String] = mapped_column(
        String(length=256),
        nullable=False,
    )
    explanation: Mapped[String] = mapped_column(
        String(),
        nullable=False,
    )
    result: Mapped[RESULT] = mapped_column(
        sqlalchemy.Enum("positive", "negative", "neutral", name="result"),
        nullable=False,
    )
