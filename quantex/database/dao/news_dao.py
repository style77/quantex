import typing

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from quantex.database.dependencies import get_db_session
from quantex.database.models.news_model import NewsModel

from quantex.web.api.news.schema import NewsModelCreateDTO, NewsModelDTO


class NewsDAO:
    """Class for accessing user table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_news(self, news: NewsModelCreateDTO) -> None:
        """Create news."""
        news_model = NewsModel(*news)
        self.session.add(news_model)
        await self.session.commit()

    async def get_news(self, news_id: int) -> NewsModelDTO:
        """Get news by id."""
        query = select(NewsModel).where(NewsModel.id == news_id)
        r = await self.session.execute(query)
        news = r.scalars().first()
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
            )
        return NewsModelDTO.from_orm(news)

    async def get_many_news(
        self,
        ticker: typing.Optional[str] = None,
        term: typing.Optional[str] = None,
        result: typing.Optional[str] = None,
    ) -> typing.List[NewsModelDTO]:
        """Get news by ticker, term or result."""
        query = select(NewsModel)
        if ticker:
            query = query.where(NewsModel.ticker == ticker)
        if term:
            query = query.where(NewsModel.term == term)
        if result:
            query = query.where(NewsModel.result == result)
        r = await self.session.execute(query)
        news = r.scalars().all()
        return [NewsModelDTO.from_orm(n) for n in news]

    async def get_news_by_headline(self, headline):
        """Get news by headline."""
        query = select(NewsModel).where(NewsModel.headline == headline)
        r = await self.session.execute(query)
        news = r.scalars().first()
        return news
