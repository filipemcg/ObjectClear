from pydantic import BaseModel, Field
from typing import Annotated, Literal, Union

class MetaDataV1(BaseModel):
    version: Literal["v1"] = "v1"
    original_uri: str | None = None
    removed_uri: str | None = None

class MetaStatus(BaseModel):
    status: Literal["QUEUED", "PENDING", "COMPLETED", "FAILED"]
    data: Annotated[Union[MetaDataV1], Field(discriminator='version')] = None

class JobStatus(BaseModel):
    hash: Literal["OBJECT_CLEAR"]
    range: str
    meta: MetaStatus