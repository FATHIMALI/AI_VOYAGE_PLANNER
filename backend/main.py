"""
AI Voyage Planner Backend

FastAPI backend for:
- Destination discovery
- Attraction discovery
- Live Geoapify places
- Live Geoapify hotels
- Live Geoapify local shops
- Geoapify live routing
- OpenWeather weather
- Trip planning
- Dynamic itinerary replanning
- Local tourism datasets
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import sys

from datetime import date
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"

load_dotenv(PROJECT_DIR / ".env")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Voyage Planner API",
    description="AI-powered personalized travel planning system",
    version="3.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class TripRequest(BaseModel):

    origin: str = Field(
        min_length=2,
        max_length=80
    )

    destination: str = Field(
        min_length=2,
        max_length=80
    )

    start_date: date | None = None

    end_date: date | None = None

    travelers: int = Field(
        default=1,
        ge=1,
        le=20
    )

    budget: int = Field(
        default=50000,
        ge=1000,
        le=10_000_000
    )

    interests: list[str] = Field(
        default_factory=list
    )

    lunch_preference: str = Field(
        default="both",
        pattern="^(vegetarian|non_vegetarian|both)$"
    )


class ReplanRequest(BaseModel):

    destination: str

    event_type: str

    event_description: str = ""

    itinerary: list = Field(
        default_factory=list
    )

    approved_activities: list = Field(
        default_factory=list
    )

    travelers: int = 1

    budget: float = 0

    interests: list = Field(
        default_factory=list
    )


# ============================================================
# DATA HELPERS
# ============================================================

@lru_cache(maxsize=32)
def read_csv(
    relative_path: str,
) -> tuple[dict[str, str], ...]:

    file_path = DATA_DIR / relative_path

    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return tuple(
            dict(row)
            for row in csv.DictReader(file)
        )


def ensure_data_file(
    relative_path: str,
) -> None:

    if not (
        DATA_DIR / relative_path
    ).is_file():

        raise HTTPException(
            status_code=503,
            detail=(
                f"Required dataset is unavailable: "
                f"{relative_path}"
            ),
        )


def safe_float(value, default=0.0):

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def safe_int(value, default=0):

    try:
        return int(float(value))

    except (
        TypeError,
        ValueError,
    ):
        return default


def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# GEOAPIFY GENERIC REQUEST
# ============================================================

def geoapify_json(endpoint, params):
    params = dict(params)

    api_key = os.getenv("GEOAPIFY_API_KEY", "").strip()
    if not api_key:
        return None

    params["apiKey"] = api_key

    # Geoapify Places API uses v2.
    # Geocoding and other APIs use v1.
    if endpoint == "places":
        base_url = "https://api.geoapify.com/v2"
    else:
        base_url = "https://api.geoapify.com/v1"

    url = f"{base_url}/{endpoint}?{urlencode(params, doseq=True)}"

    try:
        request = Request(
            url,
            headers={"User-Agent": "AI-Voyage-Planner/1.0"},
        )

        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)

    except URLError as exc:
        print(f"[GEOAPIFY] URL/HTTP error on {endpoint}: {exc}")
        return None

    except Exception as exc:
        print(f"[GEOAPIFY] Error on {endpoint}: {exc}")
        return None


# ============================================================
# GEOAPIFY GEOCODING
# ============================================================

def geoapify_coordinates(
    place: str,
) -> tuple[float, float] | None:
    place_clean = clean_text(place)
    if not place_clean:
        return None

    search_text = (
        place_clean
        if "india" in place_clean.lower()
        else f"{place_clean}, India"
    )

    data = geoapify_json(
        "geocode/search",
        {
            "text": search_text,
            "filter": "countrycode:in",
            "limit": "1",
        },
    )

    if not data:
        return None

    features = data.get("features", [])
    if not features:
        return None

    geometry = features[0].get("geometry", {})
    coordinates = geometry.get("coordinates", [])

    if len(coordinates) < 2:
        return None

    longitude = safe_float(coordinates[0])
    latitude = safe_float(coordinates[1])

    if latitude == 0 and longitude == 0:
        return None

    return (latitude, longitude)


# ============================================================
# LOCATION & DISTANCE VALIDATION
# ============================================================

def calculate_haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Calculate Great Circle distance in kilometers between two points."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def normalize_name(name: str) -> str:
    """Return a clean alphanumeric key for deduplication."""
    return re.sub(r"[^a-z0-9]", "", clean_text(name).lower())


# ============================================================
# ACCOMMODATION / HOSTEL FILTER
# ============================================================

def is_accommodation(
    name: str,
    categories: list | str | None = None,
    place_type: str = "",
) -> bool:
    """
    Check if a place is an accommodation/stay (hostel, hotel, lodge, etc.)
    and MUST NOT be recommended as a tourist destination.
    """
    name_clean = clean_text(name).lower()
    type_clean = clean_text(place_type).lower()

    if any(k in type_clean for k in (
        "hotel", "hostel", "lodge", "lodging", "accommodation",
        "resort", "guest house", "guesthouse", "dormitory", "motel",
        "inn", "homestay", "serviced apartment"
    )):
        return True

    clean_words = set(re.sub(r"[^a-z0-9\s]", " ", name_clean).split())
    blocked_words = {
        "hotel", "hostel", "lodge", "lodging", "motel", "dormitory", "dorm",
        "guesthouse", "homestay", "resort", "inn", "mews", "stay", "residency",
        "boarding", "suites", "palace hotel", "grand hotel", "resort hotel"
    }
    if clean_words & blocked_words:
        return True

    if any(phrase in name_clean for phrase in (
        "guest house", "bed & breakfast", "bed and breakfast",
        "pg for", "paying guest", "serviced apartment", "taj wellington mews"
    )):
        return True

    if categories:
        if isinstance(categories, list):
            cat_list = [str(c).lower() for c in categories]
        else:
            cat_list = [c.strip().lower() for c in str(categories).split(",")]
        for c in cat_list:
            if any(ac in c for ac in (
                "accommodation", "hotel", "hostel", "motel",
                "guest_house", "chalet", "apartment"
            )):
                return True

    return False


# ============================================================
# TIME PERIOD CLASSIFICATION
# ============================================================

def classify_place_periods(place: dict) -> set[str]:
    """
    Determine suitable time periods (morning, afternoon, evening) for a place.
    Morning: parks, beaches, temples, viewpoints, gardens, nature, morning spots.
    Afternoon: museums, shopping, indoor attractions, monuments, forts, science.
    Evening: beaches, viewpoints, sunsets, waterfronts, shopping, entertainment, cafes.
    """
    suitable = set()
    name = clean_text(place.get("name", "")).lower()
    place_type = clean_text(place.get("type", "")).lower()
    best_time = clean_text(place.get("best_time", "")).lower()
    categories = place.get("categories", [])
    if isinstance(categories, str):
        cat_text = categories.lower()
    else:
        cat_text = " ".join(str(c) for c in categories).lower()

    all_text = f"{name} {place_type} {best_time} {cat_text} {clean_text(place.get('significance', '')).lower()}"

    # Morning indicators
    morning_indicators = (
        "park", "garden", "beach", "temple", "shrine", "ashram", "mosque", "church",
        "cathedral", "religious", "nature", "sunrise", "viewpoint", "zoo", "botanical",
        "lake", "forest", "sanctuary", "waterfall", "morning", "early", "jogging", "walk"
    )
    if any(k in all_text for k in morning_indicators):
        suitable.add("morning")

    # Afternoon indicators
    afternoon_indicators = (
        "museum", "gallery", "shopping", "mall", "bazaar", "market", "monument",
        "fort", "palace", "memorial", "indoor", "science", "planetarium", "heritage",
        "culture", "historical", "centre", "center", "afternoon", "lunch", "exhibition"
    )
    if any(k in all_text for k in afternoon_indicators):
        suitable.add("afternoon")

    # Evening indicators
    evening_indicators = (
        "beach", "viewpoint", "sunset", "promenade", "waterfront", "lake", "shopping",
        "mall", "bazaar", "market", "entertainment", "theatre", "plaza", "square",
        "fountain", "amusement", "sound and light", "evening", "night", "cafe", "bistros"
    )
    if any(k in all_text for k in evening_indicators):
        suitable.add("evening")

    # Fallback versatile tourist attractions
    if not suitable:
        suitable.update(["morning", "afternoon", "evening"])

    return suitable


# ============================================================
# GEOAPIFY LIVE PLACE SEARCH
# ============================================================

def geoapify_place_search(
    city: str,
    categories: str,
    limit: int = 20,
) -> list[dict]:
    coordinates = geoapify_coordinates(city)
    if not coordinates:
        return []

    latitude, longitude = coordinates

    data = geoapify_json(
        "places",
        {
            "categories": categories,
            "filter": f"circle:{longitude},{latitude},25000",
            "bias": f"proximity:{longitude},{latitude}",
            "limit": str(limit),
        },
    )

    if not data:
        return []

    features = data.get("features", [])
    results = []
    seen = set()

    for feature in features:
        properties = feature.get("properties", {})
        name = clean_text(properties.get("name") or properties.get("formatted"))
        if not name or name.lower() in ("none", "null", ""):
            continue

        norm_name = normalize_name(name)
        if norm_name in seen:
            continue
        seen.add(norm_name)

        lat = safe_float(properties.get("lat"))
        lon = safe_float(properties.get("lon"))

        categories_found = properties.get("categories", [])

        results.append({
            "name": name,
            "address": properties.get("formatted", ""),
            "city": properties.get("city", city),
            "country": properties.get("country", "India"),
            "lat": lat,
            "lon": lon,
            "categories": categories_found if isinstance(categories_found, list) else [],
            "source": "Geoapify Live API",
        })

    return results[:limit]


# ============================================================
# LIVE TOURIST PLACES
# ============================================================

def get_live_tourist_places(
    city: str,
    limit: int = 60,
) -> list[dict]:
    """
    Get real tourist attractions from Geoapify.
    Excludes accommodation/hotels and ensures coordinates belong to the city.
    """
    coordinates = geoapify_coordinates(city)
    if not coordinates:
        print(f"[PLACES] Could not find coordinates for {city}")
        return []

    latitude, longitude = coordinates

    categories = (
        "tourism.attraction,"
        "tourism.sights,"
        "tourism.attraction.viewpoint,"
        "leisure.park,"
        "leisure.park.garden,"
        "entertainment.museum,"
        "entertainment.culture"
    )

    data = geoapify_json(
        "places",
        {
            "categories": categories,
            "filter": f"circle:{longitude},{latitude},35000",
            "bias": f"proximity:{longitude},{latitude}",
            "limit": str(limit),
        },
    )

    if not data:
        print(f"[PLACES] Geoapify returned no data for {city}")
        return []

    features = data.get("features", [])
    results = []
    seen = set()

    for feature in features:
        properties = feature.get("properties", {})
        name = clean_text(properties.get("name") or properties.get("formatted"))
        if not name or name.lower() in ("none", "null", ""):
            continue

        norm_name = normalize_name(name)
        if norm_name in seen:
            continue

        categories_found = properties.get("categories", [])
        if is_accommodation(name, categories_found, "Attraction"):
            continue

        lat = safe_float(properties.get("lat"))
        lon = safe_float(properties.get("lon"))

        # Distance validation
        if lat and lon:
            dist = calculate_haversine_distance(latitude, longitude, lat, lon)
            if dist > 40.0:
                continue

        seen.add(norm_name)

        results.append({
            "name": name,
            "address": properties.get("formatted", f"{name}, {city}"),
            "city": properties.get("city", city),
            "state": properties.get("state", ""),
            "country": properties.get("country", "India"),
            "lat": lat,
            "lon": lon,
            "categories": categories_found if isinstance(categories_found, list) else [],
            "type": "Attraction",
            "source": "Geoapify Live API",
        })

    print(f"[PLACES] {city}: {len(results)} validated real tourist places found")
    return results[:limit]


# ============================================================
# LIVE HOTELS
# ============================================================

def get_live_hotels(
    city: str,
    limit: int = 15,
) -> list[dict]:
    categories = (
        "accommodation.hotel,"
        "accommodation.resort,"
        "accommodation.guest_house"
    )
    return geoapify_place_search(
        city,
        categories,
        limit,
    )


# ============================================================
# LIVE LOCAL SHOPS
# ============================================================

def get_live_local_shops(
    city: str,
    limit: int = 15,
) -> list[dict]:
    categories = (
        "commercial.marketplace,"
        "commercial.shopping_mall,"
        "commercial.food_and_drink,"
        "commercial.supermarket"
    )
    return geoapify_place_search(
        city,
        categories,
        limit,
    )


# ============================================================
# LIVE RESTAURANTS
# ============================================================

def get_nearby_restaurants(
    place_name: str | None = None,
    destination: str | None = None,
    meal: str = "lunch",
    lunch_preference: str = "both",
    limit: int = 3,
    city: str | None = None,
    dest_coords: tuple[float, float] | None = None,
    used_names: set[str] | None = None,
) -> list[dict]:
    """
    Get restaurants genuinely located near destination.
    Relevant to meal period (breakfast/lunch/dinner) with dietary preferences.
    """
    dest_city = destination or city or place_name or ""
    anchor = place_name or dest_city

    if dest_coords is None and dest_city:
        dest_coords = geoapify_coordinates(dest_city)

    search_coords = None
    if anchor and dest_city and anchor.casefold() != dest_city.casefold():
        search_coords = geoapify_coordinates(f"{anchor}, {dest_city}")
        if search_coords and dest_coords:
            dist = calculate_haversine_distance(dest_coords[0], dest_coords[1], search_coords[0], search_coords[1])
            if dist > 25.0:
                search_coords = dest_coords

    if not search_coords:
        search_coords = dest_coords

    if not search_coords:
        return []

    latitude, longitude = search_coords

    meal_lower = clean_text(meal).lower()
    if meal_lower in ("breakfast", "morning"):
        categories = "catering.cafe,catering.fast_food,catering.restaurant"
    elif meal_lower in ("dinner", "evening"):
        categories = "catering.restaurant,catering.cafe"
    else:
        categories = "catering.restaurant"

    data = geoapify_json(
        "places",
        {
            "categories": categories,
            "filter": f"circle:{longitude},{latitude},15000",
            "bias": f"proximity:{longitude},{latitude}",
            "limit": "30",
        },
    )

    if not data:
        return []

    features = data.get("features", [])
    results = []
    seen = used_names if used_names is not None else set()

    for feature in features:
        properties = feature.get("properties", {})
        name = clean_text(properties.get("name") or properties.get("formatted"))
        if not name or name.casefold() in ("none", "null", ""):
            continue

        norm_name = normalize_name(name)
        if norm_name in seen:
            continue

        lat = safe_float(properties.get("lat"))
        lon = safe_float(properties.get("lon"))

        if lat and lon and dest_coords:
            dist = calculate_haversine_distance(dest_coords[0], dest_coords[1], lat, lon)
            if dist > 25.0:
                continue

        categories_found = properties.get("categories", [])
        cat_text = " ".join(str(c) for c in categories_found).casefold()

        if lunch_preference == "vegetarian":
            if any(x in cat_text for x in ("steakhouse", "barbecue", "meat")):
                continue

        results.append({
            "name": name,
            "address": properties.get("formatted", f"{name}, {dest_city}"),
            "city": properties.get("city", dest_city),
            "lat": lat,
            "lon": lon,
            "categories": categories_found if isinstance(categories_found, list) else [],
            "meal": meal,
            "preference": lunch_preference,
            "source": "Geoapify Live API",
        })
        seen.add(norm_name)

        if len(results) >= limit:
            break

    return results

# ============================================================
# GEOAPIFY ROUTING
# ============================================================

def geoapify_route(
    origin: str,
    destination: str,
) -> dict | None:

    origin_coordinates = (
        geoapify_coordinates(origin)
    )

    destination_coordinates = (
        geoapify_coordinates(destination)
    )

    if (
        not origin_coordinates
        or not destination_coordinates
    ):
        return None

    origin_lat, origin_lon = (
        origin_coordinates
    )

    destination_lat, destination_lon = (
        destination_coordinates
    )

    waypoints = (
        f"{origin_lat},{origin_lon}|"
        f"{destination_lat},{destination_lon}"
    )

    data = geoapify_json(
        "routing",
        {
            "waypoints":
                waypoints,

            "mode":
                "drive",
        },
    )

    if not data:
        return None

    features = data.get(
        "features",
        []
    )

    if not features:
        return None

    return features[0]


def geoapify_route_distance(
    origin: str,
    destination: str,
) -> int | None:

    route = geoapify_route(
        origin,
        destination
    )

    if not route:
        return None

    properties = route.get(
        "properties",
        {}
    )

    distance_meters = properties.get(
        "distance"
    )

    try:

        return round(
            float(distance_meters)
            / 1000
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


# ============================================================
# STATIC ROUTE MAP
# ============================================================

def geoapify_route_map(
    route: dict | None = None,
    origin: str = "",
    destination: str = "",
) -> tuple[bytes, str] | None:
    """
    Generate an uncropped, responsive map centered on India.
    Displays markers for destination (and origin if applicable),
    and plots the driving route polyline when available.
    """
    api_key = os.getenv("GEOAPIFY_API_KEY", "").strip()
    if not api_key:
        return None

    # Complete India map centering and zoom
    # Center: 79.5°E, 22.0°N (geographic center of India)
    # Dimensions: 1000x650 provides balanced framing so North, South, East, West are completely visible
    params = {
        "style": "osm-bright",
        "width": "1000",
        "height": "650",
        "center": "lonlat:79.5,22.0",
        "zoom": "4.2",
        "apiKey": api_key,
    }

    markers = []
    dest_coords = None
    if destination:
        dest_coords = geoapify_coordinates(destination)
        if dest_coords:
            markers.append(f"lonlat:{dest_coords[1]},{dest_coords[0]};color:#ef4444;size:medium;text:D")

    orig_coords = None
    if origin and origin.strip().lower() not in ("india", "none", "", destination.strip().lower()):
        orig_coords = geoapify_coordinates(origin)
        if orig_coords and orig_coords != dest_coords:
            markers.append(f"lonlat:{orig_coords[1]},{orig_coords[0]};color:#10b981;size:medium;text:O")

    if markers:
        params["marker"] = "|".join(markers)

    # Route polyline if available
    if route:
        geometry = route.get("geometry", {})
        coordinates = geometry.get("coordinates", [])
        if coordinates:
            route_points = coordinates
            if route_points and isinstance(route_points[0][0], list):
                route_points = [
                    point for line in route_points for point in line
                ]
            if len(route_points) >= 2:
                step = max(1, len(route_points) // 35)
                sampled = route_points[::step]
                if sampled[-1] != route_points[-1]:
                    sampled.append(route_points[-1])
                polyline = ",".join(
                    f"{point[0]:.5f},{point[1]:.5f}"
                    for point in sampled
                )
                params["geometry"] = (
                    f"polyline:{polyline};linecolor:#1d4ed8;linewidth:4"
                )

    try:
        url = f"https://maps.geoapify.com/v1/staticmap?{urlencode(params)}"
        request = Request(
            url,
            headers={"User-Agent": "AI-Voyage-Planner/1.0"},
        )
        with urlopen(request, timeout=15) as response:
            return (
                response.read(),
                response.headers.get_content_type(),
            )
    except Exception as exc:
        print("[MAP] Route map error:", exc)
        return None


# ============================================================
# LOCAL ITINERARY FALLBACK
# ============================================================

def create_local_exploration_days(
    destination: str,
    start_day: int,
    count: int,
) -> list[dict]:

    activities = [

        (
            "Heritage Walk",
            "Explore a historic neighbourhood "
            "and nearby cultural areas."
        ),

        (
            "Local Food Experience",
            "Explore local food streets, "
            "markets and popular local cuisine."
        ),

        (
            "Park and Leisure",
            "Spend time at a nearby park "
            "or public recreational area."
        ),

        (
            "Culture and Museum Day",
            "Explore a museum, cultural centre "
            "or local heritage attraction."
        ),
    ]

    days = []

    for offset in range(count):

        title, description = (
            activities[
                offset % len(activities)
            ]
        )

        day_number = (
            start_day + offset
        )

        days.append(
            {
                "day":
                    day_number,

                "title":
                    (
                        f"Day {day_number} — "
                        f"{title}"
                    ),

                "description":
                    (
                        f"{description} "
                        f"Destination: "
                        f"{destination}."
                    ),

                "source":
                    "AI Voyage Planner",
            }
        )

    return days



# ============================================================
# LIVE RESTAURANTS ENDPOINT
# ============================================================

@app.get("/api/live/restaurants")
def live_restaurants(
    city: str = Query(min_length=2, max_length=80),
    limit: int = Query(default=3, ge=1, le=20),
    meal: str = Query(default="lunch", max_length=20),
    lunch_preference: str = Query(
        default="both",
        pattern="^(vegetarian|non_vegetarian|both)$"
    ),
):
    restaurants = get_nearby_restaurants(
        place_name=city,
        destination=city,
        meal=meal,
        lunch_preference=lunch_preference,
        limit=limit,
    )
    return {
        "status": "success",
        "source": "Geoapify",
        "city": city,
        "meal": meal,
        "lunch_preference": lunch_preference,
        "items": restaurants,
    }


# ============================================================
# WEATHER - OPENWEATHER
# ============================================================

def get_weather(
    city: str,
) -> dict:

    api_key = os.getenv(
        "OPENWEATHER_API_KEY"
    )

    if not api_key:

        return {
            "status": "unavailable",
            "source": "OpenWeather",
            "message":
                "OpenWeather API key is not configured.",
        }

    try:

        params = {
            "q":
                f"{city},IN",

            "appid":
                api_key,

            "units":
                "metric",
        }

        url = (
            "https://api.openweathermap.org/"
            "data/2.5/weather?"
            f"{urlencode(params)}"
        )

        request = Request(
            url,
            headers={
                "User-Agent":
                    "AI-Voyage-Planner/1.0"
            },
        )

        with urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        weather = (
            data.get(
                "weather",
                [{}]
            )[0]
        )

        main = data.get(
            "main",
            {}
        )

        wind = data.get(
            "wind",
            {}
        )

        return {

            "status":
                "success",

            "source":
                "OpenWeather",

            "city":
                data.get(
                    "name",
                    city
                ),

            "country":
                data.get(
                    "sys",
                    {}
                ).get(
                    "country",
                    "IN"
                ),

            "temperature_c":
                main.get(
                    "temp"
                ),

            "feels_like_c":
                main.get(
                    "feels_like"
                ),

            "humidity":
                main.get(
                    "humidity"
                ),

            "wind_speed_mps":
                wind.get(
                    "speed"
                ),

            "description":
                weather.get(
                    "description",
                    ""
                ),

            "icon":
                weather.get(
                    "icon",
                    ""
                ),
        }

    except Exception as exc:

        print(
            "OpenWeather error:",
            exc
        )

        return {
            "status":
                "error",

            "source":
                "OpenWeather",

            "city":
                city,

            "message":
                "Weather service unavailable.",
        }


# ============================================================
# SUSTAINABILITY CALCULATION
# ============================================================

def calculate_sustainability_score(
    distance_km,
    emissions_kg,
    travelers,
    transport_mode,
    local_places_count,
):

    distance_km = (
        safe_float(
            distance_km
        )
    )

    emissions_kg = (
        safe_float(
            emissions_kg
        )
    )

    travelers = max(
        1,
        safe_int(
            travelers,
            1
        )
    )

    emissions_per_person = (
        emissions_kg / travelers
        if emissions_kg > 0
        else 0
    )

    # --------------------------------------------------------
    # Carbon score
    # --------------------------------------------------------

    if emissions_per_person <= 50:

        carbon_score = 30

    elif emissions_per_person <= 100:

        carbon_score = 25

    elif emissions_per_person <= 200:

        carbon_score = 18

    elif emissions_per_person <= 350:

        carbon_score = 10

    else:

        carbon_score = 5

    # --------------------------------------------------------
    # Transport score
    # --------------------------------------------------------

    mode = str(
        transport_mode or ""
    ).lower()

    if any(
        value in mode
        for value in [
            "walk",
            "cycle",
            "cycling",
        ]
    ):

        transport_score = 25

    elif any(
        value in mode
        for value in [
            "train",
            "metro",
            "public",
            "bus",
        ]
    ):

        transport_score = 20

    elif "shared" in mode:

        transport_score = 16

    elif "car" in mode:

        transport_score = 10

    elif "flight" in mode:

        transport_score = 5

    else:

        transport_score = 12

    # --------------------------------------------------------
    # Distance score
    # --------------------------------------------------------

    if distance_km <= 300:

        distance_score = 25

    elif distance_km <= 800:

        distance_score = 20

    elif distance_km <= 1500:

        distance_score = 15

    elif distance_km <= 2500:

        distance_score = 10

    else:

        distance_score = 5

    # --------------------------------------------------------
    # Local exploration score
    # --------------------------------------------------------

    if local_places_count >= 15:

        local_score = 15

    elif local_places_count >= 10:

        local_score = 13

    elif local_places_count >= 6:

        local_score = 10

    elif local_places_count >= 3:

        local_score = 7

    elif local_places_count >= 1:

        local_score = 5

    else:

        local_score = 2

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    total_score = (
        carbon_score
        + transport_score
        + distance_score
        + local_score
    )

    total_score = max(
        0,
        min(
            100,
            int(total_score)
        )
    )

    # --------------------------------------------------------
    # Level
    # --------------------------------------------------------

    if total_score >= 80:

        level = "Excellent"

    elif total_score >= 65:

        level = "Good"

    elif total_score >= 50:

        level = "Moderate"

    elif total_score >= 35:

        level = "Needs improvement"

    else:

        level = "High impact"

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation_parts = []

    if carbon_score >= 30:

        explanation_parts.append(
            "The estimated carbon impact "
            "per traveler is relatively low."
        )

    elif carbon_score >= 18:

        explanation_parts.append(
            "The estimated carbon impact "
            "is moderate."
        )

    else:

        explanation_parts.append(
            "The journey has a relatively "
            "high estimated carbon impact."
        )

    if transport_score >= 20:

        explanation_parts.append(
            "The selected transport mode "
            "has a relatively lower impact."
        )

    elif transport_score >= 12:

        explanation_parts.append(
            "Transport has a moderate "
            "sustainability impact."
        )

    else:

        explanation_parts.append(
            "A lower-impact transport "
            "alternative may improve the score."
        )

    if local_score >= 10:

        explanation_parts.append(
            "The destination has enough stored "
            "places to support local exploration."
        )

    else:

        explanation_parts.append(
            "Grouping nearby activities can "
            "reduce unnecessary local travel."
        )

    return {

        "sustainability_score":
            total_score,

        "sustainability_level":
            level,

        "carbon_score":
            carbon_score,

        "transport_score":
            transport_score,

        "distance_score":
            distance_score,

        "local_exploration_score":
            local_score,

        "emissions_per_traveler_kg":
            round(
                emissions_per_person,
                1
            ),

        "sustainability_explanation":
            " ".join(
                explanation_parts
            ),
    }


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "AI Voyage Planner Backend "
            "is running successfully!"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health_check():

    required_files = (

        "processed/destinations.csv",

        "master/places_master.csv",

        "processed/transport.csv",
    )

    available = all(

        (
            DATA_DIR / path
        ).is_file()

        for path in required_files
    )

    return {

        "status":
            "healthy"
            if available
            else "degraded",

        "service":
            "AI Voyage Planner",

        "data_directory":
            str(DATA_DIR),

        "data_available":
            available,

        "integrations": {

            "geoapify_configured":
                bool(
                    os.getenv(
                        "GEOAPIFY_API_KEY"
                    )
                ),

            "gemini_configured":
                bool(
                    os.getenv(
                        "GEMINI_API_KEY"
                    )
                ),

            "openweather_configured":
                bool(
                    os.getenv(
                        "OPENWEATHER_API_KEY"
                    )
                ),
        },
    }


# ============================================================
# ROUTE MAP
# ============================================================

@app.get("/api/routes/map")
def get_route_map(

    origin: str = Query(
        min_length=2,
        max_length=80,
    ),

    destination: str = Query(
        min_length=2,
        max_length=80,
    ),
):

    route = None
    try:
        route = geoapify_route(
            origin,
            destination,
        )
    except Exception as exc:
        print("[ROUTE] Route error:", exc)

    map_image = geoapify_route_map(
        route=route,
        origin=origin,
        destination=destination,
    )

    if not map_image:
        raise HTTPException(
            status_code=503,
            detail=(
                "A live route map is "
                "unavailable right now."
            ),
        )

    image, media_type = map_image

    return Response(
        content=image,
        media_type=media_type,
        headers={
            "Cache-Control":
                "public, max-age=900"
        },
    )


# ============================================================
# DESTINATIONS
# ============================================================

@app.get("/api/destinations")
def get_destinations(

    limit: int = Query(
        default=12,
        ge=1,
        le=100,
    ),
):

    dataset = (
        "master/places_master.csv"
    )

    ensure_data_file(
        dataset
    )

    rows = read_csv(
        dataset
    )

    items = list(
        dict.fromkeys(

            row.get(
                "city",
                ""
            )

            for row in rows

            if row.get(
                "city"
            )
        )
    )

    return {

        "items":
            items[:limit],

        "total":
            len(items),
    }


# ============================================================
# ATTRACTIONS
# ============================================================

@app.get("/api/attractions")
def get_attractions(

    city: str | None = Query(
        default=None,
        min_length=1,
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):

    dataset = (
        "master/places_master.csv"
    )

    ensure_data_file(
        dataset
    )

    rows = read_csv(
        dataset
    )

    if city:

        rows = tuple(

            row

            for row in rows

            if row.get(
                "city",
                ""
            ).casefold()
            == city.casefold()
        )

    return {

        "items":
            list(
                rows[:limit]
            ),

        "total":
            len(rows),
    }


# ============================================================
# LIVE PLACES ENDPOINT
# ============================================================

@app.get("/api/live/places")
def live_places(

    city: str = Query(
        min_length=2,
        max_length=80,
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=50,
    ),
):

    return {

        "status":
            "success",

        "source":
            "Geoapify",

        "city":
            city,

        "items":
            get_live_tourist_places(
                city,
                limit
            ),
    }


# ============================================================
# LIVE HOTELS ENDPOINT
# ============================================================

@app.get("/api/live/hotels")
def live_hotels(

    city: str = Query(
        min_length=2,
        max_length=80,
    ),

    limit: int = Query(
        default=15,
        ge=1,
        le=50,
    ),
):

    return {

        "status":
            "success",

        "source":
            "Geoapify",

        "city":
            city,

        "items":
            get_live_hotels(
                city,
                limit
            ),
    }


# ============================================================
# LIVE LOCAL SHOPS ENDPOINT
# ============================================================

@app.get("/api/live/shops")
def live_shops(

    city: str = Query(
        min_length=2,
        max_length=80,
    ),

    limit: int = Query(
        default=15,
        ge=1,
        le=50,
    ),
):

    return {

        "status":
            "success",

        "source":
            "Geoapify",

        "city":
            city,

        "items":
            get_live_local_shops(
                city,
                limit
            ),
    }

# ============================================================
# LIVE RESTAURANTS ENDPOINT
# ============================================================

@app.get("/api/live/restaurants")
def live_restaurants(

    city: str = Query(
        min_length=2,
        max_length=80,
    ),

    meal: str = Query(
        default="lunch",
        pattern="^(breakfast|lunch|dinner)$",
    ),

    lunch_preference: str = Query(
        default="both",
        pattern="^(vegetarian|non_vegetarian|both)$",
    ),

    limit: int = Query(
        default=3,
        ge=1,
        le=10,
    ),
):

    restaurants = get_nearby_restaurants(
        city=city,
        meal=meal,
        lunch_preference=lunch_preference,
        limit=limit,
    )

    return {
        "status": "success",
        "source": "Geoapify",
        "city": city,
        "meal": meal,
        "lunch_preference": lunch_preference,
        "items": restaurants,
    }


# ============================================================
# WEATHER ENDPOINT
# ============================================================

@app.get("/api/weather")
def weather_endpoint(

    city: str = Query(
        min_length=2,
        max_length=80,
    ),
):

    return get_weather(
        city
    )


# ============================================================
# TRANSPORT
# ============================================================

@app.get("/api/transport")
def get_transport(

    origin: str | None = Query(
        default=None,
        min_length=1,
    ),

    destination: str | None = Query(
        default=None,
        min_length=1,
    ),
):

    dataset = (
        "processed/transport.csv"
    )

    ensure_data_file(
        dataset
    )

    rows = read_csv(
        dataset
    )

    if origin:

        rows = tuple(

            row

            for row in rows

            if row.get(
                "origin",
                ""
            ).casefold()
            == origin.casefold()
        )

    if destination:

        rows = tuple(

            row

            for row in rows

            if row.get(
                "destination",
                ""
            ).casefold()
            == destination.casefold()
        )

    return {

        "items":
            list(rows),

        "total":
            len(rows),
    }



# ============================================================
# SMART ITINERARY
# ============================================================

def _place_score(place: dict, interests: list[str]) -> int:
    text = " ".join(str(v or "") for v in place.values()).casefold()
    score = 0
    for interest in interests:
        if str(interest).casefold() in text:
            score += 3
    rating = safe_float(place.get("rating"), 0)
    if rating:
        score += int(rating * 2)
    return score


def get_all_destination_places(
    destination: str,
    dest_coords: tuple[float, float] | None = None,
) -> list[dict]:
    """
    Retrieve and validate local curated tourist places for destination
    from all available datasets, strictly excluding accommodation and
    ensuring location matches the destination.
    """
    dest_clean = clean_text(destination).casefold()
    results = []
    seen = set()

    # 1. Master places
    try:
        places_rows = read_csv("master/places_master.csv")
        for row in places_rows:
            city = clean_text(row.get("city")).casefold()
            name = clean_text(row.get("name"))
            if not name or dest_clean not in city:
                continue
            if is_accommodation(name, row.get("type"), row.get("type")):
                continue
            norm = normalize_name(name)
            if norm in seen:
                continue
            seen.add(norm)
            results.append({
                "name": name,
                "city": destination,
                "type": row.get("type", "Attraction"),
                "visit_hours": row.get("visit_hours", ""),
                "rating": row.get("rating", ""),
                "entrance_fee": row.get("entrance_fee", ""),
                "weekly_off": row.get("weekly_off", ""),
                "significance": row.get("significance", ""),
                "best_time": row.get("best_time", ""),
                "source": "Local tourism dataset",
            })
    except Exception as exc:
        print("[DATA] places_master read error:", exc)

    # 2. Master tourist spots
    try:
        spots_rows = read_csv("master/tourist_spots_master.csv")
        for row in spots_rows:
            city = clean_text(row.get("city")).casefold()
            name = clean_text(row.get("name"))
            if not name:
                continue
            if city != dest_clean and dest_clean not in city:
                continue
            if is_accommodation(name, row.get("characteristics"), "Attraction"):
                continue

            lat = safe_float(row.get("latitude"))
            lon = safe_float(row.get("longitude"))
            if lat and lon and dest_coords:
                dist = calculate_haversine_distance(dest_coords[0], dest_coords[1], lat, lon)
                if dist > 40.0:
                    continue

            norm = normalize_name(name)
            if norm in seen:
                continue
            seen.add(norm)

            results.append({
                "name": name,
                "city": destination,
                "lat": lat,
                "lon": lon,
                "type": "Attraction",
                "significance": clean_text(row.get("characteristics")),
                "source": "Local tourism dataset",
            })
    except Exception as exc:
        print("[DATA] tourist_spots_master read error:", exc)

    # 3. Direct city-specific files in Tourist spot folder
    city_file = DATA_DIR / "Tourist spot" / f"Destinations_{dest_clean}.csv"
    if city_file.is_file():
        try:
            with city_file.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    name = clean_text(row.get("Name") or row.get("POI_Name"))
                    if not name:
                        continue
                    if is_accommodation(name, "", "Attraction"):
                        continue
                    lat = safe_float(row.get("Latitude"))
                    lon = safe_float(row.get("Longitude"))
                    if lat and lon and dest_coords:
                        dist = calculate_haversine_distance(dest_coords[0], dest_coords[1], lat, lon)
                        if dist > 40.0:
                            continue
                    norm = normalize_name(name)
                    if norm in seen:
                        continue
                    seen.add(norm)
                    results.append({
                        "name": name,
                        "city": destination,
                        "lat": lat,
                        "lon": lon,
                        "type": "Attraction",
                        "source": "Local tourism dataset",
                    })
        except Exception as exc:
            print("[DATA] city-specific dataset error:", exc)

    return results


def create_smart_itinerary(
    destination: str,
    duration: int,
    destination_places: list[dict],
    live_places: list[dict],
    interests: list[str],
    lunch_preference: str = "both",
) -> list[dict]:
    """
    Create a day-by-day itinerary with:
    - At least 2 morning attractions (parks, beaches, temples, viewpoints, etc.)
    - At least 2 afternoon attractions (museums, shopping, monuments, etc.)
    - At least 2 evening attractions (beaches, viewpoints, sunsets, etc.)
    - 3 breakfast restaurants
    - 3 lunch restaurants
    - 3 dinner restaurants
    - Strict uniqueness: NO place is ever repeated across periods or days
    - Strict validation: places must genuinely belong to destination (distance <= 40 km)
    - Strict exclusion: NO accommodation/hostel/hotel places
    """
    dest_coords = geoapify_coordinates(destination)

    # ============================================================
    # 1. COMBINE AND VALIDATE TOURIST CANDIDATES
    # ============================================================

    candidates = []
    seen = set()

    for raw in list(destination_places or []) + list(live_places or []):
        name = clean_text(raw.get("name"))
        if not name or name.casefold() in ("none", "null", ""):
            continue

        # Reject accommodation
        categories = raw.get("categories", [])
        place_type = raw.get("type", "Attraction")
        if is_accommodation(name, categories, place_type):
            continue

        # Location validation
        lat = safe_float(raw.get("lat") or raw.get("latitude"))
        lon = safe_float(raw.get("lon") or raw.get("longitude"))
        if lat and lon and dest_coords:
            dist = calculate_haversine_distance(dest_coords[0], dest_coords[1], lat, lon)
            if dist > 40.0:
                continue
        else:
            city_val = clean_text(raw.get("city")).casefold()
            if city_val and destination.casefold() not in city_val and city_val not in destination.casefold():
                continue

        norm = normalize_name(name)
        if norm in seen:
            continue
        seen.add(norm)

        item = dict(raw)
        item["name"] = name
        item["type"] = place_type or "Attraction"
        item["lat"] = lat if lat else None
        item["lon"] = lon if lon else None
        item["suitable_periods"] = classify_place_periods(item)
        item["score"] = _place_score(item, interests)

        candidates.append(item)

    # Guarantee minimum candidate pool if needed
    needed_places = duration * 6
    if len(candidates) < needed_places:
        try:
            extra_live = geoapify_place_search(
                destination,
                "tourism.attraction,tourism.sights,leisure.park,entertainment.museum",
                limit=50
            )
            for raw in extra_live:
                name = clean_text(raw.get("name"))
                if not name or is_accommodation(name, raw.get("categories"), "Attraction"):
                    continue
                lat = safe_float(raw.get("lat"))
                lon = safe_float(raw.get("lon"))
                if lat and lon and dest_coords:
                    dist = calculate_haversine_distance(dest_coords[0], dest_coords[1], lat, lon)
                    if dist > 40.0:
                        continue
                norm = normalize_name(name)
                if norm in seen:
                    continue
                seen.add(norm)
                item = dict(raw)
                item["suitable_periods"] = classify_place_periods(item)
                item["score"] = _place_score(item, interests)
                candidates.append(item)
                if len(candidates) >= needed_places:
                    break
        except Exception as exc:
            print("[PLACES] Candidate expansion error:", exc)

    # Sort by interest score and rating
    candidates.sort(key=lambda p: p.get("score", 0), reverse=True)

    # ============================================================
    # 2. CREATE ITINERARY ENSURING ZERO DUPLICATES
    # ============================================================

    used_place_names = set()
    used_restaurant_names = set()
    result = []

    for day_number in range(1, duration + 1):
        day = {
            "day": day_number,
            "title": f"Day {day_number} — {destination}",
            "destination": destination,
            "morning": [],
            "afternoon": [],
            "evening": [],
            "activities": [],
            "breakfast_restaurants": [],
            "lunch_restaurants": [],
            "dinner_restaurants": [],
            "lunch_preference": lunch_preference,
            "source": "AI Voyage Planner + Geoapify",
        }

        # Select at least 2 unique places for each period
        for period in ("morning", "afternoon", "evening"):
            selected = []

            # 1. First priority: unused candidates specifically matching this period
            for place in candidates:
                norm = normalize_name(place["name"])
                if norm in used_place_names:
                    continue
                if period in place.get("suitable_periods", set()):
                    selected.append(place)
                    used_place_names.add(norm)
                    if len(selected) >= 2:
                        break

            # 2. Fallback: unused valid destination candidates to ensure at least 2 places
            if len(selected) < 2:
                for place in candidates:
                    norm = normalize_name(place["name"])
                    if norm in used_place_names:
                        continue
                    selected.append(place)
                    used_place_names.add(norm)
                    if len(selected) >= 2:
                        break

            day[period] = selected
            day["activities"].extend(selected)

        # Restaurant anchors
        breakfast_anchor = (
            day["morning"][0]["name"]
            if day["morning"]
            else destination
        )
        lunch_anchor = (
            day["afternoon"][0]["name"]
            if day["afternoon"]
            else destination
        )
        dinner_anchor = (
            day["evening"][0]["name"]
            if day["evening"]
            else destination
        )

        # 3. Restaurants for each meal
        try:
            day["breakfast_restaurants"] = get_nearby_restaurants(
                place_name=breakfast_anchor,
                destination=destination,
                meal="breakfast",
                lunch_preference=lunch_preference,
                limit=3,
                dest_coords=dest_coords,
                used_names=used_restaurant_names,
            )
        except Exception as exc:
            print(f"[RESTAURANT] Breakfast error on Day {day_number}: {exc}")
            day["breakfast_restaurants"] = []

        try:
            day["lunch_restaurants"] = get_nearby_restaurants(
                place_name=lunch_anchor,
                destination=destination,
                meal="lunch",
                lunch_preference=lunch_preference,
                limit=3,
                dest_coords=dest_coords,
                used_names=used_restaurant_names,
            )
        except Exception as exc:
            print(f"[RESTAURANT] Lunch error on Day {day_number}: {exc}")
            day["lunch_restaurants"] = []

        try:
            day["dinner_restaurants"] = get_nearby_restaurants(
                place_name=dinner_anchor,
                destination=destination,
                meal="dinner",
                lunch_preference=lunch_preference,
                limit=3,
                dest_coords=dest_coords,
                used_names=used_restaurant_names,
            )
        except Exception as exc:
            print(f"[RESTAURANT] Dinner error on Day {day_number}: {exc}")
            day["dinner_restaurants"] = []

        result.append(day)

    return result    


# ============================================================
# TRIP PLANNER
# ============================================================

@app.post("/api/trips/plan")
def create_trip_plan(
    request: TripRequest,
):

    places_dataset = (
        "master/places_master.csv"
    )

    transport_dataset = (
        "processed/transport.csv"
    )

    ensure_data_file(
        places_dataset
    )

    ensure_data_file(
        transport_dataset
    )

    # --------------------------------------------------------
    # TRIP DURATION
    # --------------------------------------------------------

    duration = 3

    if (
        request.start_date
        and request.end_date
    ):

        duration = max(
            1,
            (
                request.end_date
                - request.start_date
            ).days
            + 1,
        )

    # --------------------------------------------------------
    # TRANSPORT DATASET
    # --------------------------------------------------------

    transport_rows = read_csv(
        transport_dataset
    )

    matching_route = next(

        (
            row

            for row in transport_rows

            if row.get(
                "origin",
                ""
            ).casefold()
            == request.origin.casefold()

            and row.get(
                "destination",
                ""
            ).casefold()
            == request.destination.casefold()
        ),

        None,
    )

    # --------------------------------------------------------
    # GEOAPIFY LIVE ROUTE
    # --------------------------------------------------------

    live_distance_km = (
        geoapify_route_distance(
            request.origin,
            request.destination
        )
    )

    geoapify_configured = bool(
        os.getenv(
            "GEOAPIFY_API_KEY"
        )
    )

    if live_distance_km:

        distance_km = (
            live_distance_km
        )

        route_source = (
            "Geoapify live route"
        )

    elif (
        matching_route
        and not geoapify_configured
    ):

        distance_km = safe_int(
            matching_route.get(
                "distance_km"
            )
        )

        route_source = (
            "Local dataset"
        )

    else:

        distance_km = None

        route_source = None

    # --------------------------------------------------------
    # TRANSPORT MODE
    # --------------------------------------------------------

    if live_distance_km:

        transport_mode = (
            "Driving route"
        )

    elif matching_route:

        transport_mode = (
            matching_route.get(
                "mode",
                "Train"
            )
        )

    else:

        transport_mode = (
            "Local public transport"
        )

    # --------------------------------------------------------
    # CARBON
    # --------------------------------------------------------

    if distance_km:

        emissions_kg = round(

            distance_km
            * (
                0.192
                if live_distance_km
                else 0.041
            ),

            1
        )

    else:

        emissions_kg = None

    # ========================================================
    # DATASET PLACES
    # ========================================================

    dest_coords = geoapify_coordinates(request.destination)

    destination_places = get_all_destination_places(
        request.destination,
        dest_coords
    )

    # ========================================================
    # LIVE GEOAPIFY DATA
    # ========================================================

    live_places = (
        get_live_tourist_places(
            request.destination,
            limit=50
        )
    )

    live_hotels = (
        get_live_hotels(
            request.destination
        )
    )

    live_local_shops = (
        get_live_local_shops(
            request.destination
        )
    )

    # ========================================================
    # DEDUPLICATED FRONTEND PLACES (ZERO ACCOMMODATION)
    # ========================================================

    combined_frontend_places = []
    seen_frontend_names = set()
    for p in list(live_places or []) + list(destination_places or []):
        p_name = clean_text(p.get("name"))
        if not p_name or is_accommodation(p_name, p.get("categories", []), p.get("type", "Attraction")):
            continue
        p_lat = safe_float(p.get("lat") or p.get("latitude"))
        p_lon = safe_float(p.get("lon") or p.get("longitude"))
        if p_lat and p_lon and dest_coords:
            if calculate_haversine_distance(dest_coords[0], dest_coords[1], p_lat, p_lon) > 40.0:
                continue
        p_norm = normalize_name(p_name)
        if p_norm in seen_frontend_names:
            continue
        seen_frontend_names.add(p_norm)
        combined_frontend_places.append({
            **p,
            "name": p_name,
            "type": p.get("type") or "Attraction",
            "lat": p_lat,
            "lon": p_lon,
            "source": p.get("source") or "Tourist Spot",
        })

    places_for_frontend = combined_frontend_places

    # ========================================================
    # LOCAL PLACES
    # ========================================================

    local_places = [

        {
            "city":
                place.get(
                    "city",
                    request.destination
                ),

            "name":
                place.get(
                    "name",
                    ""
                ),

            "type":
                place.get(
                    "type",
                    "Attraction"
                ),

            "visit_hours":
                place.get(
                    "visit_hours",
                    ""
                ),

            "rating":
                place.get(
                    "rating",
                    ""
                ),

            "entrance_fee":
                place.get(
                    "entrance_fee",
                    ""
                ),

            "weekly_off":
                place.get(
                    "weekly_off",
                    ""
                ),

            "significance":
                place.get(
                    "significance",
                    ""
                ),

            "best_time":
                place.get(
                    "best_time",
                    ""
                ),

            "source":
                "Local tourism dataset",
        }

        for place in destination_places
    ]

    # ========================================================
    # HOTEL FALLBACK
    # ========================================================

    hotel_dataset = (
        "master/hotels_master.csv"
    )

    hotel_suggestions = []

    if (
        DATA_DIR / hotel_dataset
    ).is_file():

        hotel_rows = read_csv(
            hotel_dataset
        )

        hotel_suggestions = [

            row

            for row in hotel_rows

            if request.destination.casefold()
            in (
                row.get(
                    "place",
                    ""
                ).casefold()
            )
        ][:15]

    # ========================================================
    # FRONTEND HOTEL DATA
    # ========================================================

    hotels_for_frontend = (

        live_hotels

        if live_hotels

        else [

            {
                **hotel,
                "source":
                    "Local hotel dataset"
            }

            for hotel in hotel_suggestions
        ]
    )

    # ========================================================
    # SMART ITINERARY
    # ========================================================

    itinerary = create_smart_itinerary(
        destination=request.destination,
        duration=duration,
        destination_places=destination_places,
        live_places=live_places,
        interests=request.interests,
        lunch_preference=request.lunch_preference,
    )

    # ========================================================
    # WEATHER
    # ========================================================

    weather_info = get_weather(
        request.destination
    )

    # ========================================================
    # SUSTAINABILITY
    # ========================================================

    sustainability = (
        calculate_sustainability_score(

            distance_km=
                distance_km,

            emissions_kg=
                emissions_kg,

            travelers=
                request.travelers,

            transport_mode=
                transport_mode,

            local_places_count=
                len(
                    places_for_frontend
                ),
        )
    )

    # ========================================================
    # ROUTE STATUS
    # ========================================================

    if live_distance_km:

        route_status = (
            "Live route from Geoapify"
        )

    elif (
        geoapify_configured
        and not live_distance_km
    ):

        route_status = (
            "Geoapify route unavailable"
        )

    elif matching_route:

        route_status = (
            "Route available in local dataset"
        )

    else:

        route_status = (
            "Route unavailable"
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "status":
            "success",

        "trip": {

            "origin":
                request.origin,

            "destination":
                request.destination,

            "start_date":
                (
                    request.start_date.isoformat()
                    if request.start_date
                    else None
                ),

            "end_date":
                (
                    request.end_date.isoformat()
                    if request.end_date
                    else None
                ),

            "travelers":
                request.travelers,

            "duration_days":
                duration,

            "budget":
                request.budget,

            "interests":
                request.interests,

            "lunch_preference":
                request.lunch_preference,
        },

        # ----------------------------------------------------
        # ROUTE
        # ----------------------------------------------------

        "route": {

            "distance_km":
                distance_km,

            "source":
                route_source,

            "status":
                route_status,

            "origin":
                request.origin,

            "destination":
                request.destination,
        },

        # ----------------------------------------------------
        # WEATHER
        # ----------------------------------------------------

        "weather":
            weather_info,

        # ----------------------------------------------------
        # PLACES
        # ----------------------------------------------------

        "places":
            places_for_frontend,

        "live_places":
            live_places,

        "local_places":
            local_places,

        # ----------------------------------------------------
        # HOTELS
        # ----------------------------------------------------

        "hotels":
            hotels_for_frontend,

        "live_hotels":
            live_hotels,

        "hotel_suggestions":
            hotel_suggestions,

        # ----------------------------------------------------
        # LOCAL SHOPS
        # ----------------------------------------------------

        "local_shops":
            live_local_shops,

        # ----------------------------------------------------
        # ITINERARY
        # ----------------------------------------------------

        "itinerary":
            itinerary,

        # ----------------------------------------------------
        # TRANSPORT
        # ----------------------------------------------------

        "transport": {

            "selected_mode":
                transport_mode,

            "recommended_mode":
                transport_mode,

            "distance_km":
                distance_km,

            "route_source":
                route_source,
        },

        # ----------------------------------------------------
        # SUSTAINABILITY
        # ----------------------------------------------------

        "sustainability": {

            **sustainability,

            "estimated_emissions_kg":
                emissions_kg,
        },
    }


# ============================================================
# FIND REPLANNING ALTERNATIVES
# ============================================================

def find_replanning_alternatives(
    destination,
    interests=None,
    limit=8,
):

    places_file = (
        DATA_DIR
        / "master"
        / "places_master.csv"
    )

    if not places_file.exists():
        return []

    interests = interests or []

    destination_text = (
        str(destination)
        .strip()
        .lower()
    )

    results = []

    try:

        rows = read_csv(
            "master/places_master.csv"
        )

        destination_rows = []

        for row in rows:

            city = str(
                row.get(
                    "city",
                    ""
                )
            ).lower()

            if (
                destination_text
                in city
            ):

                destination_rows.append(
                    row
                )

        scored = []

        for row in destination_rows:

            row_text = " ".join(
                str(value or "")
                for value in row.values()
            ).lower()

            score = 0

            for interest in interests:

                if (
                    str(interest).lower()
                    in row_text
                ):

                    score += 2

            scored.append(
                (
                    score,
                    row
                )
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        for _, row in scored:

            name = row.get(
                "name",
                ""
            )

            if not name:
                continue

            results.append(

                {
                    "name":
                        name,

                    "type":
                        row.get(
                            "type",
                            "Attraction"
                        ),

                    "rating":
                        row.get(
                            "rating",
                            ""
                        ),

                    "best_time":
                        row.get(
                            "best_time",
                            ""
                        ),

                    "source":
                        "AI Voyage Planner dataset",
                }
            )

            if len(results) >= limit:
                break

        return results

    except Exception as exc:

        print(
            "Replanning dataset error:",
            exc
        )

        return []


# ============================================================
# DYNAMIC AI REPLANNING
# ============================================================

@app.post("/api/trips/replan")
def replan_trip(
    request: ReplanRequest
):

    event_type = (
        request.event_type
        .lower()
        .strip()
    )

    candidates = (
        find_replanning_alternatives(
            destination=
                request.destination,

            interests=
                request.interests,

            limit=8,
        )
    )

    if not candidates:

        candidates = [

            {
                "name":
                    "Alternative Local Attraction",

                "type":
                    "Local Experience",

                "rating":
                    "",

                "best_time":
                    "",

                "source":
                    "Fallback",
            }
        ]

    # --------------------------------------------------------
    # Approved activities
    # --------------------------------------------------------

    approved = {

        str(activity)
        .strip()
        .lower()

        for activity
        in request.approved_activities

        if str(activity).strip()
    }

    updated_itinerary = []

    replaced_count = 0

    # --------------------------------------------------------
    # Process itinerary
    # --------------------------------------------------------

    for item in request.itinerary:

        original_item = dict(
            item
        )

        day = original_item.get(
            "day"
        )

        title = original_item.get(
            "title",
            ""
        )

        description = (
            original_item.get(
                "description",
                ""
            )
        )

        combined_text = (
            f"{title} {description}"
            .lower()
        )

        # ----------------------------------------------------
        # Preserve approved activity
        # ----------------------------------------------------

        is_approved = any(

            approved_name
            in combined_text

            for approved_name
            in approved
        )

        if is_approved:

            original_item[
                "status"
            ] = "Preserved"

            original_item[
                "adaptation_reason"
            ] = (
                "Preserved because this "
                "activity was already approved."
            )

            updated_itinerary.append(
                original_item
            )

            continue

        # ----------------------------------------------------
        # Replace affected activity
        # ----------------------------------------------------

        if (
            replaced_count
            < len(candidates)
        ):

            replacement = candidates[
                replaced_count
            ]

            updated_item = {

                "day":
                    day,

                "title":
                    (
                        f"Day {day} — "
                        f"{replacement['name']}"
                    ),

                "description":
                    (
                        f"{replacement['name']} "
                        f"({replacement['type']}). "
                        f"Selected from the "
                        f"AI Voyage Planner "
                        f"destination dataset."
                    ),

                "rating":
                    replacement.get(
                        "rating",
                        ""
                    ),

                "best_time":
                    replacement.get(
                        "best_time",
                        ""
                    ),

                "source":
                    replacement.get(
                        "source",
                        "AI Voyage Planner dataset"
                    ),

                "status":
                    "AI Replanned",

                "original_activity":
                    title,

                "adaptation_reason":
                    (
                        request.event_description
                        or
                        f"Adapted because of "
                        f"{event_type}."
                    ),
            }

            updated_itinerary.append(
                updated_item
            )

            replaced_count += 1

        else:

            # ------------------------------------------------
            # Preserve activity when no replacement is needed
            # ------------------------------------------------

            original_item["status"] = "Unchanged"

            original_item["adaptation_reason"] = (
                "No suitable replacement was required."
            )

            updated_itinerary.append(
                original_item
            )

    # --------------------------------------------------------
    # Replanning summary
    # --------------------------------------------------------

    preserved_count = sum(
        1
        for item in updated_itinerary
        if item.get("status") == "Preserved"
    )

    unchanged_count = sum(
        1
        for item in updated_itinerary
        if item.get("status") == "Unchanged"
    )

    return {

        "status":
            "success",

        "event": {

            "type":
                request.event_type,

            "description":
                request.event_description,
        },

        "destination":
            request.destination,

        "preserved_approved_activities":
            preserved_count,

        "replaced_activities":
            replaced_count,

        "unchanged_activities":
            unchanged_count,

        "total_activities":
            len(updated_itinerary),

        "itinerary":
            updated_itinerary,

        "alternatives":
            candidates,

        "replanning_strategy":
            (
                "Approved activities were preserved "
                "where possible, while affected activities "
                "were replaced with suitable alternatives "
                "from the destination dataset."
            ),
    }


# ============================================================
# STARTUP
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )