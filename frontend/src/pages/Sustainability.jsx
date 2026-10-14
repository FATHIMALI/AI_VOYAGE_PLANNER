import { useNavigate } from "react-router-dom";
import "../App.css";
import React from "react";
import { Link } from "react-router-dom";
import "./Sustainability.css";

function Sustainability() {
  const navigate = useNavigate();

  const trip = JSON.parse(
    localStorage.getItem("tripPlan") || "null"
  );

  if (!trip) {
    return (
      <div className="sustainability-empty">
        <div className="sustainability-empty-card">
          <div className="sustainability-empty-icon">♻</div>

          <h1>No Trip Data</h1>

          <p>
            Create a journey first to see its sustainability
            analysis.
          </p>

          <button
            className="primary-action-button"
            onClick={() => navigate("/plan")}
          >
            Create My Journey →
          </button>
        </div>
      </div>
    );
  }

  const score = Math.round(
    Number(trip.sustainability_score ?? 0)
  );

  const carbonScore = Math.round(
    Number(trip.carbon_score ?? 0)
  );

  const transportScore = Math.round(
    Number(trip.transport_score ?? 0)
  );

  const distanceScore = Math.round(
    Number(trip.distance_score ?? 0)
  );

  const localScore = Math.round(
    Number(trip.local_exploration_score ?? 0)
  );

  const emissions = Number(
    trip.estimated_emissions_kg || 0
  );

  const perTraveler = Number(
    trip.emissions_per_traveler_kg || 0
  );

  const distance = Number(
    trip.distance_km || 0
  );

  const sustainabilityLevel =
    trip.sustainability_level || "Moderate";

  return (
    <div className="sustainability-page">

      {/* HERO */}

      <section className="sustainability-hero">

        <div className="sustainability-hero-content">

          <span className="section-badge">
            AI SUSTAINABILITY CENTER
          </span>

          <h1>
            Travel Better.
            <br />
            Leave Less Behind.
          </h1>

          <p>
            AI-powered analysis of the environmental impact
            of your journey.
          </p>

          <div className="sustainability-route">
            <strong>{trip.origin}</strong>

            <span>→</span>

            <strong>{trip.destination}</strong>
          </div>

        </div>

      </section>


      {/* SCORE */}

      <section className="sustainability-main">

        <div className="results-container">

          <div className="sustainability-score-layout">

            <div className="sustainability-score-card">

              <div className="score-card-heading">

                <div>
                  <span className="section-kicker">
                    OVERALL IMPACT
                  </span>

                  <h2>
                    Sustainability Score
                  </h2>
                </div>

                <span className="score-level">
                  {sustainabilityLevel}
                </span>

              </div>


              <div className="large-score">

                <div
                  className="large-score-circle"
                  style={{
                    "--score": `${score}%`,
                  }}
                >
                  <div className="large-score-inner">

                    <strong>
                      {score}
                    </strong>

                    <span>
                      /100
                    </span>

                  </div>
                </div>

              </div>


              <p className="score-explanation">

                {trip.sustainability_explanation ||
                  "Your sustainability score is calculated using carbon emissions, transport choice, travel distance and local exploration."}

              </p>

            </div>


            {/* SCORE BREAKDOWN */}

            <div className="score-breakdown-card">

              <span className="section-kicker">
                SCORE BREAKDOWN
              </span>

              <h2>
                What influenced your score?
              </h2>

              <ScoreRow
                name="Carbon Impact"
                score={carbonScore}
                max={40}
                icon="CO₂"
              />

              <ScoreRow
                name="Transport"
                score={transportScore}
                max={25}
                icon="↗"
              />

              <ScoreRow
                name="Travel Distance"
                score={distanceScore}
                max={20}
                icon="⌁"
              />

              <ScoreRow
                name="Local Exploration"
                score={localScore}
                max={15}
                icon="◎"
              />

            </div>

          </div>


          {/* METRICS */}

          <section className="sustainability-metrics">

            <div className="sustainability-section-title">

              <span className="section-kicker">
                ENVIRONMENTAL METRICS
              </span>

              <h2>
                Understand Your Journey
              </h2>

            </div>


            <div className="sustainability-metric-grid">

              <MetricCard
                icon="CO₂"
                value={`${formatNumber(emissions, 1)} kg`}
                label="Estimated CO₂"
                description="Estimated emissions for the selected journey."
              />

              <MetricCard
                icon="◉"
                value={`${formatNumber(
                  perTraveler,
                  1
                )} kg`}
                label="CO₂ / Traveler"
                description="Estimated emissions distributed across travelers."
              />

              <MetricCard
                icon="⌁"
                value={`${formatNumber(
                  distance
                )} km`}
                label="Travel Distance"
                description="Estimated route distance used for the calculation."
              />

              <MetricCard
                icon="↗"
                value={
                  trip.recommended_transport ||
                  "Optimized route"
                }
                label="Transport"
                description="Transport mode used by the route engine."
              />

            </div>

          </section>


          {/* CARBON COMPARISON */}

          <section className="carbon-comparison-section">

            <div className="sustainability-section-title">

              <span className="section-kicker">
                CARBON COMPARISON
              </span>

              <h2>
                How Different Transport Choices Compare
              </h2>

              <p>
                A simplified project-level comparison showing
                how transport choices can affect estimated emissions.
              </p>

            </div>


            <div className="carbon-comparison-card">

              <CarbonBar
                label="Air Travel"
                value={Math.round(emissions * 1.8)}
                current={false}
              />

              <CarbonBar
                label="Driving"
                value={Math.round(emissions)}
                current={
                  /driving|car/i.test(
                    trip.recommended_transport || ""
                  )
                }
              />

              <CarbonBar
                label="Rail / Lower Impact"
                value={Math.round(emissions * 0.35)}
                current={false}
              />

            </div>

          </section>


          {/* AI RECOMMENDATIONS */}

          <section className="sustainability-recommendations">

            <div className="sustainability-section-title">

              <span className="section-kicker">
                AI RECOMMENDATIONS
              </span>

              <h2>
                Make This Journey Greener
              </h2>

            </div>


            <div className="recommendation-grid">

              <Recommendation
                number="01"
                title="Choose Lower-Impact Transport"
                text={
                  trip.local_transport_tip ||
                  "Use public transport, walking, cycling or shared transport whenever practical."
                }
              />

              <Recommendation
                number="02"
                title="Group Nearby Attractions"
                text={
                  trip.local_exploration_tip ||
                  "Visit nearby attractions together to reduce unnecessary travel."
                }
              />

              <Recommendation
                number="03"
                title="Support Local Experiences"
                text="Prefer local restaurants, guides, businesses and community-based experiences."
              />

              <Recommendation
                number="04"
                title="Avoid Overtourism"
                text="Consider less crowded attractions and alternative locations when suitable."
              />

            </div>

          </section>


          {/* PROJECT NOTE */}

          <section className="sustainability-note">

            <div className="sustainability-note-icon">
              ℹ
            </div>

            <div>

              <h3>
                About this sustainability score
              </h3>

              <p>
                This is a project-level comparative score
                generated from the available route, transport,
                distance and emissions data. It should not be
                interpreted as an official carbon certification.
              </p>

            </div>

          </section>


          {/* ACTIONS */}

          <div className="sustainability-actions">

            <button
              className="secondary-light-button"
              onClick={() => navigate("/results")}
            >
              ← Back to My Journey
            </button>

            <button
              className="primary-action-button"
              onClick={() => navigate("/replanning")}
            >
              Dynamic Replanning →
            </button>

          </div>

        </div>

      </section>

    </div>
  );
}


