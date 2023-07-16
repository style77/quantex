import typing
from fastapi import APIRouter
from fastapi.param_functions import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse
from quantex.database.dao.news_dao import NewsDAO

from quantex.web.api.news.schema import NewsModelCreateDTO, NewsModelDTO
from quantex.web.dependencies import verify_secret

router = APIRouter()


@router.get("/", dependencies=[Depends(verify_secret)], response_model=NewsModelDTO)
async def get_news(
    news_dao: NewsDAO = Depends(),
    news_id: typing.Optional[int] = None,
    ticker: typing.Optional[str] = None,
    term: typing.Optional[str] = None,
    result: typing.Optional[str] = None,
    headline: typing.Optional[str] = None,
):
    """Get news by id and optional ticker, term or result."""

    if headline:
        # This is mostly for getting unique news
        news = await news_dao.get_news_by_headline(headline)
    elif news_id:
        news = await news_dao.get_news(int(news_id))
    else:
        news = await news_dao.get_many_news(ticker, term, result)

    res = {
        "news": news,
        "count": 0 if not news else len(news),
    }

    return JSONResponse(res, media_type="application/json")


@router.post("/", dependencies=[Depends(verify_secret)])
async def create_news(news: NewsModelCreateDTO, news_dao: NewsDAO = Depends()):
    """Create news."""
    await news_dao.create_news(news)
    return JSONResponse({"status": "ok"})
