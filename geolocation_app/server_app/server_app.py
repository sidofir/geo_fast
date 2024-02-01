from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from geolocation_app.utils.consts import HOST
from geolocation_app.utils.db_handler import GeolocationRequestModel, get_db

app = FastAPI()


@app.get("/get_domains_by_server/", response_model=list)
async def get_domains_by_server(ip_address: str, db: Session = Depends(get_db)):
    """
    Get domains associated with a given server IP address.

    Args:
        ip_address (str): IP address of the server.
        db (Session): SQLAlchemy database session.

    Returns:
        list: List of domain names associated with the server.
    """
    matching_domains = db.query(GeolocationRequestModel).filter(
        GeolocationRequestModel.servers.contains(ip_address)
    ).all()

    domains = [domain.domain for domain in matching_domains]

    return domains


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=8004)
