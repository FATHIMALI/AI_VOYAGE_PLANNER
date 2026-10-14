import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

const API = "http://127.0.0.1:8000";

const themeData = [
  {
    title: "Beach Escapes",
    subtitle: "Sun, sand & coastal experiences",
    icon: "🏖️",
    image:
      "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=85",
    interests: "beach,relaxation,food",
  },
  {
    title: "Hills & Mountains",
    subtitle: "Scenic views and peaceful escapes",
    icon: "🏔️",
    image:
      "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=85",
    interests: "nature,adventure,photography",
  },
  {
    title: "Heritage & History",
    subtitle: "Monuments, culture and stories",
    icon: "🏛️",
    image:
      "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=900&q=85",
    interests: "history,culture,heritage",
  },
  {
    title: "Food Trails",
    subtitle: "Taste authentic local flavours",
    icon: "🍜",
    image:
      "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=85",
    interests: "food,culture,shopping",
  },
  {
    title: "Adventure",
    subtitle: "Thrills, trails and outdoor fun",
    icon: "🧗",
    image:
      "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=900&q=85",
    interests: "adventure,nature,trekking",
  },
  {
    title: "Spiritual Journeys",
    subtitle: "Temples, traditions and peaceful places",
    icon: "🛕",
    image:
      "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=85",
    interests: "spiritual,culture,history",
  },
  {
    title: "Romantic Getaways",
    subtitle: "Beautiful escapes for two",
    icon: "❤️",
    image:
      "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=85",
    interests: "romantic,relaxation,food",
  },
  {
    title: "Weekend Escapes",
    subtitle: "Short trips without the hassle",
    icon: "🌄",
    image:
      "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=85",
    interests: "nature,relaxation,adventure",
  },
];

const popularIndia = [
  {
    name: "Goa",
    type: "Beach • Food • Nightlife",
    image:
      "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Ooty",
    type: "Hills • Nature • Relaxation",
    image:
      "https://images.unsplash.com/photo-1593693411515-c20261bcad6e?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Pondicherry",
    type: "Coast • Culture • Cafés",
    image:
      "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Jaipur",
    type: "Heritage • Culture • Food",
    image:
      "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Manali",
    type: "Mountains • Adventure • Nature",
    image:
      "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Coorg",
    type: "Nature • Coffee • Hills",
    image:
      "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=900&q=85",
  },
];

const international = [
  {
    name: "Maldives",
    type: "Beach • Luxury",
    image:
      "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Bali",
    type: "Culture • Nature • Beaches",
    image:
      "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Dubai",
    type: "Luxury • Shopping • Experiences",
    image:
      "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=900&q=85",
  },
  {
    name: "Paris",
    type: "Culture • Food • Architecture",
    image:
      "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=900&q=85",
  },
];

const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

function ExploreCard({ item }) {
  const query = new URLSearchParams({
    destination: item.name,
    interests: item.interests || "culture,nature,food",
    days: "3",
    budget: "25000",
    travelers: "1",
  }).toString();

  return (
    <Link
      to={`/results?${query}`}
      className="explore-mmt-card"
    >
      <div className="explore-mmt-card-image">
        <img src={item.image} alt={item.name} />
        <div className="explore-mmt-card-overlay"></div>

        <div className="explore-mmt-card-content">
          <span>{item.type || "Explore destination"}</span>
          <h3>{item.name}</h3>
        </div>
      </div>
    </Link>
  );
}

function ThemeCard({ item }) {
  const query = new URLSearchParams({
    destination: "",
    interests: item.interests,
    days: "3",
    budget: "25000",
    travelers: "1",
  }).toString();

  return (
    <Link
      to={`/plan?${query}`}
      className="explore-theme-card"
    >
      <div className="explore-theme-image">
        <img src={item.image} alt={item.title} />
        <div className="explore-theme-overlay"></div>

        <div className="explore-theme-icon">
          {item.icon}
        </div>

        <div className="explore-theme-content">
          <h3>{item.title}</h3>
          <p>{item.subtitle}</p>
        </div>
      </div>
    </Link>
  );
}

