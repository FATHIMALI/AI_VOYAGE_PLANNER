import math
import pandas as pd
from geopy.geocoders import Nominatim


TRANSPORT_FILE = "data/processed/transport.csv"


def load_transport_data():
    try:
        return pd.read_csv(TRANSPORT_FILE)
    except Exception:
        return pd.DataFrame()


def get_dataset_distance(source, destination):

    df = load_transport_data()

    if df.empty:
        return None

    source = source.strip().lower()
    destination = destination.strip().lower()

    for _, row in df.iterrows():

        origin = str(row["origin"]).strip().lower()
        dest = str(row["destination"]).strip().lower()

        if origin == source and dest == destination:
            return float(row["distance_km"]), "Dataset"

        if origin == destination and dest == source:
            return float(row["distance_km"]), "Dataset"

    return None


def geocode_place(place):

    geolocator = Nominatim(user_agent="ai_sustainable_tourism_planner")

    try:
        location = geolocator.geocode(f"{place}, India", timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print("Geocoding error:", e)

    return None


def haversine_distance(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_distance(source, destination):

    dataset_result = get_dataset_distance(source, destination)

    if dataset_result:
        distance, source_type = dataset_result
        return {
            "distance_km": round(distance, 2),
            "source": source_type,
            "estimated": False
        }

    source_coords = geocode_place(source)
    destination_coords = geocode_place(destination)

    if not source_coords or not destination_coords:
        return None

    distance = haversine_distance(
        source_coords[0], source_coords[1],
        destination_coords[0], destination_coords[1]
    )

    estimated_route_distance = distance * 1.20

    return {
        "distance_km": round(estimated_route_distance, 2),
        "source": "Geocoding + Haversine",
        "estimated": True
    }