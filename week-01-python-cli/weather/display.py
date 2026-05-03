"""
GOOD PRACTICES APPLIED:
- All print() calls are isolated here: before, you had print() scattered across
  api.py, main.py, and everywhere else. The problem: if you want to change how
  something looks, you have to hunt through every file. Here, you change one file.

- ANSI color constants at the top: before, you either had no colors at all, or you
  were copy-pasting the raw escape codes ("\033[91m") inline. Constants have names
  that are readable (RED, BOLD) and are defined once.

- _temp_color(): the logic of "which color for which temperature" is a separate
  function, not inlined inside print_weather_card(). This makes it reusable —
  print_comparison_table() uses it too without duplicating the logic.

- Private functions with _ prefix: _temp_color() and _print_alerts() are internal
  helpers. The _ prefix is a Python convention that signals "this is not part of
  the public interface of this module — do not call it from outside."

- Asking the model instead of deciding: _print_alerts() calls data.has_rain(),
  data.is_hot(), data.is_cold(). It does not reimplement that logic. The model
  owns the business rules, the display just reacts to them.

WHAT NOT TO DO:
- Put print() calls inside client.py, models.py, or main.py business logic
- Hardcode raw ANSI escape codes inline instead of named constants
- Reimplement "is it raining?" logic in the display layer
- Build one giant print function instead of small composable ones
"""
from weather.models import WeatherData

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
GRAY = "\033[90m"


def _temp_color(temp: float) -> str:
    if temp <= 5:
        return BLUE
    if temp <= 20:
        return CYAN
    if temp <= 32:
        return GREEN
    return RED


def print_weather_card(data: WeatherData) -> None:
    """Print a single city weather card."""
    color = _temp_color(data.temperature)
    print()
    print(f"{BOLD}{'─' * 42}{RESET}")
    print(f"{BOLD}  📍 {data.city}, {data.country}{RESET}")
    print(f"{'─' * 42}")
    print(f"  🌡️  Temperature  : {color}{BOLD}{data.temperature}°C{RESET}  (feels like {data.feels_like}°C)")
    print(f"  💧 Humidity     : {data.humidity}%")
    print(f"  💨 Wind         : {data.wind_speed} km/h")
    print(f"  🌤️  Condition    : {data.description}")
    print(f"  🕒 Updated at   : {GRAY}{data.timestamp}{RESET}")
    _print_alerts(data)
    print(f"{BOLD}{'─' * 42}{RESET}")
    print()


def print_comparison_table(weather_list: list[WeatherData]) -> None:
    """Print a side-by-side comparison table for multiple cities."""
    if not weather_list:
        print(f"{RED}No data to compare.{RESET}")
        return

    print()
    print(f"{BOLD}{'─' * 72}{RESET}")
    print(f"{BOLD}  🌍 City Comparison{RESET}")
    print(f"{BOLD}{'─' * 72}{RESET}")

    # Header
    print(f"  {BOLD}{'City':<18} {'Temp':>8} {'Feels':>8} {'Humidity':>10} {'Wind':>10} {'Condition':<20}{RESET}")
    print(f"  {'─'*18} {'─'*8} {'─'*8} {'─'*10} {'─'*10} {'─'*20}")

    for d in weather_list:
        color = _temp_color(d.temperature)
        city_label = f"{d.city}, {d.country}"
        print(
            f"  {city_label:<18} "
            f"{color}{BOLD}{d.temperature:>7.1f}°{RESET} "
            f"{d.feels_like:>7.1f}° "
            f"{d.humidity:>9}% "
            f"{d.wind_speed:>8} km/h "
            f"{d.description:<20}"
        )

    print(f"{BOLD}{'─' * 72}{RESET}")

    # Highlight extremes
    hottest = max(weather_list, key=lambda x: x.temperature)
    coldest = min(weather_list, key=lambda x: x.temperature)
    windiest = max(weather_list, key=lambda x: x.wind_speed)

    print(f"\n  {RED}🔥 Hottest  :{RESET} {hottest.city} ({hottest.temperature}°C)")
    print(f"  {BLUE}❄️  Coldest  :{RESET} {coldest.city} ({coldest.temperature}°C)")
    print(f"  {CYAN}💨 Windiest :{RESET} {windiest.city} ({windiest.wind_speed} km/h)")
    print()


def _print_alerts(data: WeatherData) -> None:
    """Print contextual alerts below the weather card."""
    if data.has_rain():
        print(f"  {YELLOW}⚠️  ALERT: Rain expected — take an umbrella!{RESET}")
    if data.is_hot():
        print(f"  {RED}⚠️  ALERT: Extreme heat ({data.temperature}°C) — stay hydrated!{RESET}")
    if data.is_cold():
        print(f"  {BLUE}⚠️  ALERT: Cold weather ({data.temperature}°C) — dress warmly!{RESET}")


def print_success(message: str) -> None:
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message: str) -> None:
    print(f"{RED}❌ Error: {message}{RESET}")


def print_info(message: str) -> None:
    print(f"{CYAN}ℹ️  {message}{RESET}")
