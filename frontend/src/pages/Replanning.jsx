import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_URL = "http://127.0.0.1:8000";

function Replanning() {
  const navigate = useNavigate();

  const [trip, setTrip] = useState(null);
  const [eventType, setEventType] = useState("weather");
  const [eventDescription, setEventDescription] = useState(
    "Heavy rain is expected during the planned outdoor activities."
  );

  const [approvedActivities, setApprovedActivities] = useState([]);
  const [updatedItinerary, setUpdatedItinerary] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const storedTrip =
      sessionStorage.getItem("aiTripResult") ||
      localStorage.getItem("tripPlan");

    if (!storedTrip) {
      return;
    }

    try {
      const parsed = JSON.parse(storedTrip);
      setTrip(parsed);
    } catch (err) {
      console.error("Unable to read trip data", err);
    }
  }, []);

  const itinerary = useMemo(() => {
    if (!trip) return [];

    return (
      trip?.itinerary ||
      trip?.trip?.itinerary ||
      trip?.data?.itinerary ||
      []
    );
  }, [trip]);

  const tripInfo = trip?.trip || trip || {};

  const destination =
    tripInfo.destination ||
    trip?.destination ||
    "Your destination";

  const travelers =
    tripInfo.travelers ||
    trip?.travelers ||
    1;

  const budget =
    tripInfo.budget ||
    trip?.budget ||
    0;

  const interests =
    tripInfo.interests ||
    trip?.interests ||
    [];

  function getActivityName(activity) {
    return (
      activity?.name ||
      activity?.title ||
      activity?.place ||
      activity?.location ||
      "Travel activity"
    );
  }

  function getDayActivities(day) {
    return day?.activities || day?.places || [];
  }

  function toggleApproval(activityName) {
    setApprovedActivities((previous) => {
      if (previous.includes(activityName)) {
        return previous.filter(
          (item) => item !== activityName
        );
      }

      return [...previous, activityName];
    });
  }

  function selectEvent(type, description) {
    setEventType(type);
    setEventDescription(description);
  }

  async function runReplanning() {
    setError("");

    if (!destination || destination === "Your destination") {
      setError("Trip destination is missing.");
      return;
    }

    if (!itinerary.length) {
      setError(
        "No itinerary was found. Please create a trip first."
      );
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        `${API_URL}/api/trips/replan`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            destination,
            event_type: eventType,
            event_description: eventDescription,
            itinerary,
            approved_activities: approvedActivities,
            travelers,
            budget,
            interests,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Unable to replan the itinerary."
        );
      }

      setUpdatedItinerary(data);

      localStorage.setItem(
        "tripPlan",
        JSON.stringify({
          ...trip,
          itinerary: data.itinerary,
          replanning: data,
        })
      );
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Something went wrong while replanning."
      );
    } finally {
      setLoading(false);
    }
  }

  function goToResults() {
    if (updatedItinerary?.itinerary) {
      const updatedTrip = {
        ...trip,
        itinerary: updatedItinerary.itinerary,
        replanning: updatedItinerary,
      };

      sessionStorage.setItem(
        "aiTripResult",
        JSON.stringify(updatedTrip)
      );
    }

    navigate("/results");
  }

  return (
    <main className="replanning-page">

      {/* HERO */}
      <section className="replanning-hero">

        <div>
          <span className="replanning-eyebrow">
            AI DYNAMIC TRAVEL
          </span>

          <h1>
            Your trip changed.
            <br />
            <span>Let AI adapt it.</span>
          </h1>

          <p>
            Weather, attraction closures and transport
            disruptions shouldn't ruin your trip. Our AI
            replanning engine adjusts affected activities
            while preserving the plans you have already approved.
          </p>
        </div>

        <div className="replanning-status-card">

          <div className="status-icon">
            ✨
          </div>

          <div>
            <small>AI TRAVEL ENGINE</small>

            <strong>
              Dynamic Replanning
            </strong>

            <span>
              Ready to adapt your itinerary
            </span>
          </div>

          <div className="status-dot" />
        </div>

      </section>

      {/* TRIP SUMMARY */}
      <section className="replanning-summary">

        <div className="summary-item">
          <span>DESTINATION</span>
          <strong>{destination}</strong>
        </div>

        <div className="summary-item">
          <span>TRAVELERS</span>
          <strong>{travelers}</strong>
        </div>

        <div className="summary-item">
          <span>BUDGET</span>
          <strong>
            ₹{Number(budget).toLocaleString("en-IN")}
          </strong>
        </div>

        <div className="summary-item">
          <span>INTERESTS</span>
          <strong>
            {interests.length
              ? interests.slice(0, 3).join(", ")
              : "Personalized"}
          </strong>
        </div>

      </section>

      {/* MAIN */}
      <section className="replanning-layout">

        {/* LEFT */}
        <div className="replanning-main">

          <div className="replanning-section-heading">
            <div>
              <span className="eyebrow">
                LIVE TRAVEL EVENT
              </span>

              <h2>
                What changed?
              </h2>

              <p>
                Tell the AI what happened and it will
                determine which activities need to change.
              </p>
            </div>
          </div>

          {/* EVENT CARDS */}
          <div className="event-grid">

            <button
              className={`event-card ${
                eventType === "weather"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                selectEvent(
                  "weather",
                  "Heavy rain is expected during the planned outdoor activities."
                )
              }
            >
              <span className="event-icon">
                ☁
              </span>

              <div>
                <strong>
                  Weather Change
                </strong>

                <p>
                  Rain, heat, storms or unfavorable weather.
                </p>
              </div>

              <span className="event-check">
                {eventType === "weather"
                  ? "✓"
                  : ""}
              </span>
            </button>

            <button
              className={`event-card ${
                eventType === "attraction_closure"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                selectEvent(
                  "attraction_closure",
                  "One of the planned attractions is temporarily closed."
                )
              }
            >
              <span className="event-icon">
                ⚠
              </span>

              <div>
                <strong>
                  Attraction Closure
                </strong>

                <p>
                  A planned destination is unavailable.
                </p>
              </div>

              <span className="event-check">
                {eventType === "attraction_closure"
                  ? "✓"
                  : ""}
              </span>
            </button>

            <button
              className={`event-card ${
                eventType === "transport_delay"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                selectEvent(
                  "transport_delay",
                  "A transportation delay is affecting the planned route."
                )
              }
            >
              <span className="event-icon">
                🚆
              </span>

              <div>
                <strong>
                  Transport Delay
                </strong>

                <p>
                  Delays, route disruption or traffic.
                </p>
              </div>

              <span className="event-check">
                {eventType === "transport_delay"
                  ? "✓"
                  : ""}
              </span>
            </button>

          </div>

          {/* EVENT DESCRIPTION */}
          <div className="event-description-card">

            <label>
              EVENT DETAILS
            </label>

            <textarea
              value={eventDescription}
              onChange={(event) =>
                setEventDescription(
                  event.target.value
                )
              }
              placeholder="Describe what happened..."
              rows={4}
            />

          </div>

          {/* CURRENT ITINERARY */}
          <div className="current-itinerary">

            <div className="itinerary-heading">

              <div>
                <span className="eyebrow">
                  YOUR CURRENT PLAN
                </span>

                <h2>
                  Protect what matters
                </h2>

                <p>
                  Select activities you have already approved.
                  AI will avoid replacing them.
                </p>
              </div>

              <span className="approved-count">
                {approvedActivities.length} approved
              </span>

            </div>

            {itinerary.length === 0 ? (
              <div className="empty-itinerary">
                <span>📋</span>

                <h3>
                  No itinerary available
                </h3>

                <p>
                  Create a trip first to use dynamic replanning.
                </p>
              </div>
            ) : (
              <div className="replan-days">

                {itinerary.map((day, dayIndex) => {

                  const activities =
                    getDayActivities(day);

                  return (
                    <div
                      className="replan-day"
                      key={dayIndex}
                    >

                      <div className="replan-day-title">
                        <span>
                          DAY {day?.day || dayIndex + 1}
                        </span>

                        <strong>
                          {day?.title ||
                            `Day ${dayIndex + 1}`}
                        </strong>
                      </div>

                      <div className="replan-activities">

                        {activities.map(
                          (activity, activityIndex) => {

                            const name =
                              getActivityName(
                                activity
                              );

                            const approved =
                              approvedActivities.includes(
                                name
                              );

                            return (
                              <button
                                key={activityIndex}
                                className={`replan-activity ${
                                  approved
                                    ? "approved"
                                    : ""
                                }`}
                                onClick={() =>
                                  toggleApproval(name)
                                }
                              >

                                <span className="activity-number">
                                  {activityIndex + 1}
                                </span>

                                <div>
                                  <strong>
                                    {name}
                                  </strong>

                                  <small>
                                    {activity?.type ||
                                      activity?.significance ||
                                      "Travel activity"}
                                  </small>
                                </div>

                                <span className="approval-mark">
                                  {approved
                                    ? "✓"
                                    : "○"}
                                </span>

                              </button>
                            );
                          }
                        )}

                      </div>

                    </div>
                  );
                })}

              </div>
            )}

          </div>

          {/* ERROR */}
          {error && (
            <div className="replan-error">
              <strong>
                Unable to replan
              </strong>

              <span>
                {error}
              </span>
            </div>
          )}

          {/* ACTION */}
          <button
            className="run-replan-btn"
            onClick={runReplanning}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner" />
                AI is rebuilding your itinerary...
              </>
            ) : (
              <>
                ✨
                Run AI Replanning
                <span>→</span>
              </>
            )}
          </button>

        </div>

        {/* RIGHT SIDEBAR */}
        <aside className="replanning-sidebar">

          <div className="ai-monitor-card">

            <div className="monitor-top">

              <div className="monitor-icon">
                ✨
              </div>

              <div>
                <small>AI MONITOR</small>
                <strong>
                  Travel Intelligence
                </strong>
              </div>

              <span className="monitor-live">
                LIVE
              </span>

            </div>

            <div className="monitor-line">
              <span />
            </div>

            <div className="monitor-item">
              <span>✓</span>
              <div>
                <strong>
                  Destination
                </strong>
                <p>
                  {destination}
                </p>
              </div>
            </div>

            <div className="monitor-item">
              <span>✓</span>
              <div>
                <strong>
                  Preferences
                </strong>
                <p>
                  {interests.length
                    ? "Loaded"
                    : "Personalized"}
                </p>
              </div>
            </div>

            <div className="monitor-item">
              <span>✓</span>
              <div>
                <strong>
                  Approved activities
                </strong>
                <p>
                  {approvedActivities.length} protected
                </p>
              </div>
            </div>

          </div>

          <div className="preserve-card">

            <span className="preserve-icon">
              🛡
            </span>

            <h3>
              Your choices stay protected
            </h3>

            <p>
              Activities you approve will be preserved
              wherever possible. The AI only changes
              activities affected by the travel event.
            </p>

          </div>

          <div className="flow-card">

            <span className="eyebrow">
              HOW IT WORKS
            </span>

            <h3>
              Adaptive planning
            </h3>

            <div className="flow-step">
              <span>01</span>
              <div>
                <strong>
                  Detect
                </strong>
                <p>
                  Identify the travel disruption.
                </p>
              </div>
            </div>

            <div className="flow-step">
              <span>02</span>
              <div>
                <strong>
                  Protect
                </strong>
                <p>
                  Preserve approved activities.
                </p>
              </div>
            </div>

            <div className="flow-step">
              <span>03</span>
              <div>
                <strong>
                  Replan
                </strong>
                <p>
                  Find suitable alternatives.
                </p>
              </div>
            </div>

          </div>

        </aside>

      </section>

      {/* RESULT */}
      {updatedItinerary && (
        <section className="replanning-result">

          <div className="result-heading">

            <div>
              <span className="eyebrow">
                AI RESULT
              </span>

              <h2>
                Your itinerary has been adapted
              </h2>

              <p>
                The AI updated the affected activities
                while keeping your approved choices protected.
              </p>
            </div>

            <div className="result-success">
              ✓
              Successfully replanned
            </div>

          </div>

          <div className="result-stats">

            <div>
              <span>PRESERVED</span>
              <strong>
                {updatedItinerary
                  ?.preserved_approved_activities ??
                  updatedItinerary
                    ?.preserved_constraints
                    ?.approved_activities
                    ?.length ??
                  0}
              </strong>
            </div>

            <div>
              <span>REPLACED</span>
              <strong>
                {updatedItinerary
                  ?.replanning
                  ?.replaced_activities ??
                  updatedItinerary
                    ?.replaced_activities ??
                  0}
              </strong>
            </div>

            <div>
              <span>EVENT</span>
              <strong>
                {updatedItinerary?.event?.type ||
                  eventType}
              </strong>
            </div>

          </div>

          <div className="updated-days">

            {(updatedItinerary.itinerary || []).map(
              (day, index) => {

                const activities =
                  day?.activities ||
                  day?.places ||
                  [];

                return (
                  <div
                    className="updated-day"
                    key={index}
                  >

                    <div className="updated-day-head">
                      <span>
                        DAY {day?.day || index + 1}
                      </span>

                      <strong>
                        {day?.title ||
                          `Day ${index + 1}`}
                      </strong>
                    </div>

                    <div className="updated-activity-list">

                      {activities.length > 0 ? (
                        activities.map(
                          (activity, activityIndex) => {

                            const name =
                              getActivityName(
                                activity
                              );

                            return (
                              <div
                                className="updated-activity"
                                key={activityIndex}
                              >

                                <span>
                                  {activity?.status ===
                                  "Preserved"
                                    ? "✓"
                                    : "↻"}
                                </span>

                                <div>
                                  <strong>
                                    {name}
                                  </strong>

                                  <p>
                                    {activity?.adaptation_reason ||
                                      activity?.description ||
                                      activity?.type ||
                                      "Updated by AI"}
                                  </p>
                                </div>

                                <small
                                  className={
                                    activity?.status ===
                                    "Preserved"
                                      ? "preserved"
                                      : "replanned"
                                  }
                                >
                                  {activity?.status ||
                                    "AI Replanned"}
                                </small>

                              </div>
                            );
                          }
                        )
                      ) : (
                        <div className="updated-activity">
                          <span>↻</span>

                          <div>
                            <strong>
                              {day?.title ||
                                "Updated activity"}
                            </strong>

                            <p>
                              {day?.description ||
                                "AI adapted this part of the itinerary."}
                            </p>
                          </div>

                          <small className="replanned">
                            AI Replanned
                          </small>
                        </div>
                      )}

                    </div>

                  </div>
                );
              }
            )}

          </div>

          <div className="result-actions">

            <button
              className="secondary-action"
              onClick={() =>
                setUpdatedItinerary(null)
              }
            >
              ← Review Again
            </button>

            <button
              className="primary-action"
              onClick={goToResults}
            >
              Continue to My Trip →
            </button>

          </div>

        </section>
      )}

    </main>
  );
}

export default Replanning;