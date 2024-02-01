import requests
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse

from geolocation_app.utils import consts
from tests import (
    test_create_geolocation_request,
    test_read_geolocation_status,
    test_get_most_popular_servers,
    test_get_most_popular_domains,
    test_get_domains_by_country,
    test_get_domains_by_server,
)

app = FastAPI()


def tests_page():
    """
    HTML page containing forms to run various tests.
    """

    return """
    <html>
        <head>
            <title>Test Results</title>
        </head>
        <body>
            <h1>Test Results</h1>
            <ul>
                <li>
                    <form action="/test_create_geolocation_request" method="get">
                        <label for="domain">Domain:</label>
                        <input type="text" id="domain" name="domain" required>
                        <button type="submit">Run Test: Create Geolocation Request</button>
                    </form>
                </li>
                <li>
                    <form action="/test_read_geolocation_status" method="get">
                        <label for="domain">Request ID:</label>
                        <input type="text" id="request_id" name="request_id" required>
                        <button type="submit">Run Test: Read Geolocation Status</button>
                    </form>
                </li>
                <li>
                    <form action="/test_get_most_popular_servers" method="get">
                        <label for="n">N:</label>
                        <input type="number" id="n" name="n" required>
                        <button type="submit">Run Test: Get Most Popular Servers</button>
                    </form>
                </li>
                <li>
                    <form action="/test_get_most_popular_domains" method="get">
                        <label for="n">N:</label>
                        <input type="number" id="n" name="n" required>
                        <button type="submit">Run Test: Get Most Popular Domains</button>
                    </form>
                </li>
                <li>
                    <form action="/test_get_domains_by_country" method="get">
                        <label for="country_name">Country:</label>
                        <input type="text" id="country_name" name="country_name" required>
                        <button type="submit">Run Test: Get Domains by Country</button>
                    </form>
                </li>
                <li>
                    <form action="/test_get_domains_by_server" method="get">
                        <label for="ip_address">Server IP:</label>
                        <input type="text" id="ip_address" name="ip_address" required>
                        <button type="submit">Run Test: Get Domains by Server</button>
                    </form>
                </li>
            </ul>
        </body>
    </html>
    """


@app.get("/test_create_geolocation_request", response_class=HTMLResponse)
async def run_test_create_geolocation_request(domain: str):
    """
    Run the test for creating a geolocation request.

    Args:
        domain (str): Domain for the geolocation request.

    Returns:
        HTMLResponse: Test results.
    """
    try:
        result = test_create_geolocation_request(domain=domain)
        return f"<h2>Test: Create Geolocation Request</h2><p>Request ID: {result}</p>"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/test_read_geolocation_status", response_class=HTMLResponse)
async def run_test_read_geolocation_status(request_id: str):
    """
     Run the test for reading geolocation status.

     Args:
         request_id (str): Unique ID of the geolocation request.

     Returns:
         HTMLResponse: Test results.
     """
    try:
        status, locations = test_read_geolocation_status(request_id=request_id)
        return f"<h2>Test: Read Geolocation Status</h2><p>Status: {status}</p><p>Locations: {locations}</p>"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/test_get_most_popular_servers", response_class=HTMLResponse)
async def run_test_get_most_popular_servers(n: int):
    """
    Run the test for getting the most popular servers.

    Args:
        n (int): Number of servers to retrieve.

    Returns:
        HTMLResponse: Test results.
    """
    try:
        result = test_get_most_popular_servers(n=n)
        formatted_result = "\n".join([f"{entry['server']}: {entry['request_count']}" for entry in result])
        return f"<h2>Test: Get Most Popular Servers</h2><p>{formatted_result}</p>"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/test_get_most_popular_domains", response_class=HTMLResponse)
async def run_test_get_most_popular_domains(n: int):
    """
    Run the test for getting the most popular domains.

    Args:
        n (int): Number of domains to retrieve.

    Returns:
        HTMLResponse: Test results.
    """
    try:
        result = test_get_most_popular_domains(n=n)
        formatted_result = "\n".join([f"{entry['domain']}: {entry['request_count']}" for entry in result])
        return f"<h2>Test: Get Most Popular Domains</h2><p>{formatted_result}</p>"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/test_get_domains_by_country", response_class=HTMLResponse)
async def run_test_get_domains_by_country(country_name: str):
    """
    Run the test for getting domains by country.

    Args:
        country_name (str): Name of the country.

    Returns:
        HTMLResponse: Test results.
    """
    try:
        result = test_get_domains_by_country(country_name=country_name)
        formatted_result = "\n".join(result) if result else "No domains found for the country."
        return f"<h2>Test: Get Domains by Country</h2><p>{formatted_result}</p>"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/test_get_domains_by_server", response_class=HTMLResponse)
async def run_test_get_domains_by_server(ip_address: str):
    """
    Run the test for getting domains by server.

    Args:
        ip_address (str): IP address of the server.

    Returns:
        HTMLResponse: Test results.
    """
    try:
        result = test_get_domains_by_server(ip_address=ip_address)
        formatted_result = "\n".join(result) if result else "No domains found for the server."
        return f"<h2>Test: Get Domains by Server</h2><p>{formatted_result}</p>"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


def register_user(username, password):
    """
    Register a user and return the response text.

    Args:
        username (str): User's username.
        password (str): User's password.

    Returns:
        str: Response text.
    """
    register_url = f"{consts.BASE_URL_LOGIN}/register"
    data = {"username": username, "password": password}
    response = requests.post(register_url, data=data)
    response.raise_for_status()
    return response.text


def login_and_get_token(username, password):
    """
    Login and get the access token.

    Args:
        username (str): User's username.
        password (str): User's password.

    Returns:
        str: Access token.
    """
    login_url = f"{consts.BASE_URL_LOGIN}/token"
    data = {"username": username, "password": password}
    response = requests.post(login_url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Root endpoint with links to register and login pages.

    Returns:
        HTMLResponse: Test results.
    """

    return """
    <html>
        <head>
            <title>Test Results</title>
        </head>
        <body>
            <h1>Test Results</h1>
            <ul>
                <li>
                    <form action="/register" method="get">
                        <button type="submit">Register</button>
                    </form>
                </li>
                <li>
                    <form action="/login" method="get">
                        <button type="submit">Login</button>
                    </form>
                </li>
            </ul>
        </body>
    </html>
    """


@app.get("/register", response_class=HTMLResponse)
async def register_form():
    """
    Registration form HTML page.

    Returns:
        HTMLResponse: Registration form.
    """

    return """
    <html>
        <head>
            <title>Register</title>
        </head>
        <body>
            <h1>Register</h1>
            <form action="/register" method="post">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
                <button type="submit">Register</button>
            </form>
        </body>
    </html>
    """


@app.post("/register", response_class=HTMLResponse)
async def register(username: str = Form(...), password: str = Form(...)):
    """
    Register a user.

    Args:
        username (str): User's username.
        password (str): User's password.

    Returns:
        HTMLResponse: Registration result.
    """
    try:
        response_text = register_user(username, password)
        return HTMLResponse(content=response_text, status_code=200)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/login", response_class=HTMLResponse)
async def login_form():
    """
    Login form HTML page.

    Returns:
        HTMLResponse: Login form.
    """

    return """
    <html>
        <head>
            <title>Login</title>
        </head>
        <body>
            <h1>Login</h1>
            <form action="/login" method="post">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    """


@app.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Login and display test options.

    Args:
        username (str): User's username.
        password (str): User's password.

    Returns:
        HTMLResponse: Test options.
    """
    try:
        token = login_and_get_token(username, password)
        return tests_page()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
