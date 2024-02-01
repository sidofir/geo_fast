from enum import Enum


class GeolocationStatus(str, Enum):
    PENDING = "Pending"
    RESOLVED = "Resolved"
    ERROR = "Error"
