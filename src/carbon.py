# ============================================================
# AI SUSTAINABLE TOURISM PLANNER
# Carbon Footprint Estimator
# ============================================================


EMISSION_FACTORS = {
    "walking": 0.0,
    "cycling": 0.0,
    "train": 0.041,
    "bus": 0.089,
    "shared": 0.105,
    "car": 0.192,
    "flight": 0.255
}


def calculate_carbon(distance_km, transport_mode, passengers=1):

    mode = transport_mode.lower().strip()

    if mode not in EMISSION_FACTORS:
        raise ValueError(f"Unsupported transport mode: {transport_mode}")

    factor = EMISSION_FACTORS[mode]

    if mode in ["car", "shared"]:
        passengers = max(passengers, 1)
        emissions = distance_km * factor / passengers
    else:
        emissions = distance_km * factor

    return round(emissions, 2)


def compare_transport(distance_km):

    results = {}

    for mode in EMISSION_FACTORS:
        results[mode] = calculate_carbon(distance_km, mode)

    return results


def get_best_option(distance_km):

    results = compare_transport(distance_km)

    return min(results, key=results.get)