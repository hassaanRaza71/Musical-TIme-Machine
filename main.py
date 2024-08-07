from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "9b88e9efe93e4e08bb3cfb1f170adb50"
CLIENT_SECRET = "43028c76062244a28d9822accc7c8fbf"

# Get the date from the user
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

# Fetch the Billboard Hot 100 page for the given date
response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{date}")
web_page = response.text
soup = BeautifulSoup(web_page, "html.parser")

# Extract all song titles
all_songs = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only", id="title-of-a-story")
number_one = soup.find(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet", id="title-of-a-story").getText()
number_one = number_one.replace("\n", "")
songs = [song.getText().replace("\n", "") for song in all_songs]
songs.insert(0, number_one)

# Authenticate with Spotify using OAuth
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://localhost:8888/callback",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

# Get the user's Spotify ID
user_id = sp.current_user()["id"]

# Search for each song on Spotify and collect their URIs
year = date.split("-")[0]
song_uris = []
for song in songs:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist on Spotify. Skipped.")

# Create a new private playlist
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard Hot 100", public=False)

# Add the found songs to the playlist
if song_uris:
    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
    print(f"Playlist created: {playlist['external_urls']['spotify']}")
else:
    print("No tracks found to add to the playlist.")
