import os
import yaml
from datetime import date, datetime

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    # Expand env vars
    for k, v in config.get("notifications", {}).items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_key = v[2:-1]
            config["notifications"][k] = os.getenv(env_key, "")

    return config

def get_football_week(weeks: dict, today: date = None) -> int:
    if today is None:
        today = date.today()
    elif isinstance(today, datetime):
        today = today.date()   # 🔑 normalize to date only

    # Sort by week number (keys are ints, values are ISO dates)
    sorted_weeks = sorted(weeks.items(), key=lambda x: int(x[0]))

    current_week = 1
    for week_num, start_date in sorted_weeks:
        start = date.fromisoformat(start_date)
        if today >= start:
            current_week = int(week_num)
        else:
            break

    return min(current_week, max(weeks.keys()))  # clamp to last week
