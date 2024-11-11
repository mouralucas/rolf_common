from pydantic import BaseModel, ConfigDict, Field, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake


class SuccessResponseBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(True, serialization_alias='success')
    status_code: int = Field(None, serialization_alias='statusCode', json_schema_extra={"deprecated": True})


class DefaultModel(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=AliasGenerator(
                                  alias=to_camel,
                                  validation_alias=to_snake,
                                  serialization_alias=to_camel,
                              ))
