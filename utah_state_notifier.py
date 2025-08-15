import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

BASE_URL = "https://ncaa-api.henrygd.me/scoreboard"

SPORTS = {
    "football": {"division": "fbs", "conference": "mountain-west"},
    "soccer-women": {"division": "d1", "conference": "mountain-west"},
    "soccer-men": {"division": "d1", "conference": "mountain-west"},
    "basketball-men": {"division": "d1", "conference": "mountain-west"},
    "basketball-women": {"division": "d1", "conference": "mountain-west"},
    # Add more sports as needed
}

def fetch_games(sport, division, year, month, day, conference):
    url = f"{BASE_URL}/{sport}/{division}/{year}/{month}/{day}/{conference}"
    print(f"Fetching: {url}")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json().get("games", [])

def is_utah_state_win(game):
    status = game.get("status", {}).get("state")
    if status != "final":
        return False

    home = game.get("home", {})
    away = game.get("away", {})
    home_name = home.get("names", {}).get("short")
    away_name = away.get("names", {}).get("short")

    try:
        home_score = int(home.get("score", 0))
        away_score = int(away.get("score", 0))
    except ValueError:
        return False  # Skip if scores aren't numbers

    if home_name == "Utah St." and home_score > away_score:
        return True
    if away_name == "Utah St." and away_score > home_score:
        return True

    return False

def send_push_notification(message):
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        print("Missing Pushover credentials.")
        return

    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message
    })

    if r.status_code == 200:
        print("✅ Push notification sent.")
    else:
        print(f"❌ Push failed: {r.text}")

def check_sports_for_wins():
    today = datetime.now()
    year, month, day = today.strftime("%Y %m %d").split()

    for sport, info in SPORTS.items():
        games = fetch_games(sport, info["division"], year, month, day, info["conference"])
        for entry in games:
            game = entry.get("game", {})
            if is_utah_state_win(game):
                title = game.get("title", "Utah State Game")
                send_push_notification(f"🎉 Utah State won! {title}")

if __name__ == "__main__":
    check_sports_for_wins()
