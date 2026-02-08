from pydantic import BaseModel, Field
from typing import Annotated, Union, Literal


class ObjectRemovalDataV1(BaseModel):
    version: Literal['v1']
    project_id: Literal['MINAS', 'ROSA']
    content_id: int
    phone: str
    domain: str
    url: str


class ObjectRemovalRequest(BaseModel):
    job: Literal['OBJECT_REMOVAL']
    meta: Annotated[Union[ObjectRemovalDataV1], Field(discriminator='version')]


class JobEnvelope(BaseModel):
    request_id: str
    payload: Annotated[Union[ObjectRemovalRequest], Field(discriminator='job')]