# Agentic AI Travel Planner

An intelligent AI-powered travel planning assistant built using LangChain, OpenAI, and Streamlit.

This project helps users automatically generate travel itineraries by analyzing:
- Flights
- Hotels
- Tourist places
- Weather conditions
- Budget preferences

The system uses Agentic AI with LangChain tools to perform multi-step reasoning and generate smart travel recommendations.

---

# Features

 AI-generated travel itineraries

 Flight search from JSON dataset

 Hotel recommendations

 Tourist place suggestions

 Real-time weather integration

 Budget-aware trip planning

 Streamlit interactive UI

 LangChain agent with tool calling

---

# Tech Stack

- Python
- LangChain
- OpenAI API
- Streamlit
- JSON Datasets
- Open-Meteo API

---

# Project Structure

```plaintext
travel_planner_ai/
│
├── app.py
├── agent.py
├── tools.py
├── prompts.py
├── requirements.txt
├── .env
│
├── data/
│   ├── flights.json
│   ├── hotels.json
│   └── places.json
│
├── utils/
│   ├── weather_api.py
│   └── helpers.py
│
└── README.md
```

---

# Installation Steps

## 1. Clone the repository

```code
git clone <your_github_repo_link>
```

---

## 2. Move into project folder

```code for CMD prompt
cd travel_planner_ai
```

---

## 3. Create virtual environment

### Windows

```code for terminal
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```code for terminal
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install dependencies

```code for terminal
pip install -r requirements.txt
```

---

## 5. Create `.env` file

Create a file named `.env`

Add:

```env
OPENAI_API_KEY=your_openai_api_key
```

---

# Run Commands

Start Streamlit app:

```code for terminal
streamlit run app.py
```

---

# Example Workflow

1. Enter source city
2. Enter destination city
3. Select trip duration
4. AI agent searches:
   - Flights
   - Hotels
   - Tourist attractions
   - Weather
5. Final itinerary is generated

---

# Screenshots

## Home Page

(Add screenshot here)

## Generated Itinerary

(Add screenshot here)

---

# Future Improvements

- Real-time flight APIs
- Google Maps integration
- Expense tracking
- Voice assistant
- Multi-city planning
- Hotel booking integration

---

# Author

sumit

---

# License

This project is for educational purposes.