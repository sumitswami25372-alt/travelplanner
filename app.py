from datetime import date, timedelta
import os

import streamlit as st

from agents.travel_agent import build_rule_based_itinerary, format_human_readable, has_valid_openai_key, run_langchain_agent


st.set_page_config(page_title="Agentic Trip Planner", page_icon=":airplane:", layout="wide")
st.title("Agentic AI Trip Planner")

with st.sidebar:
    source = st.selectbox("Source", ["Delhi", "Mumbai", "Hyderabad", "Bangalore"])
    destination = st.selectbox("Destination", ["Goa", "Jaipur"])
    days = st.slider("Trip duration", min_value=3, max_value=7, value=3)
    start_date = st.date_input("Start date", value=date.today() + timedelta(days=14))
    max_hotel_price = st.number_input("Max hotel price/night", min_value=1000, max_value=10000, value=5000, step=500)
    interest = st.selectbox("Interest", ["mixed", "beach", "heritage", "market", "adventure", "nature"])
    typed_api_key = st.text_input("OpenAI API Key optional", type="password")
    if typed_api_key.strip():
        os.environ["OPENAI_API_KEY"] = typed_api_key.strip()
    openai_ready = has_valid_openai_key()
    use_llm = st.checkbox("Use LangChain OpenAI agent", value=False, disabled=not openai_ready)
    if not openai_ready:
        st.caption("OpenAI key not configured. The app will use the deterministic LangChain tools.")

query = (
    f"Plan a {days}-day trip from {source} to {destination} starting {start_date}. "
    f"Prefer {interest} places and hotels below Rs. {max_hotel_price} per night."
)

if st.button("Generate itinerary", type="primary"):
    if use_llm:
        try:
            st.subheader("LangChain Agent Output")
            st.write(run_langchain_agent(query))
        except Exception as exc:
            st.error(f"Travel Agent Error: {exc}")
            st.info("Showing deterministic tool-based itinerary instead. Check your OPENAI_API_KEY to enable the LLM agent.")

    plan = build_rule_based_itinerary(
        source=source,
        destination=destination,
        start_date=start_date,
        days=days,
        max_hotel_price=max_hotel_price,
        interest=interest,
    )

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Human-readable Output")
        st.text(format_human_readable(plan))
    with right:
        st.subheader("Clean JSON Output")
        st.json(plan)
