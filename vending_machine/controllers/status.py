from fastapi import APIRouter, Depends, HTTPException
from vending_machine.database import get_db
from typing import Any
from logging import getLogger

from sqlalchemy.sql.expression import text

routes = APIRouter()
logger = getLogger(__name__)

@routes.get("/heartbeat")
async def heartbeat(
    db: Depends = Depends(get_db),
) -> Any:
    try:
        system_time = db.execute(text("SELECT datetime('now')")).first()[0]
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"status": "ok", "system_time": system_time}