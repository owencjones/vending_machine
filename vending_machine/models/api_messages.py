from typing import Literal

from pydantic import BaseModel


class ApiMessage(BaseModel):
    message: str
    success: Literal["true", "false"]
    errors: list[str] = []
