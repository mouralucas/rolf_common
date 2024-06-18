import uuid

from fastapi.openapi.models import Schema
from pydantic import Field


class RequireUserResponse(Schema):
    user_id: uuid.UUID = Field(..., serialization_alias='userId')
