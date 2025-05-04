from pydantic import BaseModel


class OwnJobListResponse(BaseModel):
    result: str
    data: dict

