from typing import Annotated

from fastapi import Header, HTTPException

from quantex.settings import Settings


async def verify_secret(x_secret: Annotated[str, Header()]):
    if x_secret != Settings.secret_key:
        raise HTTPException(status_code=403, detail="Secret header invalid")
