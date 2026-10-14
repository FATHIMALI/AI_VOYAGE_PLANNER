import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const API_URL = "http://127.0.0.1:8000";

function Results() {
  const navigate = useNavigate();

  const [tripData, setTripData] = useState(null);
  const [activeDay, setActiveDay] = useState(1);

  const [routeImage, setRouteImage] = useState(null);
  const [livePlaces, setLivePlaces] = useState([]);
  const [loadingPlaces, setLoadingPlaces] = useState(false);
  const [routeLoading, setRouteLoading] = useState(false);

  /* =====================================================
     LOAD SAVED TRIP
  ===================================================== */

  useEffect(() => {
    const savedTrip = sessionStorage.getItem("aiTripResult");

    if (!savedTrip) {
      return;
    }

    try {
      const parsedTrip = JSON.parse(savedTrip);
      setTripData(parsedTrip);
    } catch (error) {
      console.error("Unable to read saved trip:", error);
    }
  }, []);

  /* =====================================================
     TRIP DATA
  ===================================================== */

  const trip = tripData?.trip || {};

  const destination =
    trip.destination ||
    tripData?.destination ||
    "Your Destination";

  const origin =
    trip.origin ||
    tripData?.origin ||
    "India";

  const startDate =
    trip.start_date ||
    tripData?.start_date ||
    "";

  const endDate =
    trip.end_date ||
    tripData?.end_date ||
    "";

  const travelers =
    trip.travelers ??
    tripData?.travelers ??
    1;

  const budget =
    trip.budget ??
    tripData?.budget ??
    0;

  const itinerary = Array.isArray(tripData?.itinerary)
    ? tripData.itinerary
    : [];

  const places = Array.isArray(tripData?.places)
    ? tripData.places
    : [];

  const hotels = Array.isArray(tripData?.hotels)
    ? tripData.hotels
    : [];

  const weather = tripData?.weather || {};

  const transport = tripData?.transport || {};

  /* =====================================================
     FETCH LIVE PLACES + ROUTE
  ===================================================== */

  useEffect(() => {
    if (!tripData || !destination) {
      return;
    }

    let createdImageUrl = null;
    let cancelled = false;

    const loadLiveData = async () => {
      setLoadingPlaces(true);
      setRouteLoading(true);

      try {
        /* =================================================
           LIVE PLACES
        ================================================= */

        const placesResponse = await fetch(
          `${API_URL}/api/live/places?city=${encodeURIComponent(
            destination
          )}`
        );

        if (placesResponse.ok) {
          const data = await placesResponse.json();

          let receivedPlaces = [];

          if (Array.isArray(data)) {
            receivedPlaces = data;
          } else if (Array.isArray(data.items)) {
            receivedPlaces = data.items;
          } else if (Array.isArray(data.places)) {
            receivedPlaces = data.places;
          } else if (Array.isArray(data.results)) {
            receivedPlaces = data.results;
          } else if (Array.isArray(data.features)) {
            receivedPlaces = data.features;
          }

          if (!cancelled) {
            setLivePlaces(receivedPlaces);
          }
        } else {
          if (!cancelled) {
            setLivePlaces([]);
          }
        }

        /* =================================================
           LIVE ROUTE MAP
        ================================================= */

        const routeResponse = await fetch(
          `${API_URL}/api/routes/map?origin=${encodeURIComponent(
            origin
          )}&destination=${encodeURIComponent(destination)}`
        );

        if (routeResponse.ok) {
          const blob = await routeResponse.blob();

          createdImageUrl = URL.createObjectURL(blob);

          if (!cancelled) {
            setRouteImage(createdImageUrl);
          }
        } else {
          if (!cancelled) {
            setRouteImage(null);
          }
        }
      } catch (error) {
        console.error(
          "Unable to load live travel data:",
          error
        );

        if (!cancelled) {
          setLivePlaces([]);
          setRouteImage(null);
        }
      } finally {
        if (!cancelled) {
          setLoadingPlaces(false);
          setRouteLoading(false);
        }
      }
    };

    loadLiveData();

    return () => {
      cancelled = true;

      if (createdImageUrl) {
        URL.revokeObjectURL(createdImageUrl);
      }
    };
  }, [tripData, destination, origin]);

  /* =====================================================
     DAYS
  ===================================================== */

  const days = useMemo(() => {
    return itinerary.map((day, index) => ({
      ...day,
      dayNumber:
        Number(day?.day || day?.day_number) ||
        index + 1,
    }));
  }, [itinerary]);

  /* =====================================================
     KEEP ACTIVE DAY VALID
  ===================================================== */

  useEffect(() => {
    if (days.length === 0) {
      setActiveDay(1);
      return;
    }

    const exists = days.some(
      (day) => day.dayNumber === activeDay
    );

    if (!exists) {
      setActiveDay(days[0].dayNumber);
    }
  }, [days, activeDay]);

  const currentDay =
    days.find(
      (day) => day.dayNumber === activeDay
    ) || days[0];

  /* =====================================================
     ACTIVITY HELPERS
  ===================================================== */

  const normalizeActivities = (value) => {
    if (!Array.isArray(value)) {
      return [];
    }

    return value.filter(Boolean);
  };

  const getActivities = (day) => {
    if (!day) {
      return [];
    }

    if (Array.isArray(day.activities)) {
      return day.activities;
    }

    if (Array.isArray(day.places)) {
      return day.places;
    }

    if (Array.isArray(day.schedule)) {
      return day.schedule;
    }

    if (
      day.name ||
      day.title ||
      day.place ||
      day.location
    ) {
      return [day];
    }

    return [];
  };

  const currentActivities =
    getActivities(currentDay);

  /* =====================================================
     TIME SLOTS
  ===================================================== */

  const timeSlots = [
    {
      key: "morning",
      label: "MORNING",
      title: "Morning",
      icon: "🌅",
    },
    {
      key: "afternoon",
      label: "AFTERNOON",
      title: "Afternoon",
      icon: "☀️",
    },
    {
      key: "evening",
      label: "EVENING",
      title: "Evening",
      icon: "🌆",
    },
  ];

  /* =====================================================
     GET PLACES FOR SPECIFIC PERIOD
  ===================================================== */

  const getDayPlaces = (day, period) => {
    if (!day) {
      return [];
    }

    const direct = normalizeActivities(
      day?.[period]
    );

    if (direct.length > 0) {
      return direct;
    }

    const alternativeKeys = [
      `${period}_places`,
      `${period}Places`,
      `${period}_activities`,
      `${period}Activities`,
    ];

    for (const key of alternativeKeys) {
      const value = normalizeActivities(
        day?.[key]
      );

      if (value.length > 0) {
        return value;
      }
    }

    return [];
  };

  /* =====================================================
     GET ACTIVITIES FOR DISPLAY
  ===================================================== */

  const getActivitiesForSlot = (day, period) => {
    const directPlaces = getDayPlaces(
      day,
      period
    );

    if (directPlaces.length > 0) {
      return directPlaces;
    }

    /* ---------------------------------------------
       Fallback only for older backend structures
    --------------------------------------------- */

    if (
      period === "morning" &&
      Array.isArray(day?.activities)
    ) {
      return day.activities.slice(0, 2);
    }

    if (
      period === "afternoon" &&
      Array.isArray(day?.activities)
    ) {
      return day.activities.slice(2, 4);
    }

    if (
      period === "evening" &&
      Array.isArray(day?.activities)
    ) {
      return day.activities.slice(4, 6);
    }

    return [];
  };

  /* =====================================================
     ACTIVITY DATA HELPERS
  ===================================================== */

  const getName = (activity) => {
    if (!activity) {
      return "Free time / Explore nearby";
    }

    if (typeof activity === "string") {
      return activity;
    }

    const properties =
      activity?.properties || activity;

    return (
      properties?.name ||
      activity?.name ||
      activity?.title ||
      activity?.place ||
      activity?.location ||
      "Explore destination"
    );
  };

  const getDescription = (activity) => {
    if (!activity) {
      return "Use this time to explore nearby attractions, cafés or local areas.";
    }

    if (typeof activity === "string") {
      return "Explore this destination and enjoy the local experience.";
    }

    const properties =
      activity?.properties || activity;

    return (
      properties?.description ||
      activity?.description ||
      properties?.significance ||
      activity?.significance ||
      activity?.about ||
      properties?.type ||
      activity?.type ||
      "A recommended experience based on your travel preferences."
    );
  };

  const getType = (activity) => {
    if (!activity) {
      return "EXPERIENCE";
    }

    if (typeof activity === "string") {
      return "EXPERIENCE";
    }

    const properties =
      activity?.properties || activity;

    const categories =
      properties?.categories;

    if (
      Array.isArray(categories) &&
      categories.length > 0
    ) {
      return String(categories[0])
        .split(".")
        .pop()
        .replaceAll("_", " ")
        .toUpperCase();
    }

    return (
      properties?.type ||
      activity?.type ||
      properties?.category ||
      activity?.category ||
      "ATTRACTION"
    );
  };

  const getRating = (activity) => {
    if (!activity) {
      return null;
    }

    if (typeof activity === "string") {
      return null;
    }

    const properties =
      activity?.properties || activity;

    return (
      properties?.rating ||
      activity?.rating ||
      null
    );
  };

  const getFee = (activity) => {
    if (!activity) {
      return null;
    }

    if (typeof activity === "string") {
      return null;
    }

    const properties =
      activity?.properties || activity;

    if (
      properties?.entrance_fee !== undefined &&
      properties?.entrance_fee !== null &&
      properties?.entrance_fee !== ""
    ) {
      return properties.entrance_fee;
    }

    if (
      activity?.entrance_fee !== undefined &&
      activity?.entrance_fee !== null &&
      activity?.entrance_fee !== ""
    ) {
      return activity.entrance_fee;
    }

    if (
      properties?.fee !== undefined &&
      properties?.fee !== null &&
      properties?.fee !== ""
    ) {
      return properties.fee;
    }

    if (
      activity?.fee !== undefined &&
      activity?.fee !== null &&
      activity?.fee !== ""
    ) {
      return activity.fee;
    }

    return null;
  };

  /* =====================================================
     PLACE ADDRESS
  ===================================================== */

  const getActivityAddress = (activity) => {
    if (!activity) {
      return destination;
    }

    if (typeof activity === "string") {
      return destination;
    }

    const properties =
      activity?.properties || activity;

    return (
      properties?.formatted ||
      properties?.address_line2 ||
      properties?.address_line1 ||
      activity?.address ||
      destination
    );
  };

  /* =====================================================
     RESTAURANTS
  ===================================================== */

  const getRestaurants = (day, meal) => {
    if (!day || !meal) {
      return [];
    }

    /*
      IMPORTANT:
      These are strings, not JavaScript variables.
      This fixes the previous syntax error:
      ${meal}_restaurants
    */

    const possibleKeys = [
      `${meal}_restaurants`,
      `${meal}Restaurants`,
      `${meal}_restaurant`,
      `${meal}Restaurant`,
      meal,
    ];

    for (const key of possibleKeys) {
      if (Array.isArray(day?.[key])) {
        return day[key];
      }
    }

    return [];
  };

  const getRestaurantName = (restaurant) => {
    if (!restaurant) {
      return "Restaurant";
    }

    const properties =
      restaurant?.properties ||
      restaurant;

    return (
      properties?.name ||
      restaurant?.name ||
      "Restaurant"
    );
  };

  const getRestaurantAddress = (
    restaurant
  ) => {
    if (!restaurant) {
      return destination;
    }

    const properties =
      restaurant?.properties ||
      restaurant;

    return (
      properties?.formatted ||
      properties?.address_line2 ||
      properties?.address_line1 ||
      restaurant?.address ||
      destination
    );
  };

  const getRestaurantRating = (
    restaurant
  ) => {
    if (!restaurant) {
      return null;
    }

    const properties =
      restaurant?.properties ||
      restaurant;

    return (
      properties?.rating ||
      restaurant?.rating ||
      null
    );
  };

  const getRestaurantType = (
    restaurant
  ) => {
    if (!restaurant) {
      return "RESTAURANT";
    }

    const properties =
      restaurant?.properties ||
      restaurant;

    if (
      Array.isArray(properties?.categories) &&
      properties.categories.length > 0
    ) {
      return String(
        properties.categories[0]
      )
        .split(".")
        .pop()
        .replaceAll("_", " ")
        .toUpperCase();
    }

    return (
      properties?.type ||
      restaurant?.type ||
      "RESTAURANT"
    );
  };

  /* =====================================================
     RESTAURANT SECTION
  ===================================================== */

  const MealSection = ({
    day,
    meal,
    title,
    icon,
  }) => {
    const restaurants =
      getRestaurants(day, meal);

    return (
      <div className="meal-section">

        <div className="meal-section-heading">

          <div className="meal-icon">
            {icon}
          </div>

          <div>
            <span>
              {meal.toUpperCase()}
            </span>

            <h4>
              {title}
            </h4>
          </div>

        </div>

        {restaurants.length > 0 ? (
          <div className="restaurant-list">

            {restaurants
              .slice(0, 3)
              .map(
                (
                  restaurant,
                  index
                ) => (

                  <div
                    className="restaurant-card"
                    key={`${getRestaurantName(
                      restaurant
                    )}-${index}`}
                  >

                    <div className="restaurant-card-icon">
                      🍽️
                    </div>

                    <div className="restaurant-card-content">

                      <span>
                        {getRestaurantType(
                          restaurant
                        )}
                      </span>

                      <h5>
                        {getRestaurantName(
                          restaurant
                        )}
                      </h5>

                      <p>
                        📍{" "}
                        {getRestaurantAddress(
                          restaurant
                        )}
                      </p>

                      {getRestaurantRating(
                        restaurant
                      ) && (
                        <small>
                          ★{" "}
                          {getRestaurantRating(
                            restaurant
                          )}
                        </small>
                      )}

                    </div>

                  </div>

                )
              )}

          </div>
        ) : (
          <div className="restaurant-empty">
            No {meal} restaurants found near your itinerary.
          </div>
        )}

      </div>
    );
  };

  /* =====================================================
     ITINERARY PLACE NAMES (FOR ZERO DUPLICATES)
  ===================================================== */

  const itineraryPlaceNames = useMemo(() => {
    const set = new Set();
    itinerary.forEach((day) => {
      ["morning", "afternoon", "evening", "activities"].forEach((slot) => {
        (day[slot] || []).forEach((item) => {
          const rawName =
            item?.name ||
            item?.properties?.name ||
            item?.title ||
            "";
          const norm = String(rawName).toLowerCase().trim();
          if (norm) {
            set.add(norm);
          }
        });
      });
    });
    return set;
  }, [itinerary]);

  /* =====================================================
     RECOMMENDED PLACES (STRICT UNIQUENESS & NO ACCOMMODATION)
  ===================================================== */

  const recommendedPlaces = useMemo(() => {
    const combined = [
      ...livePlaces,
      ...places,
    ];

    const unique = [];
    const names = new Set();

    const accommodationKeywords = [
      "hotel",
      "hostel",
      "lodge",
      "lodging",
      "resort",
      "motel",
      "guest house",
      "guesthouse",
      "homestay",
      "dormitory",
      "dorm",
      "stay",
      "inn",
      "accommodation",
      "pg",
    ];

    combined.forEach((place) => {
      const properties =
        place?.properties || place;

      const name =
        properties?.name ||
        place?.name ||
        place?.title;

      if (!name) {
        return;
      }

      const normalized =
        String(name)
          .toLowerCase()
          .trim();

      // Filter out places already in the scheduled itinerary
      if (itineraryPlaceNames.has(normalized)) {
        return;
      }

      if (names.has(normalized)) {
        return;
      }

      // Filter out accommodations
      const catStr = Array.isArray(properties?.categories)
        ? properties.categories.join(" ").toLowerCase()
        : String(properties?.categories || "").toLowerCase();
      const typeStr = String(
        properties?.type || place?.type || ""
      ).toLowerCase();

      const isAcc = accommodationKeywords.some((kw) => {
        const regex = new RegExp(`\\b${kw}\\b`, "i");
        return (
          regex.test(normalized) ||
          regex.test(catStr) ||
          regex.test(typeStr)
        );
      });

      if (isAcc) {
        return;
      }

      names.add(normalized);
      unique.push(place);
    });

    return unique;
  }, [livePlaces, places, itineraryPlaceNames]);

  /* =====================================================
     FORMAT DATE
  ===================================================== */

  const formatDate = (date) => {
    if (!date) {
      return "Not specified";
    }

    const parsed = new Date(date);

    if (Number.isNaN(parsed.getTime())) {
      return date;
    }

    return parsed.toLocaleDateString(
      "en-IN",
      {
        day: "numeric",
        month: "short",
        year: "numeric",
      }
    );
  };

  /* =====================================================
     FORMAT BUDGET
  ===================================================== */

  const formatBudget = (value) => {
    if (!value) {
      return "₹0";
    }

    const numericValue =
      Number(value);

    if (Number.isNaN(numericValue)) {
      return `₹${value}`;
    }

    return `₹${numericValue.toLocaleString(
      "en-IN"
    )}`;
  };

  /* =====================================================
     PLACE DATA
  ===================================================== */

  const getPlaceProperties = (
    place
  ) => {
    return (
      place?.properties ||
      place ||
      {}
    );
  };

  const getPlaceName = (place) => {
    const p =
      getPlaceProperties(place);

    return (
      p.name ||
      place?.name ||
      place?.title ||
      "Tourist Attraction"
    );
  };

  const getPlaceType = (place) => {
    const p =
      getPlaceProperties(place);

    if (
      Array.isArray(p.categories) &&
      p.categories.length > 0
    ) {
      return String(
        p.categories[0]
      )
        .split(".")
        .pop();
    }

    return (
      p.type ||
      place?.type ||
      "ATTRACTION"
    );
  };

  const getPlaceRating = (
    place
  ) => {
    const p =
      getPlaceProperties(place);

    return (
      p.rating ||
      place?.rating ||
      null
    );
  };

  const getPlaceAddress = (
    place
  ) => {
    const p =
      getPlaceProperties(place);

    return (
      p.address_line2 ||
      p.address_line1 ||
      p.formatted ||
      place?.address ||
      destination
    );
  };

  /* =====================================================
     WEATHER
  ===================================================== */

  const getWeatherText = () => {
    if (!weather) {
      return null;
    }

    return (
      weather.description ||
      weather.weather ||
      weather.condition ||
      weather.message ||
      null
    );
  };

  /* =====================================================
     NO TRIP
  ===================================================== */

  if (!tripData) {
    return (
      <main className="results-empty">

        <div className="results-empty-icon">
          ✈
        </div>

        <h1>
          No trip found
        </h1>

        <p>
          Create a trip first and your
          AI-generated itinerary will
          appear here.
        </p>

        <Link
          to="/plan"
          className="results-primary-btn"
        >
          Plan a Trip →
        </Link>

      </main>
    );
  }

  /* =====================================================
     RENDER
  ===================================================== */

  return (
    <main className="results-page">

      {/* =================================================
          HERO
      ================================================= */}

      <section className="results-hero">

        <div className="results-breadcrumb">

          <Link to="/">
            Home
          </Link>

          <span>
            ›
          </span>

          <Link to="/plan">
            Plan Trip
          </Link>

          <span>
            ›
          </span>

          <strong>
            My Trip
          </strong>

        </div>

        <div className="results-hero-content">

          <div>

            <div className="results-ai-label">
              ✦ AI GENERATED TRIP
            </div>

            <h1>
              Your trip to{" "}
              <span>
                {destination}
              </span>
            </h1>

            <p>
              Your personalized itinerary
              is ready. Explore each day,
              discover recommended places
              and adapt your trip whenever
              plans change.
            </p>

            <div className="results-route">

              <strong>
                {origin}
              </strong>

              <span>
                →
              </span>

              <strong>
                {destination}
              </strong>

            </div>

          </div>

          <button
            className="results-edit-btn"
            onClick={() =>
              navigate("/plan")
            }
          >
            ✎ Edit Trip
          </button>

        </div>

      </section>


      {/* =================================================
          SUMMARY
      ================================================= */}

      <section className="trip-summary">

        <div className="summary-item">

          <span>
            DATES
          </span>

          <strong>
            {formatDate(startDate)}
          </strong>

          <small>
            to {formatDate(endDate)}
          </small>

        </div>


        <div className="summary-item">

          <span>
            TRAVELLERS
          </span>

          <strong>
            {travelers}
          </strong>

          <small>
            {travelers === 1
              ? "Traveller"
              : "Travellers"}
          </small>

        </div>


        <div className="summary-item">

          <span>
            BUDGET
          </span>

          <strong>
            {formatBudget(budget)}
          </strong>

          <small>
            Estimated trip budget
          </small>

        </div>


        <div className="summary-item">

          <span>
            TRIP DAYS
          </span>

          <strong>
            {days.length || "—"}
          </strong>

          <small>
            AI planned days
          </small>

        </div>

      </section>


      {/* =================================================
          WEATHER
      ================================================= */}

      {getWeatherText() && (
        <section className="trip-weather">

          <div>
            🌤️
          </div>

          <div>

            <span>
              DESTINATION WEATHER
            </span>

            <strong>
              {getWeatherText()}
            </strong>

          </div>

        </section>
      )}


      {/* =================================================
          AI INSIGHT
      ================================================= */}

      <section className="ai-trip-insight">

        <div className="insight-icon">
          ✦
        </div>

        <div>

          <span>
            AI TRAVEL INSIGHT
          </span>

          <h3>
            Your itinerary is personalized
            around your trip
          </h3>

          <p>
            Your AI planner selected real
            destination places based on
            your interests and arranged
            them across morning, afternoon
            and evening.
          </p>

        </div>

      </section>


      {/* =================================================
          DAY BY DAY
      ================================================= */}

      <section className="results-section">

        <div className="results-section-heading">

          <div>

            <span className="section-eyebrow">
              YOUR JOURNEY
            </span>

            <h2>
              Day-by-Day Itinerary
            </h2>

            <p>
              See exactly where to go during
              each part of your day.
            </p>

          </div>

        </div>


        {/* =================================================
            DAY BUTTONS
        ================================================= */}

        {days.length > 0 && (

          <div className="day-tabs">

            {days.map((day) => (

              <button
                key={day.dayNumber}
                className={
                  activeDay === day.dayNumber
                    ? "day-tab active"
                    : "day-tab"
                }
                onClick={() =>
                  setActiveDay(
                    day.dayNumber
                  )
                }
              >

                <small>
                  DAY
                </small>

                <strong>
                  {day.dayNumber}
                </strong>

              </button>

            ))}

          </div>

        )}


        {/* =================================================
            CURRENT DAY
        ================================================= */}

        {currentDay ? (

          <div className="day-plan-card">

            <div className="day-plan-heading">

              <div>

                <span>
                  DAY {currentDay.dayNumber}
                </span>

                <h3>
                  {currentDay.title ||
                    currentDay.theme ||
                    `Exploring ${destination}`}
                </h3>

              </div>

              <div className="ai-planned-badge">
                ✦ AI Planned
              </div>

            </div>


            {currentDay.description && (

              <p className="day-description">
                {currentDay.description}
              </p>

            )}


            {/* =================================================
                MORNING / AFTERNOON / EVENING
            ================================================= */}

            <div className="day-time-grid">

              {timeSlots.map(
                (slot) => {

                  const activities =
                    getActivitiesForSlot(
                      currentDay,
                      slot.key
                    );

                  return (

                    <div
                      className="time-slot-card"
                      key={slot.key}
                    >

                      <div className="time-slot-top">

                        <div className="time-slot-icon">
                          {slot.icon}
                        </div>

                        <div>

                          <span>
                            {slot.label}
                          </span>

                          <small>
                            {slot.key ===
                            "morning"
                              ? "Start your day"
                              : slot.key ===
                                "afternoon"
                              ? "Explore & experience"
                              : "Relax & enjoy"}
                          </small>

                        </div>

                      </div>


                      <div className="time-slot-body">

                        {activities.length >
                        0 ? (

                          <div className="activity-list">

                            {activities
                              .map(
                                (
                                  activity,
                                  index
                                ) => (

                                  <div
                                    className="activity-item"
                                    key={`${getName(
                                      activity
                                    )}-${index}`}
                                  >

                                    <span className="activity-category">
                                      {getType(
                                        activity
                                      )}
                                    </span>

                                    <h4>
                                      {getName(
                                        activity
                                      )}
                                    </h4>

                                    <p>
                                      {getDescription(
                                        activity
                                      )}
                                    </p>

                                    <p className="activity-address">
                                      📍{" "}
                                      {getActivityAddress(
                                        activity
                                      )}
                                    </p>

                                    <div className="activity-meta">

                                      {getRating(
                                        activity
                                      ) && (

                                        <span>
                                          ★{" "}
                                          {getRating(
                                            activity
                                          )}
                                        </span>

                                      )}

                                      {getFee(
                                        activity
                                      ) !== null && (

                                        <span>
                                          ₹{" "}
                                          {getFee(
                                            activity
                                          )}
                                        </span>

                                      )}

                                    </div>

                                  </div>

                                )
                              )}

                          </div>

                        ) : (

                          <div className="activity-empty">

                            <span className="activity-category">
                              FREE TIME
                            </span>

                            <h4>
                              Explore nearby
                            </h4>

                            <p>
                              No verified place was
                              returned for this time
                              period.
                            </p>

                          </div>

                        )}

                      </div>


                      <div className="time-slot-suggestion">

                        <strong>
                          AI suggestion
                        </strong>

                        <p>
                          {slot.key ===
                          "morning"
                            ? "Start early to avoid crowds and make the most of your morning."
                            : slot.key ===
                              "afternoon"
                            ? "Keep enough time for nearby attractions and a local lunch experience."
                            : "End the day comfortably and explore local food or evening attractions."}
                        </p>

                      </div>

                    </div>

                  );
                }
              )}

            </div>


            {/* =================================================
                MEALS
            ================================================= */}

            <div className="meals-container">

              <div className="meals-heading">

                <span className="section-eyebrow">
                  FOOD
                </span>

                <h3>
                  Recommended Restaurants
                </h3>

                <p>
                  Restaurants selected near your
                  planned activities.
                </p>

              </div>


              <div className="meal-grid">

                <MealSection
                  day={currentDay}
                  meal="breakfast"
                  title="Breakfast"
                  icon="☕"
                />

                <MealSection
                  day={currentDay}
                  meal="lunch"
                  title="Lunch"
                  icon="🍛"
                />

                <MealSection
                  day={currentDay}
                  meal="dinner"
                  title="Dinner"
                  icon="🍽️"
                />

              </div>

            </div>

          </div>

        ) : (

          <div className="day-plan-card">

            <div className="activity-empty">

              <h3>
                No itinerary returned
              </h3>

              <p>
                The backend did not return
                any planned days. Please
                generate the trip again.
              </p>

            </div>

          </div>

        )}

      </section>


      {/* =================================================
          LIVE ROUTE
      ================================================= */}

      <section className="results-section">

        <div className="results-section-heading">

          <div>

            <span className="section-eyebrow">
              YOUR JOURNEY
            </span>

            <h2>
              Travel Route
            </h2>

            <p>
              Route from {origin} to{" "}
              {destination}.
            </p>

          </div>

          <div className="live-route-badge">
            ● LIVE ROUTE
          </div>

        </div>


        <div className="route-map-card">

          {routeImage ? (

            <img
              src={routeImage}
              alt={`Route from ${origin} to ${destination}`}
              className="route-map-image"
            />

          ) : (

            <div className="route-loading">

              <div className="route-loading-icon">
                🗺️
              </div>

              <h3>
                {routeLoading
                  ? "Loading travel route..."
                  : "Route unavailable"}
              </h3>

              <p>
                {routeLoading
                  ? `Fetching the route between ${origin} and ${destination}.`
                  : "The live route could not be loaded right now."}
              </p>

            </div>

          )}


          <div className="route-overlay-card">

            <span>
              ROUTE
            </span>

            <strong>
              {origin}
            </strong>

            <div>
              ↓
            </div>

            <strong>
              {destination}
            </strong>

            {transport.duration && (

              <small>
                Estimated travel time:{" "}
                {transport.duration}
              </small>

            )}

            {transport.distance_km && (

              <small>
                Distance:{" "}
                {transport.distance_km} km
              </small>

            )}

          </div>

        </div>

      </section>


      {/* =================================================
          RECOMMENDED PLACES
      ================================================= */}

      <section className="results-section places-section">

        <div className="results-section-heading">

          <div>

            <span className="section-eyebrow">
              DISCOVER
            </span>

            <h2>
              Recommended Places
            </h2>

            <p>
              Explore more places around{" "}
              {destination}.
            </p>

          </div>

          <Link
            to="/explore"
            className="section-view-link"
          >
            View All →
          </Link>

        </div>


        <div className="places-slider-wrapper">

          {loadingPlaces ? (

            <div className="places-loading">
              Finding places around{" "}
              {destination}...
            </div>

          ) : recommendedPlaces.length >
            0 ? (

            <div className="places-horizontal-slider">

              {recommendedPlaces.map(
                (place, index) => {

                  const name =
                    getPlaceName(place);

                  const type =
                    getPlaceType(place);

                  const rating =
                    getPlaceRating(place);

                  const address =
                    getPlaceAddress(place);

                  return (

                    <article
                      className="place-slide-card"
                      key={`${name}-${index}`}
                    >

                      <div className="place-slide-image">

                        <div className="place-image-placeholder">
                          {index % 4 === 0
                            ? "🌴"
                            : index % 4 === 1
                            ? "🏛️"
                            : index % 4 === 2
                            ? "🌄"
                            : "🏖️"}
                        </div>

                        {rating && (

                          <div className="place-rating">
                            ★ {rating}
                          </div>

                        )}

                      </div>


                      <div className="place-slide-content">

                        <span>
                          {String(type)
                            .replaceAll(
                              "_",
                              " "
                            )
                            .toUpperCase()}
                        </span>

                        <h3>
                          {name}
                        </h3>

                        <p>
                          📍 {address}
                        </p>

                        <button
                          onClick={() =>
                            navigate(
                              `/destination/${encodeURIComponent(
                                name
                              )}`
                            )
                          }
                        >
                          View Details →
                        </button>

                      </div>

                    </article>

                  );
                }
              )}

            </div>

          ) : (

            <div className="places-empty">
              No additional places were found.
            </div>

          )}

        </div>

      </section>


      {/* =================================================
          HOTELS
      ================================================= */}

      {hotels.length > 0 && (

        <section className="results-section">

          <div className="results-section-heading">

            <div>

              <span className="section-eyebrow">
                STAY
              </span>

              <h2>
                Recommended Hotels
              </h2>

              <p>
                Accommodation options for
                your trip.
              </p>

            </div>

          </div>


          <div className="hotel-grid">

            {hotels
              .slice(0, 8)
              .map(
                (hotel, index) => (

                  <div
                    className="hotel-card"
                    key={index}
                  >

                    <div className="hotel-image">

                      <div className="hotel-placeholder">
                        🏨
                      </div>

                    </div>


                    <div className="hotel-content">

                      <div className="hotel-rating">
                        {hotel.rating
                          ? `★ ${hotel.rating}`
                          : "Recommended"}
                      </div>

                      <h3>
                        {hotel.hotel_name ||
                          hotel.name ||
                          "Recommended Hotel"}
                      </h3>

                      <p>
                        {hotel.description ||
                          "Comfortable accommodation selected for your trip."}
                      </p>

                      {hotel.place && (

                        <small>
                          📍 {hotel.place}
                        </small>

                      )}

                    </div>

                  </div>

                )
              )}

          </div>

        </section>

      )}


      {/* =================================================
          REPLAN
      ================================================= */}

      <section className="replanning-banner">

        <div className="replanning-icon">
          ✦
        </div>

        <div className="replanning-content">

          <span>
            AI TRIP ADAPTATION
          </span>

          <h2>
            Something changed during your trip?
          </h2>

          <p>
            Weather changed? An attraction
            closed? Transport delayed? Let
            AI update your itinerary while
            preserving your approved plans.
          </p>

        </div>

        <button
          className="replanning-button"
          onClick={() =>
            navigate("/replanning")
          }
        >
          Replan with AI
          <span>
            →
          </span>
        </button>

      </section>


      {/* =================================================
          ACTIONS
      ================================================= */}

      <section className="results-actions">

        <button
          className="secondary-result-btn"
          onClick={() =>
            navigate("/plan")
          }
        >
          ← Modify Trip
        </button>

        <Link
          to="/explore"
          className="primary-result-btn"
        >
          Explore Destination →
        </Link>

      </section>

    </main>
  );
}

export default Results;