/* =========================================================
   COMPONENTS
   ========================================================= */

function ScoreRow({
  name,
  score,
  max,
  icon,
}) {
  const percentage =
    max > 0 ? (score / max) * 100 : 0;

  return (
    <div className="score-row">

      <div className="score-row-top">

        <div className="score-row-name">

          <span className="score-row-icon">
            {icon}
          </span>

          <span>
            {name}
          </span>

        </div>

        <strong>
          {score}/{max}
        </strong>

      </div>

      <div className="score-row-bar">

        <div
          style={{
            width: `${Math.min(
              100,
              Math.max(0, percentage)
            )}%`,
          }}
        />

      </div>

    </div>
  );
}


function MetricCard({
  icon,
  value,
  label,
  description,
}) {
  return (
    <div className="sustainability-metric-card">

      <div className="metric-icon">
        {icon}
      </div>

      <strong>
        {value}
      </strong>

      <span>
        {label}
      </span>

      <p>
        {description}
      </p>

    </div>
  );
}


function CarbonBar({
  label,
  value,
  current,
}) {
  const width = Math.min(
    100,
    Math.max(8, (value / 1000) * 100)
  );

  return (
    <div className="carbon-row">

      <div className="carbon-row-heading">

        <span>
          {label}
        </span>

        <strong>
          {formatNumber(value, 1)} kg CO₂
        </strong>

      </div>

      <div className="carbon-bar">

        <div
          className={current ? "current-carbon" : ""}
          style={{
            width: `${width}%`,
          }}
        />

      </div>

      {current && (
        <span className="current-label">
          CURRENT JOURNEY
        </span>
      )}

    </div>
  );
}


function Recommendation({
  number,
  title,
  text,
}) {
  return (
    <article className="recommendation-card">

      <span className="recommendation-number">
        {number}
      </span>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

    </article>
  );
}


function formatNumber(value, decimals = 0) {
  return Number(value || 0).toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: decimals,
      minimumFractionDigits: decimals,
    }
  );
}


export default Sustainability;