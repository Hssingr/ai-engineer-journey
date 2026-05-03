"""
GOOD PRACTICES APPLIED:
- @dataclass: automatically generates __init__ for us. Before, you were probably
  defining each attribute manually (self.city = city, self.temp = temp, etc.).
  @dataclass eliminates that repetitive boilerplate.

- @classmethod + from_api_response(): this is the "Factory Method" pattern. Before,
  you were probably parsing the JSON directly wherever you needed it (in api.py or
  main.py). The problem: if the API changes, you have to find and fix it everywhere.
  Here, all parsing logic is centralized in one single place.

- to_dict(): wondering why? Because json.dump() cannot serialize a custom Python
  object — it only understands built-in types (dict, list, str, int, float).
  to_dict() converts our WeatherData into a standard dict before export. Without
  this, json.dump(data) would crash with a TypeError.

- has_rain(), is_hot(), is_cold(): the logic of "is it raining?" belongs to the
  model, not to the display layer. Before, you might have written this condition
  directly inside a print(). Here, display.py just asks the model the question
  without caring about how it works internally.

WHAT NOT TO DO:
- Parse raw JSON directly in main.py or api.py (data["main"]["temp"] scattered everywhere)
- Put print() calls inside the model
- Mix data logic with display logic in the same place
"""
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class WeatherData:
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    description: str
    timestamp: str

    @classmethod
    def from_api_response(cls, data: dict) -> "WeatherData":
        return cls(
            city=data["name"],
            country=data["sys"]["country"],
            temperature=round(data["main"]["temp"], 1),
            feels_like=round(data["main"]["feels_like"], 1),
            humidity=data["main"]["humidity"],
            wind_speed=round(data["wind"]["speed"] * 3.6, 1),  # m/s → km/h
            description=data["weather"][0]["description"].capitalize(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    def has_rain(self) -> bool:
        keywords = ["rain", "drizzle", "shower", "thunder"]
        return any(k in self.description.lower() for k in keywords)

    def is_hot(self, threshold: float = 35.0) -> bool:
        return self.temperature >= threshold

    def is_cold(self, threshold: float = 5.0) -> bool:
        return self.temperature <= threshold
