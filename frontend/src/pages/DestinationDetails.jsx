import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../App.css";

const destinationImages = {
  Delhi:
    "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1600&q=80",

  Mumbai:
    "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1600&q=80",

  Lonavala:
    "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1600&q=80",

  Bangalore:
    "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=1600&q=80",

  Hyderabad:
    "https://images.unsplash.com/photo-1572445271230-a78b5944a659?auto=format&fit=crop&w=1600&q=80",

  Kolkata:
    "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=1600&q=80",

  Goa:
    "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1600&q=80",

  Ahmedabad:
    "https://images.unsplash.com/photo-1595658658481-d53d3f999875?auto=format&fit=crop&w=1600&q=80",

  Dwarka:
    "https://images.unsplash.com/photo-1609947017136-9daf32a5eb16?auto=format&fit=crop&w=1600&q=80",

  Junagadh:
    "https://images.unsplash.com/photo-1598091383021-15ddea10925d?auto=format&fit=crop&w=1600&q=80",

  Bhuj:
    "https://images.unsplash.com/photo-1605640840605-14ac1855827b?auto=format&fit=crop&w=1600&q=80",

  Vadodara:
    "https://images.unsplash.com/photo-1596402184320-417e7178b2cd?auto=format&fit=crop&w=1600&q=80",
};

