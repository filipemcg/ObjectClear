from pydantic import BaseModel, model_validator
from typing import Union, Literal, Any

class ObjectRemovalData(BaseModel):
    project_id: Literal['MINAS', 'ROSA']
    content_id: int

class PostJobRequest(BaseModel):
    job: Literal['OBJECT_REMOVAL']
    meta: Union[ObjectRemovalData]

    @model_validator(mode='before')
    def dispatch_before(values: dict[str, Any]) -> dict[str, Any]:
        job = values.get('job')
        meta = values.get('meta')
        if isinstance(meta, dict):
            if job == 'OBJECT_REMOVAL':
                values['meta'] = ObjectRemovalData.model_validate(meta)
        return values

class JobEnvelope(BaseModel):
    request_id: str
    payload: Union[PostJobRequest]