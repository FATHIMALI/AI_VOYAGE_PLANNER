import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEOAPIFY_API_KEY")

print("API KEY FOUND:", bool(API_KEY))

params = {
    "text": "Chennai, India",
    "filter": "countrycode:in",
    "type": "city",
    "limit": 5,
    "format": "json",
    "apiKey": API_KEY
}

url = "https://api.geoapify.com/v1/geocode/search"

response = requests.get(
    url,
    params=params,
    timeout=20
)

print("STATUS:", response.status_code)

print(
    response.text[:2000]
)