from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from geolocation_app.utils.db_handler import User, get_db

app = FastAPI()

SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create an access token.

    Args:
        data (dict): Data to encode into the token.
        expires_delta (timedelta, optional): Expiration time for the token.

    Returns:
        str: Generated access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception=HTTPException(status_code=401, detail="Could not validate credentials")):
    """
    Verify the given access token.

    Args:
        token (str): Access token to be verified.
        credentials_exception (HTTPException, optional): Exception on verification failure.

    Returns:
        TokenData: Decoded token data.
    """
    credentials_exception = credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


# Routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Generate an access token based on user credentials.

    Args:
        form_data (OAuth2PasswordRequestForm): User credentials (username and password).
        db (Session): SQLAlchemy database session.

    Returns:
        Token: Generated access token.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if user and app.password_hasher.verify(form_data.password, user.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/register", response_class=HTMLResponse)
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Register a new user with a username and password.

    Args:
        username (str): User's chosen username.
        password (str): User's chosen password.
        db (Session): SQLAlchemy database session.

    Returns:
        str: HTML response indicating successful registration.
    """
    hashed_password = app.password_hasher.hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return """
    <html>
        <head>
            <title>Registration Successful</title>
        </head>
        <body>
            <h1>Registration Successful</h1>
            <p>You have successfully registered. <a href="/login">Login</a></p>
        </body>
    </html>
    """


@app.get("/login", response_class=HTMLResponse)
async def login_form():
    """
    Display an HTML login form.

    Returns:
        str: HTML form for user login.
    """
    return """
    <html>
        <head>
            <title>Login</title>
        </head>
        <body>
            <h1>Login</h1>
            <form action="/token" method="post">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required><br>
                <input type="submit" value="Login">
            </form>
        </body>
    </html>
    """


@app.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Validate user credentials and generate an access token upon successful login.

    Args:
        username (str): User's entered username.
        password (str): User's entered password.
        db (Session): SQLAlchemy database session.

    Returns:
        str: HTML response indicating login success or failure.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and app.password_hasher.verify(password, user.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
        return """
        <html>
            <head>
                <title>Login Successful</title>
            </head>
            <body>
                <h1>Login Successful</h1>
                <p>Welcome, {username}!</p>
                <p>Access Token: {access_token}</p>
                <a href="/tests">Go to Tests</a>
            </body>
        </html>
        """
    else:
        return """
        <html>
            <head>
                <title>Login Failed</title>
            </head>
            <body>
                <h1>Login Failed</h1>
                <p>Invalid credentials. <a href="/login">Try again</a></p>
            </body>
        </html>
        """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
