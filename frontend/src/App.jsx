import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Home from "./pages/Home";
import PlanTrip from "./pages/PlanTrip";
import Explore from "./pages/Explore";
import DestinationDetails from "./pages/DestinationDetails";
import Results from "./pages/Results";
import Sustainability from "./pages/Sustainability";
import Replanning from "./pages/Replanning";

import "./App.css";

function Navbar() {
  return (
    <nav className="navbar">

      {/* LOGO */}
      <Link to="/" className="navbar-brand">
        <div className="brand-text">
          <span>AI Voyage</span>
          <small>PLANNER</small>
        </div>
      </Link>

      {/* NAVIGATION */}
      <div className="nav-links">

        <Link to="/" className="nav-link">
          Home
        </Link>

        <Link to="/explore" className="nav-link">
          Explore
        </Link>

        <Link to="/plan" className="nav-link">
          Plan Trip
        </Link>

        <Link to="/results" className="nav-link">
          My Trip
        </Link>

      </div>

      {/* AI CTA */}
      <Link to="/plan" className="nav-ai-btn">
        <span className="ai-sparkle">✦</span>
        Plan with AI
        <span className="ai-arrow">→</span>
      </Link>

    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>

      <Navbar />

      <Routes>

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/plan"
          element={<PlanTrip />}
        />

        <Route
          path="/explore"
          element={<Explore />}
        />

        <Route
          path="/destination/:destination"
          element={<DestinationDetails />}
        />

        <Route
          path="/results"
          element={<Results />}
        />

        <Route
          path="/sustainability"
          element={<Sustainability />}
        />

        <Route
          path="/replanning"
          element={<Replanning />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;