import streamlit as st

st.set_page_config(
    page_title="UI Test",
    page_icon="🧭",
    layout="wide"
)

st.markdown(
    """
    <style>

    .title {
        font-size: 40px;
        font-weight: 800;
        color: #0f172a;
    }

    .card {
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        background: white;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="title">
        🧭 AI Voyage Planner
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="card">

        <h2>🧳 Build Your Journey</h2>

        <p>
            Enter your travel preferences.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)

source = st.text_input(
    "📍 From",
    placeholder="Chennai"
)

destination = st.text_input(
    "🗺️ To",
    placeholder="Goa"
)

budget = st.number_input(
    "💰 Budget",
    min_value=1000,
    value=10000
)

days = st.number_input(
    "📅 Days",
    min_value=1,
    value=3
)

preference = st.selectbox(
    "🌱 Travel Preference",
    [
        "Sustainable",
        "Budget Friendly",
        "Comfort",
        "Adventure",
        "Luxury"
    ]
)

interests = st.multiselect(
    "❤️ Interests",
    [
        "Nature",
        "Heritage",
        "Food",
        "Beaches",
        "Adventure"
    ]
)

st.success("Frontend test loaded successfully.")