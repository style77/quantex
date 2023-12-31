import datetime
import typing

from pydantic import BaseModel


class NewsModelDTO(BaseModel):
    """News model DTO."""

    class Config:
        from_attributes = True

    id: int
    created_at: datetime.datetime
    term: typing.Literal["short", "long"]
    ticker: str
    headline: str
    explanation: str
    result: typing.Literal["positive", "negative", "neutral"]


class NewsModelCreateDTO(BaseModel):
    """News model create DTO."""

    class Config:
        from_attributes = True

    term: typing.Literal["short", "long"]
    ticker: str
    headline: str
    explanation: str
    result: typing.Literal["positive", "negative", "neutral"]