function DestinationDetails() {
  const { destination } = useParams();
  const navigate = useNavigate();

  const city = decodeURIComponent(destination);

  const [attractions, setAttractions] = useState([]);
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(true);

  const image =
    destinationImages[city] ||
    "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1600&q=80";

  useEffect(() => {
    async function loadDestinationData() {
      try {
        setLoading(true);

        const attractionResponse = await fetch(
          `http://127.0.0.1:8000/api/attractions?city=${encodeURIComponent(
            city
          )}&limit=12`
        );

        if (attractionResponse.ok) {
          const attractionData = await attractionResponse.json();
          setAttractions(attractionData.items || []);
        }

        try {
          const hotelResponse = await fetch(
            `http://127.0.0.1:8000/api/hotels?city=${encodeURIComponent(
              city
            )}&limit=8`
          );

          if (hotelResponse.ok) {
            const hotelData = await hotelResponse.json();
            setHotels(hotelData.items || []);
          }
        } catch {
          setHotels([]);
        }
      } catch (error) {
        console.error("Destination loading error:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDestinationData();
  }, [city]);

  return (
    <div className="destination-page">

      {/* HERO */}

      <section
        className="destination-hero"
        style={{ backgroundImage: `url("${image}")` }}
      >
        <div className="destination-hero-overlay"></div>

        <div className="destination-hero-content">
          <p>EXPLORE INDIA</p>

          <h1>{city}</h1>

          <span>
            Discover attractions, hotels, transport and travel information
          </span>
        </div>
      </section>

      {/* CONTENT */}

      <main className="destination-content">

        {/* INTRO */}

        <section className="destination-intro">

          <div>
            <span className="section-label">DESTINATION GUIDE</span>

            <h2>
              Explore {city}
            </h2>

            <p>
              Discover popular places, accommodation options and useful
              travel information for your journey to {city}.
            </p>
          </div>

          <button
            className="destination-plan-btn"
            onClick={() =>
              navigate(
                `/plan?destination=${encodeURIComponent(city)}`
              )
            }
          >
            Plan a Trip to {city} →
          </button>

        </section>

        {/* QUICK INFORMATION */}

        <section className="destination-info-grid">

          <div className="destination-info-card">
            <div className="info-icon">📍</div>
            <h3>Location</h3>
            <p>{city}, India</p>
          </div>

          <div className="destination-info-card">
            <div className="info-icon">🏛️</div>
            <h3>Attractions</h3>
            <p>
              {loading ? "Loading..." : `${attractions.length} places found`}
            </p>
          </div>

          <div className="destination-info-card">
            <div className="info-icon">🏨</div>
            <h3>Hotels</h3>
            <p>
              {loading ? "Loading..." : `${hotels.length} hotels found`}
            </p>
          </div>

          <div className="destination-info-card">
            <div className="info-icon">🌱</div>
            <h3>Sustainable Travel</h3>
            <p>Eco-conscious planning</p>
          </div>

        </section>

        {/* ATTRACTIONS */}

        <section className="destination-section">

          <div className="section-heading">
            <div>
              <span className="section-label">PLACES TO VISIT</span>
              <h2>Popular Attractions</h2>
            </div>

            <span className="section-count">
              {attractions.length} places
            </span>
          </div>

          {loading ? (
            <div className="destination-loading">
              Loading attractions...
            </div>
          ) : attractions.length === 0 ? (
            <div className="destination-empty">
              No attraction data available for {city}.
            </div>
          ) : (
            <div className="destination-card-grid">

              {attractions.map((place, index) => (

                <div
                  className="destination-place-card"
                  key={index}
                >

                  <div className="place-number">
                    {String(index + 1).padStart(2, "0")}
                  </div>

                  <h3>
                    {place.name ||
                      place.Name ||
                      place.monument ||
                      place.destination ||
                      "Tourist Attraction"}
                  </h3>

                  <p>
                    {place.description ||
                      place.significance ||
                      "Popular tourist attraction in India."}
                  </p>

                  {place.Type && (
                    <span className="place-tag">
                      {place.Type}
                    </span>
                  )}

                </div>

              ))}

            </div>
          )}

        </section>

        {/* HOTELS */}

        <section className="destination-section">

          <div className="section-heading">

            <div>
              <span className="section-label">STAY</span>
              <h2>Hotels & Accommodation</h2>
            </div>

            <span className="section-count">
              {hotels.length} options
            </span>

          </div>

          {hotels.length === 0 ? (

            <div className="destination-empty">
              Hotel information will appear here when available.
            </div>

          ) : (

            <div className="hotel-grid">

              {hotels.map((hotel, index) => (

                <div className="hotel-card" key={index}>

                  <div className="hotel-icon">
                    🏨
                  </div>

                  <div>

                    <h3>
                      {hotel["Hotel Name"] ||
                        hotel.hotel_name ||
                        "Hotel"}
                    </h3>

                    <p>
                      {hotel.Place || city}
                    </p>

                    {hotel.Rating && (
                      <span className="hotel-rating">
                        ★ {hotel.Rating}
                      </span>
                    )}

                  </div>

                </div>

              ))}

            </div>

          )}

        </section>

        {/* TRAVEL INFORMATION */}

        <section className="destination-section">

          <div className="section-heading">

            <div>
              <span className="section-label">
                TRAVEL INFORMATION
              </span>

              <h2>Getting Around</h2>
            </div>

          </div>

          <div className="travel-options">

            <div className="travel-option">
              <span>✈️</span>
              <div>
                <h3>Air Travel</h3>
                <p>
                  Find nearby airports and plan your arrival.
                </p>
              </div>
            </div>

            <div className="travel-option">
              <span>🚆</span>
              <div>
                <h3>Rail Travel</h3>
                <p>
                  Explore railway connectivity to {city}.
                </p>
              </div>
            </div>

            <div className="travel-option">
              <span>🚗</span>
              <div>
                <h3>Road Travel</h3>
                <p>
                  Plan road routes and local transportation.
                </p>
              </div>
            </div>

          </div>

        </section>

        {/* AI PLANNER */}

        <section className="destination-ai-banner">

          <div>

            <span className="section-label">
              AI VOYAGE PLANNER
            </span>

            <h2>
              Ready to build your {city} journey?
            </h2>

            <p>
              Tell us your budget, available time and interests.
              Our AI planner will create a personalized itinerary.
            </p>

          </div>

          <button
            onClick={() =>
              navigate(
                `/plan?destination=${encodeURIComponent(city)}`
              )
            }
          >
            Create My Itinerary →
          </button>

        </section>

      </main>

    </div>
  );
}

export default DestinationDetails;