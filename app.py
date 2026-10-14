import os
import re
import pickle
import hashlib

import streamlit as st
import requests
import numpy as np
import pandas as pd
import faiss
import ollama
from dotenv import load_dotenv

from distance import get_distance
from carbon import compare_transport, get_best_option


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Voyage Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

VECTOR_DB_DIR = os.path.join(
    BASE_DIR,
    "vector_db"
)

INDEX_PATH = os.path.join(
    VECTOR_DB_DIR,
    "tourism.index"
)

METADATA_PATH = os.path.join(
    VECTOR_DB_DIR,
    "metadata.pkl"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

GEOAPIFY_API_KEY = os.getenv(
    "GEOAPIFY_API_KEY"
)


# ============================================================
# MODELS
# ============================================================

LLM_MODEL = "llama3"
EMBED_MODEL = "nomic-embed-text"


# ============================================================
# SUSTAINABILITY HELPERS
# ============================================================

def calculate_sustainability_score(travel_mode, carbon):

    scores = {
        "Walking": 100,
        "Bicycle": 100,
        "Train": 90,
        "Public Transport": 85,
        "Bus": 75,
        "Bike": 65,
        "Car": 50,
        "Flight": 30
    }

    score = scores.get(travel_mode, 50)

    if carbon > 100:
        score -= 15
    elif carbon > 60:
        score -= 10
    elif carbon > 30:
        score -= 5

    return max(0, min(100, score))


def get_sustainability_level(carbon):

    if carbon <= 10:
        return "Very Low"
    if carbon <= 30:
        return "Low"
    if carbon <= 60:
        return "Moderate"
    if carbon <= 100:
        return "High"
    return "Very High"


def get_green_recommendations(travel_mode):

    recommendations = []

    if travel_mode in ["Car", "Bike"]:
        recommendations.append(
            "🚆 Consider trains or public transport for longer journeys."
        )

    if travel_mode == "Flight":
        recommendations.append(
            "🚆 Consider rail transport when a practical alternative exists."
        )

    recommendations.extend([
        "🚶 Walk for short-distance sightseeing.",
        "💧 Carry a reusable water bottle.",
        "♻️ Avoid single-use plastic.",
        "🏡 Prefer locally owned businesses.",
        "🌿 Respect natural areas and local communities."
    ])

    return recommendations


def create_budget(budget):

    return {
        "Accommodation": round(budget * 0.30),
        "Transportation": round(budget * 0.25),
        "Food": round(budget * 0.20),
        "Activities": round(budget * 0.15),
        "Emergency": round(budget * 0.10)
    }


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    :root {
        --navy: #10264d;
        --blue: #1e4b8f;
        --green: #1f7a4d;
        --green-dark: #14532d;
        --bg: #eef2f7;
    }

    /* ---------------- FORCE BLACK TEXT ---------------- */

    .stApp,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp div,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp li,
    .navbar-logo,
    .navbar-links,
    .hero-title,
    .hero-subtitle,
    .hero-tagline,
    .card-title,
    .field-label,
    .feature-title,
    .feature-desc,
    .main-title,
    .subtitle,
    .section-title {
        color: #000000 !important;
    }

    /* Keep button text readable (white on colored buttons) */

    .stButton > button,
    button[kind="primary"],
    [data-testid="stPills"] button[aria-pressed="true"] {
        color: #ffffff !important;
    }

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: var(--bg);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    div.block-container {
        padding-top: 1.2rem;
        max-width: 1200px;
    }

    /* ---------------- NAVBAR ---------------- */

    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        padding: 14px 28px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(16, 38, 77, 0.06);
        margin-bottom: 18px;
    }

    .navbar-logo {
        font-size: 20px;
        font-weight: 800;
        color: var(--navy);
    }

    .navbar-links {
        display: flex;
        gap: 26px;
        font-weight: 600;
        color: #445;
        font-size: 15px;
    }

    .navbar-links .nav-active {
        color: var(--blue);
        border-bottom: 2px solid var(--blue);
        padding-bottom: 4px;
    }

    /* ---------------- HERO ---------------- */

    .hero {
        text-align: center;
        padding: 90px 20px 110px 20px;
        border-radius: 20px;
        margin-bottom: -60px;
        position: relative;
        overflow: hidden;
        background-image:
            linear-gradient(180deg, rgba(8, 20, 45, 0.55) 0%, rgba(8, 20, 45, 0.72) 100%),
            url('https://picsum.photos/seed/aivoyage-hero/1600/700');
        background-size: cover;
        background-position: center;
    }

    .hero .hero-badge,
    .hero div.hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.35);
        color: #ffffff !important;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 6px 16px;
        border-radius: 999px;
        margin-bottom: 16px;
        backdrop-filter: blur(4px);
    }

    .hero .hero-title,
    .hero div.hero-title {
        font-size: 50px;
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 10px;
        text-shadow: 0 2px 18px rgba(0, 0, 0, 0.35);
    }

    .hero .hero-subtitle,
    .hero div.hero-subtitle {
        font-size: 20px;
        font-weight: 600;
        color: #eef4ff !important;
        margin-bottom: 6px;
    }

    .hero .hero-tagline,
    .hero div.hero-tagline {
        font-size: 15px;
        color: #d7e2f5 !important;
    }

    /* ---------------- TRIP PREFERENCES CARD ---------------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 12px 30px rgba(16, 38, 77, 0.12);
        padding: 6px 10px;
        position: relative;
        z-index: 2;
    }

    .card-title {
        font-size: 24px;
        font-weight: 700;
        color: var(--navy);
        margin: 6px 0 18px 0;
    }

    .field-label {
        font-weight: 600;
        color: var(--navy);
        font-size: 15px;
        margin-bottom: 4px;
    }

    /* text / number inputs */

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        border-radius: 10px !important;
        border: 1px solid #dde3ec !important;
        padding: 10px 12px !important;
        background: #fbfcfe !important;
        color: #000000 !important;
    }

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder {
        color: #000000 !important;
        opacity: 1 !important;
    }

    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSelectbox"] label {
        font-weight: 600 !important;
        color: var(--navy) !important;
    }

    [data-testid="stSelectbox"] > div > div {
        border-radius: 10px !important;
        border: 1px solid #dde3ec !important;
        background: #fbfcfe !important;
    }

    [data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    [data-testid="stSelectbox"] input::placeholder {
        color: #000000 !important;
        opacity: 1 !important;
    }

    ul[data-testid="stSelectboxVirtualDropdown"] li {
        color: #000000 !important;
    }

    /* pills (interests) */

    [data-testid="stPills"] button {
        border-radius: 999px !important;
        border: 1px solid #dbe6de !important;
        background: #eaf6ee !important;
        color: #1f5c38 !important;
        font-weight: 600 !important;
    }

    [data-testid="stPills"] button[aria-pressed="true"] {
        background: var(--green) !important;
        color: #ffffff !important;
        border-color: var(--green) !important;
    }

    /* primary buttons */

    .stButton > button, button[kind="primary"] {
        background: var(--green) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 12px 18px !important;
    }

    .stButton > button:hover {
        background: var(--green-dark) !important;
    }

    /* ---------------- FEATURE ROW ---------------- */

    .feature-item {
        text-align: center;
        padding: 10px 8px;
    }

    .feature-icon {
        font-size: 26px;
        width: 58px;
        height: 58px;
        line-height: 58px;
        border-radius: 50%;
        background: #eef3fb;
        margin: 0 auto 10px auto;
    }

    .feature-title {
        font-weight: 700;
        color: var(--navy);
        font-size: 15px;
        margin-bottom: 6px;
    }

    .feature-desc {
        font-size: 13px;
        color: #64748b;
        line-height: 1.4;
    }

    /* ---------------- GENERAL SECTIONS ---------------- */

    .main-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        color: var(--navy);
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #445;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 27px;
        font-weight: 700;
        color: var(--navy);
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .place-card {
        padding: 0;
        border-radius: 16px;
        border: 1px solid #e5e9f0;
        margin-bottom: 18px;
        background-color: #ffffff;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(16, 38, 77, 0.08);
    }

    .place-card-inner {
        padding: 16px 18px 18px 18px;
    }

    .place-card-img {
        width: 100%;
        height: 160px;
        object-fit: cover;
        display: block;
    }

    .place-badge {
        display: inline-block;
        background: #eaf6ee;
        color: #1f5c38 !important;
        font-size: 12px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 6px;
    }

    .selected-box {
        padding: 15px;
        border-radius: 10px;
        border: 2px solid var(--green);
        margin-bottom: 10px;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f4f6f8;
        margin-top: 10px;
    }

    /* ---------------- FOOTER ---------------- */

    .app-footer {
        background: linear-gradient(135deg, var(--green-dark) 0%, #1f7a4d 100%);
        color: #eafaf0;
        padding: 26px 30px;
        border-radius: 18px;
        text-align: center;
        margin-top: 40px;
    }

    .app-footer .footer-title {
        font-size: 19px;
        font-weight: 800;
        margin-bottom: 4px;
        color: #ffffff;
    }

    .app-footer .footer-sub {
        font-size: 13px;
        color: #d7f0e0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NAVBAR
# ============================================================

st.markdown(
    """
    <div class="navbar">
        <div class="navbar-logo">🧭 AI Voyage Planner</div>
                <div class="navbar-links">
            <span class="nav-active">🏠 Home</span>
            <span>ℹ️ About</span>
            <span>🍃 Sustainability</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">✨ AI-Powered Sustainable Travel</div>
        <div class="hero-title">✈️ AI Voyage Planner</div>
        <div class="hero-subtitle">
            Generative AI-powered Personalized &amp; Sustainable Tourism Planner
        </div>
        <div class="hero-tagline">
            Discover amazing places, plan your perfect trip, and travel responsibly.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TRIP PREFERENCES CARD (main page)
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="card-title">🧭 Trip Preferences</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        source = st.text_input(
            "📍 Source City",
            value="Chennai",
            placeholder="e.g. Chennai"
        )

    with col2:
        destination = st.text_input(
            "📍 Destination",
            value="Coorg",
            placeholder="e.g. Coorg"
        )

    with col3:
        budget = st.number_input(
            "💰 Budget (₹)",
            min_value=1000,
            max_value=1000000,
            value=15000,
            step=1000
        )

    with col4:
        days = st.number_input(
            "📅 Number of Days",
            min_value=1,
            max_value=30,
            value=3,
            step=1
        )

    col_a, col_b = st.columns([2, 1])

    with col_a:

        st.markdown(
            '<div class="field-label">⭐ Interests</div>',
            unsafe_allow_html=True
        )

        interest_options = [
            "🌿 Nature",
            "🍴 Food",
            "🏰 Heritage",
            "⛰️ Adventure",
            "🏛️ Culture",
            "🛍️ Shopping",
            "🐾 Wildlife",
            "🧘 Relaxation"
        ]

        interests_selected = st.pills(
            "Interests",
            interest_options,
            selection_mode="multi",
            default=["🌿 Nature", "🍴 Food"],
            label_visibility="collapsed",
            key="interests_pills"
        )

        interests = (
            [item.split(" ", 1)[1] for item in interests_selected]
            if interests_selected
            else []
        )

    with col_b:
        travel_preference = st.selectbox(
            "🍃 Travel Preference",
            [
                "Sustainable",
                "Budget Friendly",
                "Comfort",
                "Adventure",
                "Luxury"
            ]
        )

        travel_mode = st.selectbox(
            "🚗 Preferred Transport",
            [
                "Public Transport",
                "Train",
                "Bus",
                "Car",
                "Bike",
                "Flight",
                "Walking",
                "Bicycle"
            ]
        )

    st.markdown(
        "<div style='height:6px'></div>",
        unsafe_allow_html=True
    )

    explore_button = st.button(
        "🔍 Explore Destination",
        use_container_width=True,
        type="primary"
    )

# ============================================================
# FEATURE HIGHLIGHTS
# ============================================================

st.markdown(
    "<div style='height:26px'></div>",
    unsafe_allow_html=True
)

FEATURES = [
    ("✨", "Personalized Plans", "Tailored to your interests, budget and travel style"),
    ("🌱", "Sustainable Travel", "Support eco-friendly and local tourism"),
    ("🧠", "Powered by AI", "Smart recommendations for the best experience"),
    ("📍", "Real-time Data", "Live info from Geoapify API for accurate results"),
    ("❤️", "Unforgettable Experiences", "Explore, eat, stay and create memories"),
]

feature_cols = st.columns(5)

for feature_col, (f_icon, f_title, f_desc) in zip(feature_cols, FEATURES):

    with feature_col:

        st.markdown(
            f"""
            <div class="feature-item">
                <div class="feature-icon">{f_icon}</div>
                <div class="feature-title">{f_title}</div>
                <div class="feature-desc">{f_desc}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "selected_spots": [],
    "selected_hotels": [],
    "selected_restaurants": [],
    "generated_itinerary": "",
    "rag_results": [],
    "explored_destination": "",
    "tourist_places": [],
    "hotel_places": [],
    "restaurant_places": [],
    "details_place": None
}

for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# API KEY CHECK
# ============================================================

if not GEOAPIFY_API_KEY:

    st.error(
        "❌ Geoapify API key was not found."
    )

    st.info(
        "Create a .env file in the same folder "
        "as app.py and add:\n\n"
        "GEOAPIFY_API_KEY=YOUR_API_KEY"
    )


# ============================================================
# RAG DATABASE
# ============================================================

@st.cache_resource
def load_rag_database():

    if not os.path.exists(INDEX_PATH):

        return None, []

    if not os.path.exists(METADATA_PATH):

        return None, []

    try:

        index = faiss.read_index(
            INDEX_PATH
        )

        with open(
            METADATA_PATH,
            "rb"
        ) as f:

            metadata = pickle.load(f)

        return index, metadata

    except Exception as e:

        st.warning(
            f"RAG database could not be loaded: {e}"
        )

        return None, []


index, metadata = load_rag_database()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if not text:

        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# GEOAPIFY GEOCODING API
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def geoapify_geocode(destination):

    if not GEOAPIFY_API_KEY:

        return None

    destination = destination.strip()

    if not destination:

        return None

    url = (
        "https://api.geoapify.com/"
        "v1/geocode/search"
    )

    params = {
        "text": f"{destination}, India",
        "filter": "countrycode:in",
        "limit": 1,
        "format": "json",
        "apiKey": GEOAPIFY_API_KEY
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        if response.status_code != 200:

            print(
                "Geoapify Geocoding Error:",
                response.status_code,
                response.text[:500]
            )

            return None

        data = response.json()

        results = data.get(
            "results",
            []
        )

        if not results:

            return None

        result = results[0]

        return {
            "lat": float(
                result["lat"]
            ),
            "lon": float(
                result["lon"]
            ),
            "formatted": result.get(
                "formatted",
                destination
            ),
            "place_id": result.get(
                "place_id"
            )
        }

    except Exception as e:

        print(
            "Geoapify Geocoding Exception:",
            e
        )

        return None


# ============================================================
# GEOAPIFY PLACE SEARCH
# ============================================================

@st.cache_data(
    ttl=1800,
    show_spinner=False
)
def geoapify_places(
    destination,
    categories,
    limit=10
):

    if not GEOAPIFY_API_KEY:

        return []

    location = geoapify_geocode(
        destination
    )

    if not location:

        return []

    lat = location["lat"]
    lon = location["lon"]

    url = (
        "https://api.geoapify.com/"
        "v2/places"
    )

    params = {
        "categories": categories,

        "filter": (
            f"circle:{lon},{lat},30000"
        ),

        "bias": (
            f"proximity:{lon},{lat}"
        ),

        "limit": limit,

        "lang": "en",

        "apiKey": GEOAPIFY_API_KEY
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        if response.status_code != 200:

            print(
                "Geoapify Places Error:",
                response.status_code,
                response.text[:500]
            )

            return []

        data = response.json()

        features = data.get(
            "features",
            []
        )

        places = []

        seen_names = set()

        for feature in features:

            properties = feature.get(
                "properties",
                {}
            )

            name = (
                properties.get("name")
                or properties.get(
                    "address_line1"
                )
            )

            if not name:

                continue

            name = str(
                name
            ).strip()

            normalized_name = normalize_text(
                name
            )

            if not normalized_name:

                continue

            if normalized_name in seen_names:

                continue

            seen_names.add(
                            normalized_name
            )

            # ------------------------------------------------
            # COORDINATES
            # ------------------------------------------------

            place_lat = properties.get(
                "lat"
            )

            place_lon = properties.get(
                "lon"
            )

            if (
                place_lat is None
                or place_lon is None
            ):

                geometry = feature.get(
                    "geometry",
                    {}
                )

                coordinates = geometry.get(
                    "coordinates",
                    []
                )

                if len(coordinates) >= 2:

                    place_lon = coordinates[0]
                    place_lat = coordinates[1]

            if (
                place_lat is None
                or place_lon is None
            ):

                continue

            # ------------------------------------------------
            # CATEGORIES
            # ------------------------------------------------

            place_categories = (
                properties.get(
                    "categories",
                    []
                )
            )

            if isinstance(
                place_categories,
                list
            ):

                place_type = (
                    place_categories[0]
                    if place_categories
                    else ""
                )

            else:

                place_type = str(
                    place_categories
                )

            # ------------------------------------------------
            # ADDRESS
            # ------------------------------------------------

            address = (
                properties.get(
                    "formatted"
                )
                or ""
            )

            # ------------------------------------------------
            # CONTACT
            # ------------------------------------------------

            contact = properties.get(
                "contact",
                {}
            )

            if not isinstance(
                contact,
                dict
            ):

                contact = {}

            website = (
                properties.get(
                    "website"
                )
                or contact.get(
                    "website"
                )
                or ""
            )

            phone = (
                properties.get(
                    "phone"
                )
                or contact.get(
                    "phone"
                )
                or ""
            )

            opening_hours = (
                properties.get(
                    "opening_hours"
                )
                or ""
            )

            # ------------------------------------------------
            # CUISINE
            # ------------------------------------------------

            cuisine = (
                properties.get(
                    "catering.cuisine"
                )
                or properties.get(
                    "cuisine"
                )
                or ""
            )

            places.append(
                {
                    "name": name,
                    "lat": float(place_lat),
                    "lon": float(place_lon),
                    "address": address,
                    "type": place_type,
                    "website": website,
                    "phone": phone,
                    "opening_hours": opening_hours,
                    "cuisine": cuisine,
                    "category": categories,
                    "place_id": properties.get(
                        "place_id"
                    )
                }
            )

            if len(places) >= limit:

                break

        return places

    except Exception as e:

        print(
            "Geoapify Places Exception:",
            e
        )

        return []


# ============================================================
# TOURIST SPOTS
# ============================================================

def get_tourist_spots(
    destination
):

    return geoapify_places(
        destination,

        (
            "tourism.attraction,"
            "tourism.sights,"
            "entertainment.museum,"
            "leisure.park"
        ),

        limit=10
    )


# ============================================================
# HOTELS
# ============================================================

def get_hotels(
    destination
):

    return geoapify_places(
        destination,

        "accommodation",

        limit=10
    )


# ============================================================
# RESTAURANTS
# ============================================================

def get_restaurants(
    destination
):

    return geoapify_places(
        destination,

        "catering.restaurant",

        limit=10
    )


# ============================================================
# OLLAMA EMBEDDING
# ============================================================

def create_embedding(text):

    try:

        response = ollama.embeddings(
            model=EMBED_MODEL,
            prompt=text
        )

        embedding = response[
            "embedding"
        ]

        return np.array(
            embedding,
            dtype="float32"
        )

    except Exception as e:

        print(
            f"Embedding error: {e}"
        )

        return None


# ============================================================
# DESTINATION MATCH
# ============================================================

def destination_match(
    text,
    destination
):

    text_normalized = normalize_text(
        text
    )

    destination_normalized = normalize_text(
        destination
    )

    if not text_normalized:

        return False

    if not destination_normalized:

        return False

    # Exact match
    if destination_normalized in text_normalized:

        return True

    destination_words = [
        word
        for word in destination_normalized.split()
        if len(word) >= 3
    ]

    if not destination_words:

        return False

    text_words = set(
        text_normalized.split()
    )

    matches = sum(
        1
        for word in destination_words
        if word in text_words
    )

    return matches >= max(
        1,
        len(destination_words) // 2
    )


# ============================================================
# METADATA TO TEXT
# ============================================================

def metadata_to_text(item):

    if isinstance(
        item,
        str
    ):

        return item

    if isinstance(
        item,
        dict
    ):

        values = []

        for key, value in item.items():

            if value is not None:

                values.append(
                    f"{key}: {value}"
                )

        return " ".join(
            values
        )

    return str(item)


# ============================================================
# DESTINATION-FOCUSED RAG
# ============================================================

@st.cache_data(
    ttl=1800,
    show_spinner=False
)
def retrieve_information(
    destination,
    interests,
    top_k=8
):

    if index is None:

        return []

    query = (
        f"Tourism destination: {destination}. "
        f"Tourist attractions, hotels, restaurants, "
        f"transportation and sustainable tourism "
        f"specifically for {destination}. "
        f"Interests: {', '.join(interests)}."
    )

    embedding = create_embedding(
        query
    )

    if embedding is None:

        return []

    embedding = embedding.reshape(
        1,
        -1
    )

    try:

        distances, indices = index.search(
            embedding,
            min(
                top_k * 3,
                index.ntotal
            )
        )

    except Exception as e:

        print(
            f"FAISS search error: {e}"
        )

        return []

    results = []

    for idx in indices[0]:

        if idx < 0:

            continue

        if idx >= len(metadata):

            continue

        item = metadata[idx]

        text = metadata_to_text(
            item
        )

        if destination_match(
            text,
            destination
        ):

            results.append(
                {
                    "text": text,
                    "metadata": item
                }
            )

        if len(results) >= top_k:

            break

    return results


# ============================================================
# BUILD RAG CONTEXT
# ============================================================

def build_rag_context(
    rag_results
):

    if not rag_results:

        return (
            "No destination-specific RAG "
            "information was found."
        )

    context_parts = []

    for i, result in enumerate(
        rag_results,
        start=1
    ):

        context_parts.append(
            f"RAG SOURCE {i}:\n"
            f"{result['text']}"
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# PLACE DESCRIPTION
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def generate_place_description(
    name,
    category,
    place_type,
    address,
    cuisine
):

    prompt = f"""
You are a tourism information assistant.

Explain this place briefly.

Place: {name}
Category: {category}
Type: {place_type}
Address: {address}
Cuisine: {cuisine}

Rules:
- Do not invent facts.
- Do not invent prices.
- Do not claim current availability.
- Do not create fake contact details.
- Do not claim opening hours unless supplied.
- Keep the answer concise.
- Explain why a tourist might visit this place.
"""

    try:

        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response[
            "message"
        ]["content"]

    except Exception as e:

        return (
            "Description unavailable: "
            f"{e}"
        )


# ============================================================
# ITINERARY GENERATION
# ============================================================

def generate_itinerary(
    source,
    destination,
    budget,
    days,
    interests,
    travel_preference,
    selected_spots,
    selected_hotel,
    selected_restaurants,
    rag_context
):

    spots_text = "\n".join(
        [
            f"- {p['name']} "
            f"({p.get('type', 'tourist attraction')})"
            for p in selected_spots
        ]
    )

    if not spots_text:

        spots_text = (
            "None selected."
        )

    if selected_hotel:

        hotel_text = (
            f"{selected_hotel['name']} "
            f"({selected_hotel.get('type', 'hotel')})"
        )

    else:

        hotel_text = (
            "None selected."
        )

    restaurants_text = "\n".join(
        [
            f"- {p['name']} "
            f"({p.get('cuisine') or 'restaurant'})"
            for p in selected_restaurants
        ]
    )

    if not restaurants_text:

        restaurants_text = (
            "None selected."
        )

    prompt = f"""
You are the AI engine of an
AI Sustainable Tourism Planner.

Create a realistic personalized
tourism itinerary.

================================================
TRIP INFORMATION
================================================

Source City: {source}
Destination: {destination}
Budget: ₹{budget}
Number of Days: {days}
Interests: {', '.join(interests)}
Travel Preference: {travel_preference}

================================================
VERIFIED TOURIST SPOTS
================================================

{spots_text}

================================================
VERIFIED HOTEL
================================================

{hotel_text}

================================================
VERIFIED RESTAURANTS
================================================

{restaurants_text}

================================================
DESTINATION-SPECIFIC RAG
================================================

{rag_context}

================================================
STRICT GROUNDING RULES
================================================

1. The destination is ONLY:
   {destination}

2. NEVER recommend places from another
   city, state or destination.

3. VERIFIED TOURIST SPOTS are places
   returned by the Geoapify place-discovery
   API and selected by the user.

4. VERIFIED HOTEL is the hotel returned
   by Geoapify and selected by the user.

5. VERIFIED RESTAURANTS are restaurants
   returned by Geoapify and selected by
   the user.

6. If VERIFIED HOTEL is "None selected",
   DO NOT invent a hotel name.

7. If VERIFIED RESTAURANTS is "None selected",
   DO NOT invent restaurant names.

8. If VERIFIED TOURIST SPOTS is
   "None selected", you may suggest
   general activities, but DO NOT invent
   exact business/place names.

9. RAG information may only be used if
   it clearly belongs to {destination}.

10. Never use a hotel, restaurant or attraction
    from another destination.

11. Do not claim live availability.

12. Do not invent exact hotel prices.

13. Do not invent exact restaurant prices.

14. Do not invent exact ticket prices.

15. Keep the estimated trip cost within
    ₹{budget}.

16. Include sustainable tourism practices.

17. Prefer walking, public transport,
    shared transport and local businesses
    where practical.

18. Use the user's selected places whenever
    they are available.

================================================
OUTPUT FORMAT
================================================

# 🌍 Trip Overview

Destination:
Duration:
Budget:
Interests:
Travel Preference:

# 📍 Selected Places

Tourist Spots:
Hotel:
Restaurants:

# 🗓️ Day-by-Day Itinerary

## Day 1

Morning:
Afternoon:
Evening:
Meals:
Accommodation:

Continue for all {days} days.

# 💰 Estimated Budget Allocation

Accommodation:
Food:
Local Transport:
Activities:
Miscellaneous:
Total:

# 🌱 Sustainable Tourism Recommendations

- Recommendation 1
- Recommendation 2
- Recommendation 3

# ⭐ Why This Itinerary Fits

Explain how the itinerary matches the
user's interests, budget and travel preference.

IMPORTANT:
Only use verified exact place names supplied
in the VERIFIED sections.

NEVER invent exact hotels,
restaurants or businesses.
"""

    try:

        response = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response[
            "message"
        ]["content"]

    except Exception as e:

        return (
            "❌ Itinerary generation failed.\n\n"
            f"Error: {e}"
        )


# ============================================================
# NOTE:
# The Trip Preferences form now lives on the main page
# (see the "TRIP PREFERENCES CARD" section near the top of
# this file). source, destination, budget, days, interests,
# travel_preference, and explore_button are already defined
# there and are reused below.
# ============================================================
# EXPLORE DESTINATION
# ============================================================

if explore_button:

    if not destination.strip():

        st.error(
            "❌ Please enter a destination."
        )

    elif not GEOAPIFY_API_KEY:

        st.error(
            "❌ Geoapify API key is missing."
        )

        st.info(
            "Check your .env file."
        )

    else:

        with st.spinner(
            f"🔎 Finding places in {destination}..."
        ):

            # Geocode destination first
            location = geoapify_geocode(
                destination
            )

            if not location:

                st.error(
                    f"❌ Could not find "
                    f"'{destination}'. "
                    "Please check the destination name."
                )

                st.stop()

            tourist_places = (
                get_tourist_spots(
                    destination
                )
            )

            hotel_places = (
                get_hotels(
                    destination
                )
            )

            restaurant_places = (
                get_restaurants(
                    destination
                )
            )

        # ----------------------------------------------------
        # STORE API RESULTS
        # ----------------------------------------------------

        st.session_state.tourist_places = (
            tourist_places
        )

        st.session_state.hotel_places = (
            hotel_places
        )

        st.session_state.restaurant_places = (
            restaurant_places
        )

        st.session_state.explored_destination = (
            destination.strip()
        )

        # ----------------------------------------------------
        # RESET OLD SELECTIONS
        # ----------------------------------------------------

        st.session_state.selected_spots = []

        st.session_state.selected_hotels = []

        st.session_state.selected_restaurants = []

        st.session_state.generated_itinerary = ""

        st.session_state.rag_results = []

        st.session_state.details_place = None

        # ----------------------------------------------------
        # RESULT MESSAGE
        # ----------------------------------------------------

        st.success(
            f"✅ Search completed for {destination}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🏛️ Tourist Spots",
                len(tourist_places)
            )

        with col2:

            st.metric(
                "🏨 Hotels",
                len(hotel_places)
            )

        with col3:

            st.metric(
                "🍽️ Restaurants",
                len(restaurant_places)
            )

        # ----------------------------------------------------
        # EMPTY RESULT DIAGNOSTIC
        # ----------------------------------------------------

        if (
            not tourist_places
            and not hotel_places
            and not restaurant_places
        ):

            st.error(
                "❌ Geoapify returned no places."
            )

            st.info(
                "Please check the terminal for "
                "Geoapify API error information."
            )

        st.rerun()


# ============================================================
# DISPLAY PLACES
# ============================================================

if (
    st.session_state.explored_destination
    and
    st.session_state.explored_destination.lower()
    ==
    destination.strip().lower()
):

    # ========================================================
    # TOURIST SPOTS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🏛️ Tourist Spots'
        '</div>',
        unsafe_allow_html=True
    )

    tourist_places = (
        st.session_state.tourist_places
    )

    if not tourist_places:

        st.warning(
            "No tourist spots were found by "
            "Geoapify for this destination."
        )

    else:

        for i, place in enumerate(
            tourist_places
        ):

            img_seed = normalize_text(
                place["name"]
            ).replace(" ", "-") or f"spot-{i}"

            st.markdown(
                f'<div class="place-card">'
                f'<img class="place-card-img" '
                f'src="https://picsum.photos/seed/{img_seed}/500/320" />'
                f'<div class="place-card-inner">'
                f'<span class="place-badge">🏛️ Tourist Spot</span>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"### {place['name']}"
            )

            st.write(
                f"Type: "
                f"{place.get('type', 'Tourist attraction')}"
            )

            if place.get("address"):

                st.write(
                    f"📍 {place['address']}"                    )

            col1, col2 = st.columns(2)

            details_key = (
                "tourist_details_"
                +
                hashlib.md5(
                    (
                        place["name"]
                        +
                        str(i)
                    ).encode()
                ).hexdigest()
            )

            pick_key = (
                "tourist_pick_"
                +
                hashlib.md5(
                    (
                        place["name"]
                        +
                        str(i)
                    ).encode()
                ).hexdigest()
            )

            with col1:

                if st.button(
                    "👁️ View Details",
                    key=details_key,
                    use_container_width=True
                ):

                    st.session_state.details_place = (
                        place
                    )

                    st.rerun()

            with col2:

                already_selected = any(
                    p["name"]
                    ==
                    place["name"]
                    for p
                    in
                    st.session_state.selected_spots
                )

                if already_selected:

                    st.success(
                        "✓ Selected"
                    )

                else:

                    if st.button(
                        "⭐ Pick",
                        key=pick_key,
                        use_container_width=True
                    ):

                        st.session_state.selected_spots.append(
                            place
                        )

                        st.rerun()

            st.markdown(
                "</div></div>",
                unsafe_allow_html=True
            )


    # ========================================================
    # HOTELS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🏨 Hotels'
        '</div>',
        unsafe_allow_html=True
    )

    hotel_places = (
        st.session_state.hotel_places
    )

    if not hotel_places:

        st.warning(
            "No hotels were found by Geoapify "
            "for this destination."
        )

    else:

        for i, place in enumerate(
            hotel_places
        ):

            img_seed = normalize_text(
                place["name"]
            ).replace(" ", "-") or f"hotel-{i}"

            st.markdown(
                f'<div class="place-card">'
                f'<img class="place-card-img" '
                f'src="https://picsum.photos/seed/{img_seed}/500/320" />'
                f'<div class="place-card-inner">'
                f'<span class="place-badge">🏨 Hotel</span>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"### {place['name']}"
            )

            st.write(
                f"Type: "
                f"{place.get('type', 'Hotel')}"
            )

            if place.get("address"):

                st.write(
                    f"📍 {place['address']}"
                )

            col1, col2 = st.columns(2)

            details_key = (
                "hotel_details_"
                +
                hashlib.md5(
                    (
                        place["name"]
                        +
                        str(i)
                    ).encode()
                ).hexdigest()
            )

            pick_key = (
                "hotel_pick_"
                +
                hashlib.md5(
                    (
                        place["name"]
                        +
                        str(i)
                    ).encode()
                ).hexdigest()
            )

            with col1:

                if st.button(
                    "👁️ View Details",
                    key=details_key,
                    use_container_width=True
                ):

                    st.session_state.details_place = (
                        place
                    )

                    st.rerun()

            with col2:

                selected_hotel = (
                    st.session_state.selected_hotels[0]
                    if
                    st.session_state.selected_hotels
                    else None
                )

                if (
                    selected_hotel
                    and
                    selected_hotel["name"]
                    ==
                    place["name"]
                ):

                    st.success(
                        "✓ Selected Hotel"
                    )

                else:

                    if st.button(
                        "⭐ Pick Hotel",
                        key=pick_key,
                        use_container_width=True
                    ):

                        # Only ONE hotel
                        st.session_state.selected_hotels = [
                            place
                        ]

                        st.rerun()

            st.markdown(
                "</div></div>",
                unsafe_allow_html=True
            )


    # ========================================================
    # RESTAURANTS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🍽️ Restaurants'
        '</div>',
        unsafe_allow_html=True
    )

    restaurant_places = (
        st.session_state.restaurant_places
    )

    if not restaurant_places:

        st.warning(
            "No restaurants were found by "
            "Geoapify for this destination."
        )

    else:

        for i, place in enumerate(
            restaurant_places
        ):

            img_seed = normalize_text(
                place["name"]
            ).replace(" ", "-") or f"restaurant-{i}"

            st.markdown(
                f'<div class="place-card">'
                f'<img class="place-card-img" '
                f'src="https://picsum.photos/seed/{img_seed}/500/320" />'
                f'<div class="place-card-inner">'
                f'<span class="place-badge">🍽️ Restaurant</span>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"### {place['name']}"
            )

            cuisine = (
                place.get("cuisine")
                or
                "Cuisine information unavailable"
            )

            st.write(
                f"Cuisine: {cuisine}"
            )

            if place.get("address"):

                st.write(
                    f"📍 {place['address']}"
                )

            col1, col2 = st.columns(2)

            details_key = (
                "restaurant_details_"
                +
                hashlib.md5(
                    (
                        place["name"]
                        +
                        str(i)
                    ).encode()
                ).hexdigest()
            )

            pick_key = (
                "restaurant_pick_"
                +
                hashlib.md5(
                    (
                        place["name"]
                        +
                        str(i)
                    ).encode()
                ).hexdigest()
            )

            with col1:

                if st.button(
                    "👁️ View Details",
                    key=details_key,
                    use_container_width=True
                ):

                    st.session_state.details_place = (
                        place
                    )

                    st.rerun()

            with col2:

                already_selected = any(
                    p["name"]
                    ==
                    place["name"]
                    for p
                    in
                    st.session_state.selected_restaurants
                )

                if already_selected:

                    st.success(
                        "✓ Selected"
                    )

                else:

                    if st.button(
                        "⭐ Pick",
                        key=pick_key,
                        use_container_width=True
                    ):

                        st.session_state.selected_restaurants.append(
                            place
                        )

                        st.rerun()

            st.markdown(
                "</div></div>",
                unsafe_allow_html=True
            )


    # ========================================================
    # MAP
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🗺️ Journey Map'
        '</div>',
        unsafe_allow_html=True
    )

    source_location = geoapify_geocode(source)

    destination_location = geoapify_geocode(destination)

    if source_location and destination_location:

        map_data = pd.DataFrame(
            {
                "latitude": [
                    source_location["lat"],
                    destination_location["lat"]
                ],
                "longitude": [
                    source_location["lon"],
                    destination_location["lon"]
                ]
            }
        )

        st.map(
            map_data,
            latitude="latitude",
            longitude="longitude",
            zoom=5
        )

    else:

        st.info(
            "🗺️ Map unavailable — could not resolve "
            "coordinates for one of the locations."
        )


    # ========================================================
    # DISTANCE & CARBON FOOTPRINT
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🌱 Distance & Carbon Footprint'
        '</div>',
        unsafe_allow_html=True
    )

    with st.spinner(
        "📏 Calculating distance..."
    ):

        distance_result = get_distance(
            source,
            destination
        )

    if distance_result:

        dist_km = distance_result["distance_km"]

        carbon_for_mode = compare_transport(
            dist_km
        )

        chosen_mode_key = travel_mode.lower().replace(
            "public transport", "bus"
        ).replace("bicycle", "cycling")

        carbon_value = carbon_for_mode.get(
            chosen_mode_key,
            carbon_for_mode.get("car", 0.0)
        )

        score = calculate_sustainability_score(
            travel_mode,
            carbon_value
        )

        level = get_sustainability_level(
            carbon_value
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "📏 Distance",
                f"{dist_km} km"
            )

        with col2:

            st.metric(
                "🌍 CO₂ (chosen mode)",
                f"{carbon_value} kg"
            )

        with col3:

            st.metric(
                "🌱 Sustainability",
                f"{score}/100"
            )

        with col4:

            st.metric(
                "📊 Impact Level",
                level
            )

        st.progress(
            score / 100
        )

        if distance_result["estimated"]:

            st.caption(
                "⚠️ Estimated distance (straight-line × 1.2 "
                "route factor). Not from a verified dataset."
            )

        emissions_df = pd.DataFrame(
            {
                "Transport Mode": [
                    m.title() for m in carbon_for_mode.keys()
                ],
                "CO2 Emissions (kg)": list(
                    carbon_for_mode.values()
                )
            }
        ).sort_values(
            "CO2 Emissions (kg)"
        )

        st.bar_chart(
            emissions_df.set_index(
                "Transport Mode"
            )
        )

        best_mode = get_best_option(
            dist_km
        )

        st.success(
            f"🌱 Lowest-emission option overall: "
            f"**{best_mode.title()}** "
            f"({carbon_for_mode[best_mode]} kg CO2 "
            f"for this trip)"
        )

        st.markdown(
            "#### 🌿 Green Recommendations"
        )

        for item in get_green_recommendations(
            travel_mode
        ):

            st.write(
                item
            )

    else:

        st.warning(
            "⚠️ Could not calculate distance between "
            f"{source} and {destination}. "
            "This may be due to a network or "
            "geocoding issue."
        )


# ============================================================
# PLACE DETAILS
# ============================================================

if st.session_state.details_place:

    place = (
        st.session_state.details_place
    )

    st.markdown(        '<div class="section-title">'
        '🔎 Place Details'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"## {place['name']}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Category:** "
            f"{place.get('category', '')}"
        )

        st.write(
            f"**Type:** "
            f"{place.get('type', '')}"
        )

        if place.get("address"):

            st.write(
                f"**📍 Address:** "
                f"{place['address']}"
            )

        if place.get("cuisine"):

            st.write(
                f"**🍽️ Cuisine:** "
                f"{place['cuisine']}"
            )

    with col2:

        if place.get("phone"):

            st.write(
                f"**📞 Phone:** "
                f"{place['phone']}"
            )

        if place.get("opening_hours"):

            st.write(
                f"**🕐 Opening Hours:** "
                f"{place['opening_hours']}"
            )

        if place.get("website"):

            st.markdown(
                f"**🌐 Website:** "
                f"[Open Website]"
                f"({place['website']})"
            )

    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    map_url = (
        "https://www.openstreetmap.org/"
        f"?mlat={place['lat']}"
        f"&mlon={place['lon']}"
        f"#map=18/"
        f"{place['lat']}/"
        f"{place['lon']}"
    )

    st.link_button(
        "🗺️ View Location",
        map_url
    )

    # --------------------------------------------------------
    # AI DESCRIPTION
    # --------------------------------------------------------

    with st.spinner(
        "🤖 Generating place information..."
    ):

        description = (
            generate_place_description(
                place["name"],
                place.get(
                    "category",
                    ""
                ),
                place.get(
                    "type",
                    ""
                ),
                place.get(
                    "address",
                    ""
                ),
                place.get(
                    "cuisine",
                    ""
                )
            )
        )

    st.markdown(
        "### 🤖 AI Description"
    )

    st.write(
        description
    )


# ============================================================
# SELECTED PLACES
# ============================================================

st.markdown(
    '<div class="section-title">'
    '⭐ Your Selected Places'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SELECTED TOURIST SPOTS
# ============================================================

st.markdown(
    "### 🏛️ Tourist Spots"
)

if st.session_state.selected_spots:

    for i, place in enumerate(
        st.session_state.selected_spots
    ):

        col1, col2 = st.columns(
            [5, 1]
        )

        with col1:

            st.write(
                f"⭐ {place['name']}"
            )

        with col2:

            if st.button(
                "Remove",
                key=f"remove_spot_{i}"
            ):

                st.session_state.selected_spots.pop(
                    i
                )

                st.rerun()

else:

    st.write(
        "No tourist spots selected."
    )


# ============================================================
# SELECTED HOTEL
# ============================================================

st.markdown(
    "### 🏨 Hotel"
)

if st.session_state.selected_hotels:

    hotel = (
        st.session_state.selected_hotels[0]
    )

    col1, col2 = st.columns(
        [5, 1]
    )

    with col1:

        st.write(
            f"⭐ {hotel['name']}"
        )

    with col2:

        if st.button(
            "Remove",
            key="remove_hotel"
        ):

            st.session_state.selected_hotels = []

            st.rerun()

else:

    st.write(
        "No hotel selected."
    )


# ============================================================
# SELECTED RESTAURANTS
# ============================================================

st.markdown(
    "### 🍽️ Restaurants"
)

if st.session_state.selected_restaurants:

    for i, restaurant in enumerate(
        st.session_state.selected_restaurants
    ):

        col1, col2 = st.columns(
            [5, 1]
        )

        with col1:

            st.write(
                f"⭐ {restaurant['name']}"
            )

        with col2:

            if st.button(
                "Remove",
                key=f"remove_restaurant_{i}"
            ):

                st.session_state.selected_restaurants.pop(
                    i
                )

                st.rerun()

else:

    st.write(
        "No restaurants selected."
    )


# ============================================================
# GENERATE ITINERARY
# ============================================================

st.markdown("---")

generate_button = st.button(
    "🧳 Generate My AI Itinerary",
    type="primary",
    use_container_width=True
)


if generate_button:

    if not destination.strip():

        st.error(
            "❌ Please enter a destination."
        )

    elif not GEOAPIFY_API_KEY:

        st.error(
            "❌ Geoapify API key is missing."
        )

    else:

        with st.spinner(
            "📚 Retrieving destination information..."
        ):

            rag_results = retrieve_information(
                destination,
                interests,
                top_k=8
            )

            st.session_state.rag_results = (
                rag_results
            )

            rag_context = build_rag_context(
                rag_results
            )

        selected_hotel = (
            st.session_state.selected_hotels[0]
            if
            st.session_state.selected_hotels
            else None
        )

        with st.spinner(
            "🤖 Llama 3 is creating your itinerary..."
        ):

            itinerary = generate_itinerary(
                source=source,
                destination=destination,
                budget=budget,
                days=days,
                interests=interests,
                travel_preference=travel_preference,
                selected_spots=(
                    st.session_state.selected_spots
                ),
                selected_hotel=selected_hotel,
                selected_restaurants=(
                    st.session_state.selected_restaurants
                ),
                rag_context=rag_context
            )

        st.session_state.generated_itinerary = (
            itinerary
        )


# ============================================================
# DISPLAY ITINERARY
# ============================================================

if st.session_state.generated_itinerary:

    st.markdown(
        '<div class="section-title">'
        '🧳 Your AI-Generated Itinerary'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        st.session_state.generated_itinerary
    )

    # --------------------------------------------------------
    # SUGGESTED BUDGET BREAKDOWN
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '💰 Suggested Budget Breakdown'
        '</div>',
        unsafe_allow_html=True
    )

    budget_data = create_budget(
        budget
    )

    budget_df = pd.DataFrame(
        {
            "Category": list(budget_data.keys()),
            "Amount (₹)": list(budget_data.values())
        }
    )

    st.dataframe(
        budget_df,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        budget_df.set_index("Category")
    )

    # --------------------------------------------------------
    # DOWNLOAD ITINERARY
    # --------------------------------------------------------

    download_content = f"""
AI VOYAGE PLANNER
=================

FROM: {source}
TO: {destination}

DURATION: {days} days
BUDGET: ₹{budget}
TRAVEL PREFERENCE: {travel_preference}
TRANSPORT: {travel_mode}
INTERESTS: {', '.join(interests)}


AI ITINERARY
============

{st.session_state.generated_itinerary}


SUGGESTED BUDGET
================

"""

    for category, amount in budget_data.items():

        download_content += f"{category}: ₹{amount}\n"

    st.download_button(
        "📥 Download Itinerary",
        download_content,
        "AI_Voyage_Planner_Itinerary.txt",
        "text/plain",
        use_container_width=True
    )


# ============================================================
# RAG SOURCES
# ============================================================

if st.session_state.rag_results:

    with st.expander(
        "📚 View RAG Sources"
    ):

        for i, result in enumerate(
            st.session_state.rag_results,
            start=1
        ):

            st.markdown(
                f"**Source {i}**"
            )

            st.write(
                result["text"]
            )

            st.markdown(
                "---"
            )

else:

    if st.session_state.generated_itinerary:

        with st.expander(
            "📚 RAG Information"
        ):

            st.info(
                "No destination-specific information "
                "was found in the RAG database. "
                "Llama 3 generated the general itinerary "
                "without using unrelated destinations."
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    "---"
)

st.markdown(
    """
    <div class="app-footer">
        <div class="footer-title">🌍 AI Voyage Planner</div>
        <div class="footer-sub">
            Generative AI • RAG • Geoapify API •
            Sustainable Tourism • Personalized Travel Planning
        </div>
    </div>
    """,
    unsafe_allow_html=True
)