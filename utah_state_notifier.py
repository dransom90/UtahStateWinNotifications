import os
import requests
from datetime import datetime, date
from dotenv import load_dotenv
import time
from config_loader import load_config, get_football_week

# Load .env variables
load_dotenv()
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

config = load_config()
today = date.today()

BASE_URL = "https://ncaa-api.henrygd.me/scoreboard"


def fetch_games(sport: str, division: str, year: int, month: int, day: int, conference: str, week: int = None):
    if sport == "football":
        if week is None:
            raise ValueError("Football requires a 'week' number (1–15)")
        url = f"https://ncaa-api.henrygd.me/scoreboard/{sport}/{division}/{year}/{week}"
    else:
        url = f"https://ncaa-api.henrygd.me/scoreboard/{sport}/{division}/{year}/{month}/{day}/{conference}"

    try:
        print(f"calling url: {url}")
        resp = requests.get(url, timeout=10)
        if resp.status_code == 404:
            print("No games found")
            return []
        resp.raise_for_status()
        data = resp.json()
        return data.get("games", [])
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching games from {url}: {e}")
        return []

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
    print(f"Checking for USU wins for {today}")

    #Uncomment for debugging push notifications
    #send_push_notification("Starting check for USU wins")
    year, month, day = today.strftime("%Y %m %d").split()

    for sport, info in config["sports"].items():
        print(f"checking {sport}")
        if sport == "football":
            week = get_football_week(info["weeks"], today)
            games = fetch_games(sport, info["division"], today.year, None, None, config["conference"], week=week)
        else:
            games = fetch_games(sport, info["division"], today.year, today.month, today.day, config["conference"])
            for entry in games:
                game = entry.get("game", {})
                if is_utah_state_win(game):
                    title = game.get("title", "Utah State Game")
                    send_push_notification(f"🎉 Utah State won! {title}")
        # Sleep 0.3s between calls → max ~3 calls per second
        time.sleep(0.3)

if __name__ == "__main__":
    check_sports_for_wins()
