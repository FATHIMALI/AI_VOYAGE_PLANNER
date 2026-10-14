def calculate_sustainability_score(
    travel_preference,
    local_business=True,
    eco_accommodation=True,
    responsible_tourism=True
):
    score = 0

    preference = travel_preference.lower()

    if "walk" in preference:
        score += 30
    elif "cycle" in preference or "cycling" in preference:
        score += 30
    elif "public" in preference:
        score += 25
    elif "train" in preference:
        score += 25
    elif "shared" in preference:
        score += 20
    elif "bus" in preference:
        score += 20
    elif "car" in preference:
        score += 10
    else:
        score += 15

    if local_business:
        score += 20

    if eco_accommodation:
        score += 20

    if responsible_tourism:
        score += 20

    return min(score, 100)


def get_rating(score):

    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Moderate"
    else:
        return "Needs Improvement"