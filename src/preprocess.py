import pandas as pd
import os

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ============================================================
# 1. CARBON DATA
# ============================================================

carbon_file = os.path.join(
    RAW_DIR,
    "co2-emissions-transport.csv"
)

carbon = pd.read_csv(carbon_file)

carbon = carbon.rename(columns={
    "Entity": "country",
    "Code": "country_code",
    "Year": "year",
    "Carbon dioxide emissions from transport":
        "transport_co2"
})

carbon = carbon.dropna(subset=["country", "year", "transport_co2"])

carbon.to_csv(
    os.path.join(PROCESSED_DIR, "carbon.csv"),
    index=False
)

print("Created carbon.csv")


# ============================================================
# 2. ATTRACTIONS DATA
# ============================================================

attractions_file = os.path.join(
    RAW_DIR,
    "India-Tourism-Statistics-2022-Table-5.2.2.csv"
)

attractions_raw = pd.read_csv(attractions_file)


domestic = attractions_raw[
    [
        "10 Most popular Centrally Protected Ticketed Monuments for Domestic Visitors in 2021-22 - Rank",
        "10 Most popular Centrally Protected Ticketed Monuments for Domestic Visitors in 2021-22 - Name of Monument",
        "10 Most popular Centrally Protected Ticketed Monuments for Domestic Visitors in 2021-22 - No. of Domestic visitors",
        "10 Most popular Centrally Protected Ticketed Monuments for Domestic Visitors in 2021-22 - Percentage share"
    ]
].copy()

domestic.columns = [
    "rank",
    "monument",
    "domestic_visitors",
    "domestic_percentage"
]

foreign = attractions_raw[
    [
        "10 Most popular Centrally Protected Ticketed Monuments for Foreign Visitors in 2021-22 - Rank",
        "10 Most popular Centrally Protected Ticketed Monuments for Foreign Visitors in 2021-22 - Name of Monument",
        "10 Most popular Centrally Protected Ticketed Monuments for Foreign Visitors in 2021-22 - No. of Foreign visitors",
        "10 Most popular Centrally Protected Ticketed Monuments for Foreign Visitors in 2021-22 - Percentage share"
    ]
].copy()

foreign.columns = [
    "foreign_rank",
    "foreign_monument",
    "foreign_visitors",
    "foreign_percentage"
]

attractions = domestic.copy()

attractions["foreign_rank"] = foreign["foreign_rank"]
attractions["foreign_monument"] = foreign["foreign_monument"]
attractions["foreign_visitors"] = foreign["foreign_visitors"]
attractions["foreign_percentage"] = foreign["foreign_percentage"]

attractions.to_csv(
    os.path.join(PROCESSED_DIR, "attractions.csv"),
    index=False
)

print("Created attractions.csv")

# Remove aggregate/non-attraction rows
attractions = attractions[
    ~attractions["monument"].astype(str).str.strip().isin(
        ["Others", "Total"]
    )
].copy()

# ============================================================
# 3. TRANSPORT DATA
# ============================================================

transport_file = os.path.join(
    RAW_DIR,
    "indian-cities-dataset.csv"
)

transport = pd.read_csv(transport_file)

transport = transport.rename(columns={
    "Origin": "origin",
    "Destination": "destination",
    "Distance": "distance_km"
})

transport = transport.dropna(
    subset=["origin", "destination", "distance_km"]
)

transport.to_csv(
    os.path.join(PROCESSED_DIR, "transport.csv"),
    index=False
)

print("Created transport.csv")


# ============================================================
# 4. DESTINATIONS DATA
# ============================================================

destinations = attractions[["monument"]].copy()

destinations = destinations.rename(
    columns={"monument": "destination"}
)

destinations = destinations.dropna()
destinations = destinations.drop_duplicates()

destinations.to_csv(
    os.path.join(PROCESSED_DIR, "destinations.csv"),
    index=False
)

print("Created destinations.csv")


print("\nPreprocessing completed successfully!")