"""
GOOD PRACTICES APPLIED:
- argparse instead of sys.argv manually: before, you had no --help, no usage message,
  no automatic validation. argparse gives you all of that for free. If the user forgets
  to pass a city, it shows a clear error. If they type --help, it shows full documentation.

- parse_args() as a separate function: argument parsing is isolated in its own function,
  not mixed into main(). This makes main() easier to read and makes parse_args() testable
  independently.

- run_single() and run_multiple() as separate functions: before, you probably had one big
  block of if/else in main(). Splitting into two functions means each case is readable on
  its own and main() stays a clean 10-line orchestrator.

- Creating WeatherClient once in main(): the client is created once and passed to
  run_single() or run_multiple(). Before, you might have created a new client (or made
  a new requests.get()) inside each function call. Creating it once is cleaner and would
  allow connection reuse via Session().

- sys.exit(1) on failure: before, you probably just let the program end naturally after
  printing an error. sys.exit(1) signals to the shell that the program failed — important
  for scripts used in automation or CI pipelines.

- if __name__ == "__main__": without this guard, any file that imports main.py would
  trigger the entire program to run. This is the standard Python protection against
  accidental execution on import.

- cities = [c.strip() for c in args.cities if c.strip()]: defensive cleaning of input.
  Before, you probably used args.cities directly without sanitizing. This guards against
  accidental whitespace-only strings being passed as city names.

WHAT NOT TO DO:
- Parse sys.argv manually with indexes (sys.argv[1], sys.argv[2], etc.)
- Put all logic directly inside main() — it becomes unreadable fast
- Skip sys.exit(1) on errors — silent failures are hard to debug in scripts
- Forget if __name__ == "__main__" — always include it in any entry point file
- Mix argument parsing, API calls, display, and export all in the same function
"""
import argparse
import sys

from weather.client import WeatherClient, WeatherAPIError
from weather.display import (
    print_weather_card,
    print_comparison_table,
    print_error,
    print_success,
    print_info,
)
from utils.logger import log_search
from utils.export import export_to_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="weather-cli",
        description="🌤️  WeatherCLI — Get current weather from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py Paris
  python main.py "New York" --export
  python main.py Paris London Tokyo --compare
  python main.py Tunis --export --output tunis_weather.json
        """,
    )
    parser.add_argument(
        "cities",
        nargs="+",
        help="One or more city names to look up",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Show a comparison table when querying multiple cities",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to a JSON file in the ./exports folder",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom filename for the JSON export (used with --export)",
    )
    return parser.parse_args()


def run_single(client: WeatherClient, city: str, export: bool, output: str) -> None:
    """Handle a single city lookup."""
    try:
        data = client.get_weather(city)
        print_weather_card(data)
        log_search(city, success=True, detail=f"{data.temperature}°C, {data.description}")

        if export:
            path = export_to_json(data, filename=output)
            print_success(f"Exported to {path}")

    except WeatherAPIError as e:
        print_error(str(e))
        log_search(city, success=False, detail=str(e))
        sys.exit(1)


def run_multiple(client: WeatherClient, cities: list[str], compare: bool, export: bool, output: str) -> None:
    """Handle multiple city lookups."""
    print_info(f"Fetching weather for: {', '.join(cities)}\n")
    results = client.get_multiple(cities)

    if not results:
        print_error("No results retrieved. Check your city names.")
        sys.exit(1)

    if compare:
        print_comparison_table(results)
    else:
        for data in results:
            print_weather_card(data)

    for data in results:
        log_search(data.city, success=True, detail=f"{data.temperature}°C")

    if export:
        path = export_to_json(results, filename=output)
        print_success(f"Exported {len(results)} results to {path}")


def main() -> None:
    args = parse_args()
    cities = [c.strip() for c in args.cities if c.strip()]

    try:
        client = WeatherClient()
    except WeatherAPIError as e:
        print_error(str(e))
        sys.exit(1)

    if len(cities) == 1:
        run_single(client, cities[0], args.export, args.output)
    else:
        run_multiple(client, cities, args.compare, args.export, args.output)


if __name__ == "__main__":
    main()
