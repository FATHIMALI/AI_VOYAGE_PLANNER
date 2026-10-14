import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

function PlanTrip() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // =========================================================
  // TRIP DETAILS
  // =========================================================

  const [origin, setOrigin] = useState(
    searchParams.get("origin") || ""
  );

  const [destination, setDestination] = useState(
    searchParams.get("destination") || ""
  );

  const [startDate, setStartDate] = useState(
    searchParams.get("start_date") || ""
  );

  const [endDate, setEndDate] = useState(
    searchParams.get("end_date") || ""
  );

  const [travelers, setTravelers] = useState(
    Number(searchParams.get("travelers")) || 1
  );

  const [budget, setBudget] = useState(25000);

  const [selectedInterests, setSelectedInterests] = useState([]);

  // Lunch preference:
  // vegetarian / non_vegetarian / both
  const [lunchPreference, setLunchPreference] = useState("both");

  const [loading, setLoading] = useState(false);

  // =========================================================
  // INTERESTS
  // =========================================================

  const interests = [
    {
      id: "culture",
      icon: "🏛️",
      title: "Culture",
      description: "Heritage & traditions",
    },
    {
      id: "history",
      icon: "🏰",
      title: "History",
      description: "Historic places",
    },
    {
      id: "nature",
      icon: "🌿",
      title: "Nature",
      description: "Parks & landscapes",
    },
    {
      id: "food",
      icon: "🍜",
      title: "Food",
      description: "Local cuisine",
    },
    {
      id: "adventure",
      icon: "🧗",
      title: "Adventure",
      description: "Thrilling activities",
    },
    {
      id: "shopping",
      icon: "🛍️",
      title: "Shopping",
      description: "Markets & malls",
    },
    {
      id: "relaxation",
      icon: "🏖️",
      title: "Relaxation",
      description: "Peaceful experiences",
    },
    {
      id: "photography",
      icon: "📸",
      title: "Photography",
      description: "Scenic locations",
    },
  ];

  // =========================================================
  // TOGGLE INTEREST
  // =========================================================

  const toggleInterest = (interest) => {
    setSelectedInterests((current) => {
      if (current.includes(interest)) {
        return current.filter((item) => item !== interest);
      }

      return [...current, interest];
    });
  };

  // =========================================================
  // GENERATE TRIP
  // =========================================================

  const handleGenerateTrip = async () => {
    if (!destination.trim()) {
      alert("Please enter your destination.");
      return;
    }

    if (!startDate || !endDate) {
      alert("Please select your travel dates.");
      return;
    }

    if (new Date(endDate) < new Date(startDate)) {
      alert("Return date cannot be before departure date.");
      return;
    }

    if (selectedInterests.length === 0) {
      alert("Please select at least one travel interest.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/api/trips/plan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            origin: origin || "India",
            destination: destination.trim(),
            start_date: startDate,
            end_date: endDate,
            travelers,
            budget,
            interests: selectedInterests,

            // NEW
            lunch_preference: lunchPreference,
          }),
        }
      );

      if (!response.ok) {
        let errorMessage = "Unable to generate trip.";

        try {
          const errorData = await response.json();

          if (errorData?.detail) {
            errorMessage =
              typeof errorData.detail === "string"
                ? errorData.detail
                : "Unable to generate trip.";
          }
        } catch {
          // Keep default error message
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();

      // Store complete AI trip response
      sessionStorage.setItem(
        "aiTripResult",
        JSON.stringify(data)
      );

      // Also store the food preference separately.
      // This helps Results.jsx access it if required.
      sessionStorage.setItem(
        "lunchPreference",
        lunchPreference
      );

      navigate("/results");
    } catch (error) {
      console.error("Trip generation error:", error);

      alert(
        error.message ||
          "Unable to generate the trip right now. Please make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // UI
  // =========================================================

  return (
    <main className="plan-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <section className="plan-header">
        <div className="plan-header-content">

          <span className="plan-eyebrow">
            AI TRIP PLANNER
          </span>

          <h1>
            Plan a trip
            <br />
            <span>made for you.</span>
          </h1>

          <p>
            Tell us what you want from your journey. Our AI will
            create a personalized travel plan based on your
            destination, dates, budget and interests.
          </p>

        </div>
      </section>

      {/* =====================================================
          PLANNER
      ===================================================== */}

      <section className="plan-container">

        <div className="plan-main-card">

          {/* =================================================
              01 — TRIP DETAILS
          ================================================= */}

          <div className="plan-section">

            <div className="plan-section-heading">

              <div className="plan-number">
                01
              </div>

              <div>
                <h2>Where are you going?</h2>

                <p>
                  Tell us your starting point and destination.
                </p>
              </div>

            </div>

            <div className="plan-location-grid">

              {/* FROM */}

              <div className="plan-input-group">

                <label>FROM</label>

                <div className="plan-input">

                  <span>📍</span>

                  <input
                    type="text"
                    placeholder="Starting city"
                    value={origin}
                    onChange={(e) =>
                      setOrigin(e.target.value)
                    }
                  />

                </div>

              </div>

              {/* DESTINATION */}

              <div className="plan-input-group">

                <label>DESTINATION</label>

                <div className="plan-input">

                  <span>✈️</span>

                  <input
                    type="text"
                    placeholder="Where do you want to go?"
                    value={destination}
                    onChange={(e) =>
                      setDestination(e.target.value)
                    }
                  />

                </div>

              </div>

            </div>

          </div>

          {/* =================================================
              02 — DATES
          ================================================= */}

          <div className="plan-section">

            <div className="plan-section-heading">

              <div className="plan-number">
                02
              </div>

              <div>
                <h2>When are you travelling?</h2>

                <p>
                  Choose your travel dates.
                </p>
              </div>

            </div>

            <div className="plan-location-grid">

              {/* DEPARTURE */}

              <div className="plan-input-group">

                <label>DEPARTURE</label>

                <div className="plan-input">

                  <span>📅</span>

                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) =>
                      setStartDate(e.target.value)
                    }
                  />

                </div>

              </div>

              {/* RETURN */}

              <div className="plan-input-group">

                <label>RETURN</label>

                <div className="plan-input">

                  <span>📅</span>

                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) =>
                      setEndDate(e.target.value)
                    }
                  />

                </div>

              </div>

            </div>

          </div>

          {/* =================================================
              03 — TRIP PREFERENCES
          ================================================= */}

          <div className="plan-section">

            <div className="plan-section-heading">

              <div className="plan-number">
                03
              </div>

              <div>
                <h2>Trip preferences</h2>

                <p>
                  Help AI understand your travel style.
                </p>
              </div>

            </div>

            <div className="plan-preferences-grid">

              {/* TRAVELLERS */}

              <div className="plan-input-group">

                <label>TRAVELLERS</label>

                <div className="plan-input">

                  <span>👥</span>

                  <select
                    value={travelers}
                    onChange={(e) =>
                      setTravelers(
                        Number(e.target.value)
                      )
                    }
                  >

                    <option value={1}>
                      1 Traveller
                    </option>

                    <option value={2}>
                      2 Travellers
                    </option>

                    <option value={3}>
                      3 Travellers
                    </option>

                    <option value={4}>
                      4 Travellers
                    </option>

                    <option value={5}>
                      5 Travellers
                    </option>

                    <option value={6}>
                      6 Travellers
                    </option>

                    <option value={7}>
                      7 Travellers
                    </option>

                    <option value={8}>
                      8 Travellers
                    </option>

                  </select>

                </div>

              </div>

              {/* BUDGET */}

              <div className="plan-budget">

                <div className="budget-header">

                  <label>TRIP BUDGET</label>

                  <strong>
                    ₹{budget.toLocaleString("en-IN")}
                  </strong>

                </div>

                <input
                  type="range"
                  min="5000"
                  max="200000"
                  step="5000"
                  value={budget}
                  onChange={(e) =>
                    setBudget(
                      Number(e.target.value)
                    )
                  }
                />

                <div className="budget-range">

                  <span>₹5,000</span>

                  <span>₹2,00,000+</span>

                </div>

              </div>

            </div>

          </div>

          {/* =================================================
              04 — INTERESTS
          ================================================= */}

          <div className="plan-section">

            <div className="plan-section-heading">

              <div className="plan-number">
                04
              </div>

              <div>
                <h2>What do you love?</h2>

                <p>
                  Select everything you'd like to experience.
                </p>
              </div>

            </div>

            <div className="interest-grid">

              {interests.map((interest) => {

                const selected =
                  selectedInterests.includes(
                    interest.id
                  );

                return (
                  <button
                    type="button"
                    key={interest.id}
                    className={`interest-card ${
                      selected ? "selected" : ""
                    }`}
                    onClick={() =>
                      toggleInterest(interest.id)
                    }
                  >

                    <div className="interest-icon">
                      {interest.icon}
                    </div>

                    <div className="interest-info">

                      <strong>
                        {interest.title}
                      </strong>

                      <span>
                        {interest.description}
                      </span>

                    </div>

                    <div className="interest-check">
                      {selected ? "✓" : "+"}
                    </div>

                  </button>
                );
              })}

            </div>

          </div>

          {/* =================================================
              05 — LUNCH FOOD PREFERENCE
          ================================================= */}

          <div className="plan-section">

            <div className="plan-section-heading">

              <div className="plan-number">
                05
              </div>

              <div>
                <h2>What would you like for lunch?</h2>

                <p>
                  Choose your preferred food type for nearby
                  lunch restaurants.
                </p>
              </div>

            </div>

            <div className="food-preference-grid">

              {/* VEGETARIAN */}

              <button
                type="button"
                className={`food-preference-card ${
                  lunchPreference === "vegetarian"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setLunchPreference("vegetarian")
                }
              >

                <div className="food-icon">
                  🥗
                </div>

                <div className="food-preference-info">

                  <strong>
                    Vegetarian
                  </strong>

                  <span>
                    Prefer vegetarian restaurants
                  </span>

                </div>

                <div className="food-check">
                  {lunchPreference === "vegetarian"
                    ? "✓"
                    : ""}
                </div>

              </button>

              {/* NON-VEGETARIAN */}

              <button
                type="button"
                className={`food-preference-card ${
                  lunchPreference === "non_vegetarian"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setLunchPreference(
                    "non_vegetarian"
                  )
                }
              >

                <div className="food-icon">
                  🍗
                </div>

                <div className="food-preference-info">

                  <strong>
                    Non-Vegetarian
                  </strong>

                  <span>
                    Prefer non-veg restaurants
                  </span>

                </div>

                <div className="food-check">
                  {lunchPreference ===
                  "non_vegetarian"
                    ? "✓"
                    : ""}
                </div>

              </button>

              {/* BOTH */}

              <button
                type="button"
                className={`food-preference-card ${
                  lunchPreference === "both"
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  setLunchPreference("both")
                }
              >

                <div className="food-icon">
                  🍽️
                </div>

                <div className="food-preference-info">

                  <strong>
                    Both
                  </strong>

                  <span>
                    Show veg & non-veg options
                  </span>

                </div>

                <div className="food-check">
                  {lunchPreference === "both"
                    ? "✓"
                    : ""}
                </div>

              </button>

            </div>

          </div>

          {/* =================================================
              GENERATE
          ================================================= */}

          <div className="plan-generate-section">

            <div>

              <span>
                ✨ AI TRAVEL INTELLIGENCE
              </span>

              <h2>
                Ready to build your journey?
              </h2>

              <p>
                AI will combine your preferences with
                destination, weather, places and travel
                information to create your itinerary.
              </p>

            </div>

            <button
              className="generate-trip-btn"
              onClick={handleGenerateTrip}
              disabled={loading}
            >

              {loading
                ? "Creating your trip..."
                : "✨ Generate My Trip"}

            </button>

          </div>

        </div>

      </section>

    </main>
  );
}

export default PlanTrip;