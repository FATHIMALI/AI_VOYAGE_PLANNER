import os
import pandas as pd

DATA_DIR = "data"
MASTER_DIR = os.path.join(DATA_DIR, "master")

os.makedirs(MASTER_DIR, exist_ok=True)


# --------------------------------------------------
# 1. TOP INDIAN PLACES
# --------------------------------------------------

top_places = os.path.join(
    DATA_DIR,
    "top indian place",
    "Top Indian Places to Visit.csv"
)

if os.path.exists(top_places):
    df = pd.read_csv(top_places)

    df = df.rename(columns={
        "City": "city",
        "Name": "name",
        "Type": "type",
        "time needed to visit in hrs": "visit_hours",
        "Google review rating": "rating",
        "Entrance Fee in INR": "entrance_fee",
        "Weekly Off": "weekly_off",
        "Significance": "significance",
        "Best Time to visit": "best_time"
    })

    columns = [
        "city",
        "name",
        "type",
        "visit_hours",
        "rating",
        "entrance_fee",
        "weekly_off",
        "significance",
        "best_time"
    ]

    columns = [c for c in columns if c in df.columns]

    places_master = df[columns].copy()

else:
    places_master = pd.DataFrame()


# --------------------------------------------------
# 2. TOURIST SPOT DATA
# --------------------------------------------------

tourist_folder = os.path.join(DATA_DIR, "Tourist spot")

tourist_data = []

if os.path.exists(tourist_folder):

    for file in os.listdir(tourist_folder):

        if file.lower().endswith(".csv"):

            path = os.path.join(tourist_folder, file)

            try:
                df = pd.read_csv(path)

                # Find common columns
                name_col = None
                lat_col = None
                lon_col = None
                char_col = None

                for col in df.columns:
                    c = col.lower()

                    if c in ["name", "poi_name"]:
                        name_col = col

                    if "latitude" in c:
                        lat_col = col

                    if "longitude" in c:
                        lon_col = col

                    if "characteristics" in c:
                        char_col = col

                if name_col and lat_col and lon_col:

                    temp = pd.DataFrame()

                    temp["name"] = df[name_col]
                    temp["latitude"] = df[lat_col]
                    temp["longitude"] = df[lon_col]

                    if char_col:
                        temp["characteristics"] = df[char_col]
                    else:
                        temp["characteristics"] = ""

                    # City from filename
                    city = file.replace(
                        "Destinations_", ""
                    ).replace(
                        ".csv", ""
                    )

                    temp["city"] = city.title()

                    tourist_data.append(temp)

            except Exception as e:
                print("Skipped:", file)
                print("Reason:", e)


if tourist_data:

    tourist_master = pd.concat(
        tourist_data,
        ignore_index=True
    )

else:

    tourist_master = pd.DataFrame(
        columns=[
            "name",
            "latitude",
            "longitude",
            "characteristics",
            "city"
        ]
    )


# --------------------------------------------------
# 3. SAVE MASTER TOURIST SPOTS
# --------------------------------------------------

tourist_master.to_csv(
    os.path.join(
        MASTER_DIR,
        "tourist_spots_master.csv"
    ),
    index=False
)


# --------------------------------------------------
# 4. SAVE TOP PLACES MASTER
# --------------------------------------------------

places_master.to_csv(
    os.path.join(
        MASTER_DIR,
        "places_master.csv"
    ),
    index=False
)


# --------------------------------------------------
# 5. HOTELS
# --------------------------------------------------

hotel_file = os.path.join(
    DATA_DIR,
    "hotels",
    "hotel_details.csv"
)

if os.path.exists(hotel_file):

    hotels = pd.read_csv(hotel_file)

    hotels = hotels.rename(columns={
        "Hotel Name": "hotel_name",
        "Place": "place",
        "description": "description",
        "Condition": "condition",
        "Rating": "rating",
        "Total Reviews": "total_reviews"
    })

    hotels.to_csv(
        os.path.join(
            MASTER_DIR,
            "hotels_master.csv"
        ),
        index=False
    )


# --------------------------------------------------
# DONE
# --------------------------------------------------

print("\n================================")
print("MASTER DATA CREATED SUCCESSFULLY")
print("================================")

print("\nFiles created:")

for file in os.listdir(MASTER_DIR):
    print(" -", file)

print("\nTourist spots:",
      len(tourist_master))

print("Top places:",
      len(places_master))

print("\nNext step: connect master data to FastAPI.")