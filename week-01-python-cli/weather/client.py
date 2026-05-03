"""
GOOD PRACTICES APPLIED:
- requests.Session(): before, you were using requests.get() directly for each call.
  The problem: you had to repeat appid, units, and lang every single time. Session()
  lets you define those parameters once and they are sent automatically with every
  request.

- Custom exception WeatherAPIError: before, you were probably letting raw exceptions
  from requests propagate (ConnectionError, HTTPError, etc.). The problem: the rest
  of your code had to know the internals of the requests library to catch them. A
  custom exception gives you one single, clean type to catch everywhere.

- _handle_response_errors(): before, you probably checked status codes inline inside
  your get function, or worse, ignored them entirely. Isolating this in a private
  method keeps get_weather() readable and puts all HTTP error translation in one place.

- timeout=10: before, you had no timeout on requests.get(). Without it, if the server
  never responds, your program hangs forever. Always set a timeout on network calls.

- Returning WeatherData, not raw dict: before, your api.py probably returned the raw
  JSON dict directly. The problem: every caller had to know the exact structure of the
  API response (data["main"]["temp"], etc.). Now callers just get a clean WeatherData
  object with named attributes.

WHAT NOT TO DO:
- Use requests.get() with all parameters repeated on every call
- Return raw JSON dicts from your API layer
- Leave network calls without a timeout
- Let requests internal exceptions propagate to main.py
- Put print() calls inside the client — error display belongs to display.py or main.py
"""
import os
import requests
from typing import Optional
from dotenv import load_dotenv

from weather.models import WeatherData

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherAPIError(Exception):
    """Custom exception for API-related errors."""
    pass


class WeatherClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise WeatherAPIError(
                "API key not found. Set OPENWEATHER_API_KEY in your .env file."
            )
        self.session = requests.Session()
        self.session.params = {"appid": self.api_key, "units": "metric", "lang": "en"}

    def get_weather(self, city: str) -> WeatherData:
        """
        Fetch current weather for a given city.
        Raises WeatherAPIError on any failure.
        """
        try:
            response = self.session.get(
                f"{BASE_URL}/weather",
                params={"q": city},
                timeout=10,
            )
            self._handle_response_errors(response, city)
            return WeatherData.from_api_response(response.json())

        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("No internet connection. Please check your network.")
        except requests.exceptions.Timeout:
            raise WeatherAPIError(f"Request timed out for city: {city}")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Unexpected network error: {e}")

    def get_multiple(self, cities: list[str]) -> list[WeatherData]:
        """Fetch weather for multiple cities. Skips failed ones with a warning."""
        results = []
        for city in cities:
            try:
                results.append(self.get_weather(city))
            except WeatherAPIError as e:
                print(f"Skipping '{city}': {e}")
        return results

    def _handle_response_errors(self, response: requests.Response, city: str) -> None:
        """Translate HTTP error codes into human-readable messages."""
        if response.status_code == 200:
            return
        if response.status_code == 401:
            raise WeatherAPIError("Invalid API key. Check your .env file.")
        if response.status_code == 404:
            raise WeatherAPIError(f"City not found: '{city}'. Check the spelling.")
        if response.status_code == 429:
            raise WeatherAPIError("Rate limit exceeded. Wait a moment and retry.")
        if response.status_code >= 500:
            raise WeatherAPIError("OpenWeatherMap server error. Try again later.")
        response.raise_for_status()
