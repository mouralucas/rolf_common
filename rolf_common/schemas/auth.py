import uuid

from pydantic import Field, BaseModel

from rolf_common.schemas import SuccessResponseBase


class RequiredUser(BaseModel):
    user_id: uuid.UUID = Field(..., serialization_alias='userId')
