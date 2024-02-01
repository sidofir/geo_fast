import re
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from geolocation_app.utils.consts import HOST
from geolocation_app.utils.db_handler import GeolocationRequestModel, get_db

app = FastAPI()


@app.get("/most_popular_domains/", response_model=list)
async def get_most_popular_domains(n: int = 5, db: Session = Depends(get_db)):
    """
    Get the N most popular domains.

    Args:
        n (int): Number of domains to retrieve.
        db (Session): SQLAlchemy database session.

    Returns:
        list: List of dictionaries with "domain" and "request_count" keys.
    """
    most_popular_domains = db.query(
        GeolocationRequestModel.domain,
        func.count(GeolocationRequestModel.domain).label("request_count")
    ).group_by(GeolocationRequestModel.domain).order_by(
        desc("request_count")
    ).limit(n).all()

    return [{"domain": domain, "request_count": request_count} for domain, request_count in most_popular_domains]


@app.get("/most_popular_servers/", response_model=list)
async def get_most_popular_servers(n: int = 3, db: Session = Depends(get_db)):
    """
    Get the N most popular servers.

    Args:
        n (int): Number of servers to retrieve.
        db (Session): SQLAlchemy database session.

    Returns:
        list: List of dictionaries with "server" and "request_count" keys.
    """
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    result = db.query(GeolocationRequestModel.servers).filter(GeolocationRequestModel.servers != '').all()

    if not result:
        raise HTTPException(status_code=404, detail="No data found")

    servers_count = {}

    for row in result:
        servers = re.findall(ip_pattern, row.servers)
        for server in servers:
            servers_count[server] = servers_count.get(server, 0) + 1

    sorted_servers = sorted(servers_count.items(), key=lambda x: x[1], reverse=True)[:n]

    return [{"server": server, "request_count": count} for server, count in sorted_servers]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=8006)