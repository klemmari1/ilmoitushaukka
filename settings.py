import os

from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

BASE_URL = "https://bbs.io-tech.fi"


HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "3600",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
}


# Load ENV variables
HOST_NAME = os.getenv("HOST_NAME", "test")

SECRET_KEY = os.getenv("SECRET_KEY", "test")

FROM_EMAIL = os.getenv("FROM_EMAIL", "a@b.com")

EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "test")
