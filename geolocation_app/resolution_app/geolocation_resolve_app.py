import logging
import socket

import requests
from fastapi import FastAPI
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from geolocation_app.utils.db_handler import GeolocationRequestModel, get_db
from geolocation_app.utils.status import GeolocationStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("geolocation_resolve_app.log"),
    ],
)

app = FastAPI()

# Set up a background scheduler
scheduler = BackgroundScheduler()
scheduler.start()


def resolve_geolocation(db: Session, request_id: str, domain: str):
    """
    Resolve geolocation information for a given domain and update the database.

    Args:
        db (Session): SQLAlchemy database session.
        request_id (str): Unique ID of the geolocation request.
        domain (str): Domain for which geolocation is to be resolved.
    """
    locations = set()
    servers = set()

    try:
        ip_addresses = socket.gethostbyname_ex(domain)[2]

        for ip_address in ip_addresses:
            try:
                response = requests.get(f"http://ip-api.com/json/{ip_address}")
                data = response.json()

                # Get location information
                country = data.get('country', 'N/A')
                region = data.get('regionName', 'N/A')
                locations.add(f"{country}/{region}")
                servers.add(ip_address)

            except Exception as e:
                logging.error(f"Error getting location for IP {ip_address}: {e}")

        status = GeolocationStatus.RESOLVED if locations else GeolocationStatus.ERROR

        try:
            with db.begin_nested():
                db.query(GeolocationRequestModel).filter(GeolocationRequestModel.id == request_id).update(
                    {"status": status, "locations": ", ".join(locations), "servers": str(list(servers))}
                )

                if db.is_active:
                    db.commit()
        except InvalidRequestError:
            logging.warning("Transaction already in progress. Skipping update.")

    except socket.gaierror:
        logging.error(f"Unable to resolve the domain: {domain}")
        db.query(GeolocationRequestModel).filter(GeolocationRequestModel.id == request_id).update(
            {"status": GeolocationStatus.ERROR}
        )
    finally:
        db.commit()


def process_pending_requests_closure():
    """
       Closure to create a function to process pending geolocation requests.
       """
    def process_pending_requests(db: Session = next(get_db())):
        """
        Process pending geolocation requests from the database.

        Args:
            db (Session): SQLAlchemy database session.
        """
        pending_requests = (
            db.query(GeolocationRequestModel)
            .filter(GeolocationRequestModel.status == GeolocationStatus.PENDING)
            .all()
        )

        # Process each pending request in the background
        for request in pending_requests:
            scheduler.add_job(
                resolve_geolocation,
                args=[db, request.id, request.domain],
                id=request.id,
                misfire_grace_time=60,  # Allow jobs to be delayed by at most 60 seconds
            )
            logging.info(f"Scheduled resolution for request ID {request.id}")

    return process_pending_requests


def startup_event():
    """
     Schedule background task to process pending geolocation requests on startup.
     """
    trigger = IntervalTrigger(minutes=1)
    scheduler.add_job(process_pending_requests_closure(), trigger)
    logging.info("Scheduled background task to process pending geolocation requests.")


def shutdown_event():
    """
     Shut down the background scheduler on shutdown.
     """
    scheduler.shutdown()
    logging.info("Shutting down the background scheduler.")


app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
