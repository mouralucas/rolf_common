import uuid

from pydantic import Field

from rolf_common.schemas import SuccessResponseBase


class RequiredUser(SuccessResponseBase):
    user_id: uuid.UUID = Field(..., serialization_alias='userId')
    # Add info as needed
