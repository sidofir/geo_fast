from fastapi import Depends, HTTPException, FastAPI
from sqlalchemy.orm import Session

from geolocation_app.utils.consts import HOST
from geolocation_app.utils.db_handler import GeolocationRequestModel, get_db

app = FastAPI()


@app.get("/get_domains_by_country/{country_name}", response_model=list[str])
async def get_domains_by_country(
    country_name: str, db: Session = Depends(get_db)
):
    """
    Retrieve domains associated with a specific country.
    """
    country_records = (
        db.query(GeolocationRequestModel)
        .filter(GeolocationRequestModel.locations.contains(country_name))
        .all()
    )

    if country_records:
        return [record.domains for record in country_records]
    else:
        raise HTTPException(status_code=404, detail=f"No records found for country: {country_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=8007)
