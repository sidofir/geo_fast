#!/bin/bash

export PYTHONPATH=/home/sidney/code/geo_fast

# Run each app in the background
python geolocation_app/country_app/country_app.py &
python geolocation_app/login_app/login_app.py &
python geolocation_app/popularity_app/popularity_app.py &
python geolocation_app/request_app/geolocation_request_app.py &
python geolocation_app/resolution_app/geolocation_resolve_app.py &
python geolocation_app/server_app/server_app.py &
python geolocation_app/status_app/status_app.py &
python geolocation_app/test_app/test_app.py &


echo "All apps started."