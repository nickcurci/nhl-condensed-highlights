import requests
from datetime import date
import time

# Function to fetch game data for a specific date
def fetch_game_data_by_date(selected_date):
    # Define the User-Agent header to mimic a web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    # Fetching game data for the selected date from the NHL API
    games = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?date={selected_date}', headers=headers)
    games = games.json()
    return games

# Function to fetch game media details for a specific game
def fetch_game_media_details(game_pk):
    # Define the User-Agent header to mimic a web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # Fetching game media details for a specific game using the game's unique ID (game_pk)
    game_url = f"http://statsapi.web.nhl.com/api/v1/game/{game_pk}/content"
    team_response = requests.get(game_url, headers=headers)
    js = team_response.json()

    return js

# Function to find the highest quality MP4 link
def find_highest_quality_mp4(game_media):
    highest_quality_mp4 = None

    # Loop through media items to find Extended Highlights
    for item in game_media['media']['epg']:
        if item['title'] == 'Extended Highlights':
            # Loop through video items under Extended Highlights
            for video_item in item['items']:
                if 'playbacks' in video_item and isinstance(video_item['playbacks'], list) and len(
                        video_item['playbacks']) > 0:
                    mp4_url = video_item['playbacks'][0]['url']
                    quality = video_item['playbacks'][0]['name']
                    # Check if the current MP4 URL has higher quality than the previous highest
                    if highest_quality_mp4 is None or quality > highest_quality_mp4[1]:
                        highest_quality_mp4 = (mp4_url, quality)

    return highest_quality_mp4

# Function to fetch the game text synopsis
def fetch_game_text_synopsis(game_media):
    text_synopsis = ""

    # Loop through media milestones to find text synopsis items
    for item in game_media['media']['milestones']['items']:
        if item['type'] == 'text':
            text_synopsis += item['headline'] + "\n" + item['description'] + "\n\n"

    return text_synopsis

# Function to find team ID by team name
def find_team_id_by_name(team_name):
    # Define the User-Agent header to mimic a web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # Fetching team data from the NHL API
    teams = requests.get('https://statsapi.web.nhl.com/api/v1/teams', headers=headers)
    teams = teams.json()

    for team in teams['teams']:
        if team['name'] == team_name:
            return team['id']

    return None

# Taking user input for team name(s) and date
user_input_team = input("Enter a team name (e.g., 'Boston Bruins') or skip to see all games: ")
user_input_date = input("Enter a date (YYYY-MM-DD): ")

# Check if user input is a valid date
try:
    if user_input_date:
        selected_date = date.fromisoformat(user_input_date)
        selected_date = selected_date.strftime('%Y-%m-%d')
        games = fetch_game_data_by_date(selected_date)

        if not games['dates'][0]['games']:
            print(f"No games were played on {selected_date}.")

        else:
            if user_input_team:
                print(f"Games for {user_input_team} on {selected_date}:")
                team_id = find_team_id_by_name(user_input_team)
            else:
                print(f"Games on {selected_date} for all teams:")
                team_id = None

            for game in games['dates'][0]['games']:
                home_team_name = game['teams']['home']['team']['name']
                away_team_name = game['teams']['away']['team']['name']

                if not team_id or team_id in (game['teams']['home']['team']['id'], game['teams']['away']['team']['id']):
                    print(f"{home_team_name} vs. {away_team_name}")
                    game_details = fetch_game_media_details(game['gamePk'])

                    # Extract and print condensed game, highlights, blurbs, highest quality MP4 link, and text synopsis
                    for item in game_details['media']['epg']:
                        if item['title'] == 'Extended Highlights':
                            print(f"Condensed Game: {item['items'][0]['title']}")
                            # print(f"Blurb: {item['items'][0]['blurb']}")
                            highest_quality_mp4 = find_highest_quality_mp4(game_details)
                            if highest_quality_mp4:
                                print(f"Highest Quality MP4 URL: {highest_quality_mp4[0]}")
                            for highlight in item['items'][1:]:
                                print(f"Highlight: {highlight['title']}")
                                # print(f"Blurb: {highlight['blurb']}")
                    print('')


    else:
        print("Please enter a valid date (YYYY-MM-DD).")

except ValueError:
    print("Invalid date format. Please enter a date in the format YYYY-MM-DD.")
