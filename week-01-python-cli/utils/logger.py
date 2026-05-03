"""
GOOD PRACTICES APPLIED:
- Standard logging module instead of print(): before, you might have used print()
  to track what your program was doing. The problem: print() goes to the terminal
  and disappears. The logging module writes to a persistent file with timestamps,
  levels, and formatting — automatically.

- setup_logger() with if not logger.handlers: logging.getLogger() always returns
  the same logger instance for the same name (it's a global registry). Without the
  if not logger.handlers guard, every call to setup_logger() would add another
  FileHandler to the same logger — and every message would be written 2x, 3x, 4x
  to the file. This one line prevents that duplication bug.

- log_search() as the only public interface: the rest of the project never touches
  logging configuration directly. It just calls log_search(city, success, detail).
  All the setup complexity is hidden inside.

WHAT NOT TO DO:
- Use print() for tracking program activity and search history
- Call logging.getLogger() and configure handlers directly in main.py
- Add handlers without checking if they already exist — you will get duplicate log lines
"""
import logging
import os
from datetime import datetime

LOG_FILE = "weather_history.log"


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("weather_cli")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_search(city: str, success: bool, detail: str = "") -> None:
    logger = setup_logger()
    status = "OK" if success else "FAIL"
    msg = f"[{status}] city='{city}'"
    if detail:
        msg += f" | {detail}"
    logger.info(msg)