export default function Explore() {
  const [search, setSearch] = useState("");
  const [selectedMonth, setSelectedMonth] = useState("October");
  const [datasetPlaces, setDatasetPlaces] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDestinations();
  }, []);

  async function loadDestinations() {
    try {
      setLoading(true);

      const response = await fetch(
        `${API}/api/destinations`
      );

      if (!response.ok) {
        throw new Error("Unable to load destinations");
      }

      const data = await response.json();

      const items =
        data.items ||
        data.destinations ||
        data.results ||
        [];

      setDatasetPlaces(items);
    } catch (error) {
      console.error("Explore data error:", error);
      setDatasetPlaces([]);
    } finally {
      setLoading(false);
    }
  }

  const filteredPlaces = useMemo(() => {
    if (!search.trim()) {
      return datasetPlaces.slice(0, 12);
    }

    const value = search.toLowerCase();

    return datasetPlaces
      .filter((place) => {
        const text = [
          place.name,
          place.city,
          place.type,
          place.description,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();

        return text.includes(value);
      })
      .slice(0, 12);
  }, [search, datasetPlaces]);

  function searchDestination(event) {
    event.preventDefault();

    const destination = search.trim();

    if (!destination) return;

    const query = new URLSearchParams({
      destination,
      interests: "culture,food,nature",
      days: "3",
      budget: "25000",
      travelers: "1",
    }).toString();

    window.location.href = `/results?${query}`;
  }

  const datasetCards = filteredPlaces.map(
    (place, index) => {
      const image =
        place.image ||
        place.image_url ||
        place.photo ||
        place.thumbnail ||
        "";

      return {
        name:
          place.name ||
          place.city ||
          "Travel destination",
        type:
          place.type ||
          place.description ||
          "Explore this place",
        image,
        interests: "culture,nature,food",
        index,
      };
    }
  );

  return (
    <div className="explore-mmt-page">

      {/* =====================================================
          HERO
      ===================================================== */}

      <section className="explore-mmt-hero">
        <div className="explore-mmt-hero-overlay"></div>

        <div className="explore-mmt-hero-content">
          <div className="explore-mmt-eyebrow">
            AI VOYAGE PLANNER
          </div>

          <h1>
            Discover places.
            <br />
            <span>Plan unforgettable journeys.</span>
          </h1>

          <p>
            Explore destinations, experiences and travel
            ideas — then let AI build the journey around you.
          </p>

          <form
            className="explore-search"
            onSubmit={searchDestination}
          >
            <div className="explore-search-icon">
              🔍
            </div>

            <input
              type="text"
              placeholder="Search a destination, city or experience"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />

            <button type="submit">
              Explore
            </button>
          </form>

          <div className="explore-search-hints">
            <span>Try:</span>
            <button
              type="button"
              onClick={() => setSearch("Goa")}
            >
              Goa
            </button>
            <button
              type="button"
              onClick={() => setSearch("Ooty")}
            >
              Ooty
            </button>
            <button
              type="button"
              onClick={() => setSearch("Jaipur")}
            >
              Jaipur
            </button>
            <button
              type="button"
              onClick={() => setSearch("Kerala")}
            >
              Kerala
            </button>
          </div>
        </div>
      </section>

      {/* =====================================================
          THEME DISCOVERY
      ===================================================== */}

      <section className="explore-mmt-section">
        <div className="explore-mmt-section-heading">
          <div>
            <span>FIND YOUR KIND OF TRIP</span>
            <h2>Explore by experience</h2>
            <p>
              Choose the kind of journey you are in the mood
              for and discover destinations that match it.
            </p>
          </div>
        </div>

        <div className="explore-theme-grid">
          {themeData.map((item) => (
            <ThemeCard
              item={item}
              key={item.title}
            />
          ))}
        </div>
      </section>

      {/* =====================================================
          INDIA DESTINATIONS
      ===================================================== */}

      <section className="explore-mmt-section explore-light-section">
        <div className="explore-mmt-section-heading split">
          <div>
            <span>TRAVEL INDIA</span>
            <h2>Popular places to explore</h2>
            <p>
              Discover some of India's most loved travel
              destinations and create your own AI-powered
              itinerary.
            </p>
          </div>

          <Link
            to="/plan"
            className="explore-view-all"
          >
            Plan a trip →
          </Link>
        </div>

        <div className="explore-destination-grid">
          {popularIndia.map((item) => (
            <ExploreCard
              item={item}
              key={item.name}
            />
          ))}
        </div>
      </section>

      {/* =====================================================
          AI DISCOVERY
      ===================================================== */}

      <section className="explore-ai-banner">
        <div className="explore-ai-banner-content">
          <span>AI-POWERED DISCOVERY</span>

          <h2>
            Don't know where to go?
            <br />
            Let AI find the right trip for you.
          </h2>

          <p>
            Tell us your interests, budget and available
            time. AI Voyage Planner can turn those
            preferences into a personalized journey.
          </p>

          <Link
            to="/plan"
            className="explore-ai-button"
          >
            Start planning with AI →
          </Link>
        </div>

        <div className="explore-ai-visual">
          <div className="ai-orbit-card ai-card-one">
            <span>INTEREST</span>
            <strong>Culture</strong>
          </div>

          <div className="ai-orbit-card ai-card-two">
            <span>BUDGET</span>
            <strong>₹25,000</strong>
          </div>

          <div className="ai-orbit-card ai-card-three">
            <span>DURATION</span>
            <strong>3 Days</strong>
          </div>

          <div className="ai-center-circle">
            <div>✦</div>
            <strong>AI</strong>
            <span>VOYAGE</span>
          </div>
        </div>
      </section>

      {/* =====================================================
          DATASET DESTINATIONS
      ===================================================== */}

      <section className="explore-mmt-section">
        <div className="explore-mmt-section-heading split">
          <div>
            <span>DESTINATION DISCOVERY</span>
            <h2>Explore more places</h2>
            <p>
              Places available from your tourism knowledge
              base.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="explore-data-loading">
            <div className="explore-spinner"></div>
            <p>Discovering destinations...</p>
          </div>
        ) : datasetCards.length > 0 ? (
          <div className="explore-dataset-grid">
            {datasetCards.map((item) => (
              <ExploreCard
                item={item}
                key={`${item.name}-${item.index}`}
              />
            ))}
          </div>
        ) : (
          <div className="explore-empty">
            <span>📍</span>
            <h3>No destination data available</h3>
            <p>
              Try searching for a destination or start
              planning a trip with AI.
            </p>
          </div>
        )}
      </section>

      {/* =====================================================
          INTERNATIONAL
      ===================================================== */}

      <section className="explore-mmt-section explore-light-section">
        <div className="explore-mmt-section-heading split">
          <div>
            <span>GO BEYOND INDIA</span>
            <h2>International inspiration</h2>
            <p>
              Explore destinations around the world and
              create your next adventure.
            </p>
          </div>
        </div>

        <div className="explore-destination-grid international-grid">
          {international.map((item) => (
            <ExploreCard
              item={item}
              key={item.name}
            />
          ))}
        </div>
      </section>

      {/* =====================================================
          MONTHLY DISCOVERY
      ===================================================== */}

      <section className="explore-month-section">
        <div className="explore-mmt-section-heading">
          <span>PLAN AROUND THE TIME OF YEAR</span>
          <h2>Where should you travel?</h2>
          <p>
            Select a month to start discovering destinations
            that could fit your travel plans.
          </p>
        </div>

        <div className="explore-month-tabs">
          {months.map((month) => (
            <button
              key={month}
              className={
                selectedMonth === month
                  ? "active"
                  : ""
              }
              onClick={() =>
                setSelectedMonth(month)
              }
            >
              {month}
            </button>
          ))}
        </div>

        <div className="explore-month-result">
          <div className="month-result-icon">
            📅
          </div>

          <div>
            <span>SELECTED MONTH</span>
            <h3>{selectedMonth}</h3>
            <p>
              Ready to discover destinations for
              {` ${selectedMonth}`}?
            </p>
          </div>

          <Link
            to="/plan"
            className="month-plan-button"
          >
            Plan this trip →
          </Link>
        </div>
      </section>

      {/* =====================================================
          TRAVEL COLLECTIONS
      ===================================================== */}

      <section className="explore-collections">
        <div className="explore-collections-heading">
          <span>CURATED IDEAS</span>
          <h2>Travel collections for every mood</h2>
        </div>

        <div className="explore-collection-list">
          <Link to="/plan">
            <span>01</span>
            <strong>Weekend escapes</strong>
            <em>Short & refreshing</em>
            <b>→</b>
          </Link>

          <Link to="/plan">
            <span>02</span>
            <strong>Heritage journeys</strong>
            <em>History & culture</em>
            <b>→</b>
          </Link>

          <Link to="/plan">
            <span>03</span>
            <strong>Adventure trails</strong>
            <em>Thrills & nature</em>
            <b>→</b>
          </Link>

          <Link to="/plan">
            <span>04</span>
            <strong>Food discoveries</strong>
            <em>Local flavours</em>
            <b>→</b>
          </Link>

          <Link to="/plan">
            <span>05</span>
            <strong>Peaceful getaways</strong>
            <em>Relax & recharge</em>
            <b>→</b>
          </Link>
        </div>
      </section>

      {/* =====================================================
          FINAL CTA
      ===================================================== */}

      <section className="explore-final-cta">
        <div>
          <span>YOUR JOURNEY STARTS HERE</span>
          <h2>
            Found a place you love?
          </h2>
          <p>
            Give us your destination and preferences.
            Our AI will turn the idea into a complete
            personalized voyage.
          </p>
        </div>

        <Link
          to="/plan"
          className="explore-final-button"
        >
          Build my itinerary →
        </Link>
      </section>

    </div>
  );
}

