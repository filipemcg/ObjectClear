from pydantic import BaseModel
from typing import Literal, Union

class MetaDataV1(BaseModel):
    version: Literal["v1"] = "v1"
    original_uri: str | None
    removed_uri: str | None

class MetaStatus(BaseModel):
    status: Literal["QUEUED", "PENDING", "COMPLETED", "FAILED"]
    data: Union[MetaDataV1] | None = None

class JobStatus(BaseModel):
    hash: Literal["OBJECT_CLEAR"]
    range: str
    meta: MetaStatus
