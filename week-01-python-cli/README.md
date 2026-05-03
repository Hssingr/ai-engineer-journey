# 🌤️ WeatherCLI

A clean, professional command-line weather tool built with Python.  
Fetches real-time weather data from [OpenWeatherMap](https://openweathermap.org/api).

> Part of my [ai-engineer-journey](https://github.com/yourusername/ai-engineer-journey) — Day 5 project.

---

## Features

- 🔍 **Single city lookup** — temperature, humidity, wind, condition
- 🌍 **Multi-city comparison** — side-by-side table with extremes highlighted  
- ⚠️ **Smart alerts** — warns on rain, extreme heat, or cold
- 💾 **JSON export** — save results to `exports/` folder
- 📋 **Search history** — auto-logged to `weather_history.log`
- 🧱 **Clean architecture** — separated client, models, display, utils

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/ai-engineer-journey.git
cd ai-engineer-journey/day-05-weather-cli

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# Edit .env and add your key from https://openweathermap.org/api
```

---

## Usage

```bash
# Single city
python main.py Paris

# Multiple cities (individual cards)
python main.py Paris London Tokyo

# Compare multiple cities in a table
python main.py Paris London Tokyo --compare

# Export results to JSON
python main.py "New York" --export

# Compare + export with custom filename
python main.py Tunis Paris Berlin --compare --export --output my_report.json
```

---

## Project Structure

```
weather-cli/
├── main.py              # CLI entry point (argparse)
├── weather/
│   ├── client.py        # HTTP calls to OpenWeatherMap API
│   ├── models.py        # WeatherData dataclass
│   └── display.py       # Terminal formatting & colors
├── utils/
│   ├── logger.py        # Search history logging
│   └── export.py        # JSON export
├── .env.example         # API key template
├── requirements.txt
└── README.md
```

---

## Example Output

```
──────────────────────────────────────────
  📍 Paris, FR
──────────────────────────────────────────
  🌡️  Temperature  : 18.4°C  (feels like 17.9°C)
  💧 Humidity     : 72%
  💨 Wind         : 14.4 km/h
  🌤️  Condition    : Partly cloudy
  🕒 Updated at   : 2025-04-26 14:32:01
──────────────────────────────────────────
```

---

## What I Learned

- Structuring a Python project with modules and packages
- Separating concerns (API client / models / display / utils)  
- Error handling for network calls with `requests`
- Using `dataclasses` to model API responses
- CLI argument parsing with `argparse`
- Managing secrets with `python-dotenv` and `.gitignore`

---

## Tech Stack

- Python 3.11+
- `requests` — HTTP calls
- `python-dotenv` — environment variables
- OpenWeatherMap API (free tier)
