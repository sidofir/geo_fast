from datetime import datetime
import hashlib

from fastapi import FastAPI, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from geolocation_app.utils.consts import HOST
from geolocation_app.utils.db_handler import GeolocationRequestModel, get_db
from geolocation_app.utils.models import GeolocationResponse, GeolocationRequestParams

app = FastAPI()


def create_geolocation_request(db: Session, params: GeolocationRequestParams):
    """
    Create a geolocation request and return the request ID.

    Args:
        db (Session): SQLAlchemy database session.
        params (GeolocationRequestParams): Geolocation request parameters.

    Returns:
        str: Request ID.
    """
    try:
        timestamp = str(datetime.now())
        data_to_hash = f"{params.domain}{timestamp}"

        request_id = hashlib.sha256(data_to_hash.encode()).hexdigest()
        db_request = GeolocationRequestModel(id=request_id, domain=params.domain, servers="")
        db.add(db_request)
        db.commit()
    except IntegrityError:
        db.rollback()
        error_message = {"error": "Domain already exists"}
        return JSONResponse(content=error_message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return request_id


@app.post("/geolocation/request", response_model=GeolocationResponse, status_code=status.HTTP_200_OK)
async def geolocation_request(params: GeolocationRequestParams = Depends()):
    """
    Endpoint to create a geolocation request.

    Args:
        params (GeolocationRequestParams): Geolocation request parameters.

    Returns:
        GeolocationResponse: Response containing the request ID.
    """
    response = create_geolocation_request(next(get_db()), params)
    return GeolocationResponse(request_id=response)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=8001)
