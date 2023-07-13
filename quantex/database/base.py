from sqlalchemy.orm import DeclarativeBase

from quantex.database.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
