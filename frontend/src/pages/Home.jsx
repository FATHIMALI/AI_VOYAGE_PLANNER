import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

function Home() {
  const navigate = useNavigate();

  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [travelers, setTravelers] = useState(1);

  const handleSearch = () => {
    if (!destination || !startDate || !endDate) {
      alert("Please enter destination and travel dates.");
      return;
    }

    navigate(
      `/plan?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(
        destination
      )}&start_date=${startDate}&end_date=${endDate}&travelers=${travelers}`
    );
  };

  const popularDestinations = [
    {
      name: "Goa",
      subtitle: "Beaches & nightlife",
      image:
        "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1000&q=85",
    },
    {
      name: "Manali",
      subtitle: "Mountains & adventure",
      image:
        "https://images.unsplash.com/photo-1518002054494-3a6f94352e9d?auto=format&fit=crop&w=1000&q=85",
    },
    {
      name: "Jaipur",
      subtitle: "Heritage & culture",
      image:
        "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1000&q=85",
    },
    {
      name: "Ooty",
      subtitle: "Hills & nature",
      image:
        "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=1000&q=85",
    },
  ];

  const travelCategories = [
    {
      icon: "🏖️",
      title: "Beach Escapes",
      text: "Relax by beautiful beaches",
    },
    {
      icon: "⛰️",
      title: "Mountain Trips",
      text: "Explore scenic mountain destinations",
    },
    {
      icon: "🏛️",
      title: "Heritage",
      text: "Discover history and culture",
    },
    {
      icon: "🍜",
      title: "Food Trails",
      text: "Experience local flavours",
    },
    {
      icon: "🧗",
      title: "Adventure",
      text: "Plan exciting experiences",
    },
    {
      icon: "🌿",
      title: "Nature",
      text: "Escape into peaceful destinations",
    },
  ];

  return (
    <main className="home-page">

      {/* HERO */}
      <section className="home-hero">
        <div className="home-hero-overlay"></div>

        <div className="home-hero-content">
          <div className="home-eyebrow">
            AI POWERED TRAVEL PLANNING
          </div>

          <h1>
            Your journey.
            <br />
            <span>Planned intelligently.</span>
          </h1>

          <p>
            Discover destinations, create personalized itineraries and
            adapt your trip with AI.
          </p>

          {/* SEARCH CARD */}
          <div className="home-search-card">

            <div className="home-search-heading">
              <span>✈</span>
              <div>
                <strong>Plan your trip</strong>
                <small>Let AI build your perfect journey</small>
              </div>
            </div>

            <div className="home-search-fields">

              <div className="home-field">
                <label>FROM</label>
                <input
                  type="text"
                  placeholder="Your city"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                />
              </div>

              <div className="home-field">
                <label>TO</label>
                <input
                  type="text"
                  placeholder="Where do you want to go?"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                />
              </div>

              <div className="home-field">
                <label>DEPARTURE</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>

              <div className="home-field">
                <label>RETURN</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>

              <div className="home-field travelers-field">
                <label>TRAVELLERS</label>

                <select
                  value={travelers}
                  onChange={(e) =>
                    setTravelers(Number(e.target.value))
                  }
                >
                  <option value={1}>1 Traveller</option>
                  <option value={2}>2 Travellers</option>
                  <option value={3}>3 Travellers</option>
                  <option value={4}>4 Travellers</option>
                  <option value={5}>5 Travellers</option>
                  <option value={6}>6 Travellers</option>
                </select>
              </div>

              <button
                className="home-ai-search-btn"
                onClick={handleSearch}
              >
                ✨ Plan with AI
              </button>

            </div>
          </div>
        </div>
      </section>

      {/* POPULAR DESTINATIONS */}
      <section className="home-section">

        <div className="home-section-header">
          <div>
            <span className="home-section-label">
              DISCOVER INDIA
            </span>

            <h2>
              Popular destinations
            </h2>

            <p>
              Find your next destination and let AI plan the rest.
            </p>
          </div>

          <Link to="/explore" className="home-view-all">
            View all →
          </Link>
        </div>

        <div className="home-destination-grid">

          {popularDestinations.map((destination) => (
            <Link
              to={`/destination/${destination.name}`}
              className="home-destination-card"
              key={destination.name}
            >
              <img
                src={destination.image}
                alt={destination.name}
              />

              <div className="home-card-gradient"></div>

              <div className="home-destination-info">
                <span>EXPLORE</span>
                <h3>{destination.name}</h3>
                <p>{destination.subtitle}</p>
              </div>
            </Link>
          ))}

        </div>
      </section>

      {/* CATEGORIES */}
      <section className="home-category-section">

        <div className="home-section-header">
          <div>
            <span className="home-section-label">
              FIND YOUR EXPERIENCE
            </span>

            <h2>
              What kind of trip are you planning?
            </h2>
          </div>
        </div>

        <div className="home-category-grid">

          {travelCategories.map((category) => (
            <Link
              to={`/explore?theme=${encodeURIComponent(
                category.title
              )}`}
              className="home-category-card"
              key={category.title}
            >
              <div className="home-category-icon">
                {category.icon}
              </div>

              <h3>{category.title}</h3>

              <p>{category.text}</p>

              <span>Explore →</span>
            </Link>
          ))}

        </div>

      </section>

      {/* AI FEATURE */}
      <section className="home-ai-section">

        <div className="home-ai-content">

          <span className="home-section-label">
            YOUR PERSONAL AI TRAVEL ASSISTANT
          </span>

          <h2>
            Don't just book a trip.
            <br />
            <span>Build a journey.</span>
          </h2>

          <p>
            Tell us where you want to go, how much you want to spend,
            what you love doing and how long you are travelling.
            Our AI creates a personalized itinerary around you.
          </p>

          <div className="home-ai-points">

            <div>
              <strong>01</strong>
              <span>Personalized itinerary</span>
            </div>

            <div>
              <strong>02</strong>
              <span>Real-time travel information</span>
            </div>

            <div>
              <strong>03</strong>
              <span>Dynamic trip adaptation</span>
            </div>

          </div>

          <Link to="/plan" className="home-dark-btn">
            Start planning with AI →
          </Link>

        </div>

        <div className="home-ai-visual">

          <div className="ai-trip-card">

            <div className="ai-trip-top">
              <span>AI GENERATED TRIP</span>
              <span className="ai-status">● Ready</span>
            </div>

            <h3>5 Days in Rajasthan</h3>

            <p>
              Personalized for culture, history & food
            </p>

            <div className="ai-trip-items">

              <div>
                <span>DAY 01</span>
                <strong>Jaipur Heritage</strong>
              </div>

              <div>
                <span>DAY 02</span>
                <strong>Amber Fort & Local Food</strong>
              </div>

              <div>
                <span>DAY 03</span>
                <strong>Jodhpur Exploration</strong>
              </div>

              <div>
                <span>DAY 04</span>
                <strong>Local Experiences</strong>
              </div>

            </div>

          </div>

        </div>

      </section>

      {/* FINAL CTA */}
      <section className="home-final-cta">

        <span>READY TO EXPLORE?</span>

        <h2>
          Your next adventure
          <br />
          starts here.
        </h2>

        <p>
          Let AI turn your travel ideas into a complete journey.
        </p>

        <Link to="/plan" className="home-cta-btn">
          Plan my trip with AI ✨
        </Link>

      </section>

    </main>
  );
}

export default Home;