from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.sql.expression import text

from vending_machine.database import get_db
from vending_machine.logging import get_logger

routes = APIRouter()
logger = get_logger(__name__)


@routes.get("/heartbeat", tags=["status"])
async def heartbeat(
    db: Depends = Depends(get_db),
) -> Any:
    """
    Check the status of the server.

    Returns:
        dict: The status of the server.
    """

    try:
        system_time = db.execute(text("SELECT datetime('now')")).first()[0]
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"status": "ok", "system_time": system_time}
