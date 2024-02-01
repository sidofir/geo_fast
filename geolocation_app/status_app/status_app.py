from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from geolocation_app.utils.consts import HOST
from geolocation_app.utils.db_handler import GeolocationRequestModel, get_db

app = FastAPI()


@app.get("/geolocation/status/{request_id}", response_model=dict)
async def get_status(request_id: str, db: Session = Depends(get_db)):
    """
    Get the status and locations of a geolocation request.

    Args:
        request_id (str): Unique ID of the geolocation request.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Dictionary containing the status and locations of the geolocation request.
    """

    geolocation_request = db.query(GeolocationRequestModel).filter(GeolocationRequestModel.id == request_id).first()

    if not geolocation_request:
        raise HTTPException(status_code=404, detail="Request ID not found")

    status = geolocation_request.status
    locations = geolocation_request.locations.split(", ") if geolocation_request.locations else []

    response_data = {"status": status, "locations": locations}
    return JSONResponse(content=response_data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=8005)
