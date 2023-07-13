from typing import AsyncGenerator

from redis.asyncio import Redis
from starlette.requests import Request


async def get_redis_pool(
    request: Request,
) -> AsyncGenerator[Redis, None]:  # pragma: no cover
    """
    Returns connection pool.

    :param request: current request.
    :returns:  redis connection pool.
    """
    return request.app.state.redis_pool
