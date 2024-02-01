from pydantic import BaseModel
from typing import List


class GeolocationResponse(BaseModel):
    request_id: str


class GeolocationRequestParams(BaseModel):
    domain: str


class GeolocationStatusRequestModel(BaseModel):
    request_id: str


class GeolocationStatusResponseModel(BaseModel):
    status: str
    locations: List[str]