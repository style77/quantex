from fastapi.routing import APIRouter

from quantex.web.api import news

api_router = APIRouter()
api_router.include_router(news.router)
