"""
GOOD PRACTICES APPLIED:
- os.makedirs(EXPORT_DIR, exist_ok=True): before, you were probably checking manually
  if the folder existed before creating it (if not os.path.exists(...): os.mkdir(...)).
  exist_ok=True handles both cases in one line — create if missing, do nothing if present.

- os.path.join() for file paths: before, you were probably building paths with string
  concatenation ("exports/" + filename). This breaks on Windows which uses backslashes.
  os.path.join() is OS-agnostic and always produces the correct separator.

- Auto-generated timestamp filename: before, you were probably hardcoding a filename
  or asking the user for one every time. The timestamp approach guarantees uniqueness —
  you never accidentally overwrite a previous export.

- WeatherData | list[WeatherData] union type: one function handles both a single result
  and a list of results. Before, you might have written two separate functions, or worse,
  always wrapped a single result in a list just to have one code path.

- isinstance() to branch on type: the correct way to handle the union input. We check
  what we actually received and build the appropriate JSON structure for each case.

- json.dump() with indent=2 and ensure_ascii=False: before, you were probably dumping
  without indent (unreadable one-liner output) and without ensure_ascii=False (city
  names like "São Paulo" would be mangled into unicode escape sequences).

- with open() context manager: before, you might have used f = open() without with.
  The problem: if an exception occurs before f.close(), the file is never properly
  closed and can be corrupted. with guarantees the file is always closed.

WHAT NOT TO DO:
- Build file paths with string concatenation instead of os.path.join()
- Check folder existence manually instead of using exist_ok=True
- Call json.dump() without indent — the output is unreadable
- Open files without the with context manager
- Hardcode the export filename — you will overwrite previous results
"""
import json
import os
from datetime import datetime
from weather.models import WeatherData

EXPORT_DIR = "exports"


def export_to_json(data: WeatherData | list[WeatherData], filename: str = None) -> str:
    """
    Export one or multiple WeatherData objects to a JSON file.
    Returns the path of the created file.
    """
    os.makedirs(EXPORT_DIR, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weather_{timestamp}.json"

    filepath = os.path.join(EXPORT_DIR, filename)

    if isinstance(data, list):
        payload = {"count": len(data), "results": [d.to_dict() for d in data]}
    else:
        payload = data.to_dict()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return filepath
