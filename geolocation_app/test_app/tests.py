import logging
import requests
from geolocation_app.utils import consts
from fastapi import status
from geolocation_app.utils.models import GeolocationRequestParams, GeolocationResponse, GeolocationStatusResponseModel


def test_create_geolocation_request(domain):
    url = f"{consts.BASE_URL_GEOREQUEST}/geolocation/request/"
    data = GeolocationRequestParams(domain=domain).dict()

    try:
        response = requests.post(url, params=data)
        response.raise_for_status()

        if response.status_code == status.HTTP_200_OK:
            response_data = GeolocationResponse(**response.json())
            logging.info(f"Geolocation request created successfully. Request ID: {response_data.request_id}")
            return response_data.request_id
        elif response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            logging.info("Domain already exists. Test passed.")
            return None
    except requests.RequestException as e:
        logging.error(f"Error creating geolocation request: {e}")
        raise


def test_read_geolocation_status(request_id):
    try:
        url = f"{consts.BASE_URL_STATUS}/geolocation/status/{request_id}"
        response = requests.get(url)
        response.raise_for_status()

        assert response.status_code == 200
        response_data = GeolocationStatusResponseModel(**response.json())
        logging.critical(f"Geolocation status retrieved successfully for Request ID: {request_id}, "
                         f"Status: {response_data.status}, Locations: {response_data.locations}")

        return response_data.status, response_data.locations

    except requests.RequestException as e:
        logging.error(f"Error retrieving geolocation status: {e}")
        raise


def test_get_most_popular_domains(n):
    url = f"{consts.BASE_URL_POPULARITY}/most_popular_domains/"
    params = {"n": n}
    response = requests.get(url, params=params)

    assert response.status_code == 200
    data = response.json()
    logging.info(f"Most popular domains: {data}")
    assert isinstance(data, list)
    assert all("domain" in entry and "request_count" in entry for entry in data)

    return data


def test_get_most_popular_servers(n):
    url = f"{consts.BASE_URL_POPULARITY}/most_popular_servers/"
    params = {"n": n}
    response = requests.get(url, params=params)

    assert response.status_code == 200
    data = response.json()
    logging.info(f"Most popular servers: {data}")
    assert isinstance(data, list)
    assert all("server" in entry and "request_count" in entry for entry in data)

    return data


def test_get_domains_by_country(country_name):
    url = f"{consts.BASE_URL_COUNTRY}/get_domains_by_country/{country_name}"
    response = requests.get(url)

    try:
        response.raise_for_status()

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            logging.info(f"Domains in {country_name}: {data}")
            assert isinstance(data, list)
            return data
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            logging.info("Country not found. Test passed.")
            return None
    except requests.RequestException as e:
        logging.error(f"Error getting domains by country: {e}")
        raise


def test_get_domains_by_server(ip_address):
    url = f"{consts.BASE_URL_SERVER}/get_domains_by_server/"
    params = {"ip_address": ip_address}
    response = requests.get(url, params=params)

    try:
        response.raise_for_status()

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            logging.info(f"Domains mapped to server {ip_address}: {data}")
            assert isinstance(data, list)
            return data
    except requests.RequestException as e:
        logging.error(f"Error getting domains by server: {e}")
        raise
