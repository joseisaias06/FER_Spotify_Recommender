import spotipy
import yaml
from spotipy.oauth2 import SpotifyOAuth
from data_functions import offset_api_limit, get_artists_df, get_tracks_df, get_track_audio_df,\
    get_all_playlist_tracks_df, get_recommendations

#Cambiar Paths

with open(r'\spotify\spotify_details.yaml') as stream:
    spotify_details = yaml.safe_load(stream)

# https://developer.spotify.com/web-api/using-scopes/
scope = "user-library-read user-follow-read user-top-read playlist-read-private playlist-read-collaborative"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=spotify_details['client_id'],
    client_secret=spotify_details['client_secret'],
    redirect_uri=spotify_details['redirect_uri'],
    scope=scope,
))

# Spotify API calls and data manipulation
# Save for later to be quickly read by multiple workflows
print("Getting, transforming, and saving top artist data...")
top_artists = offset_api_limit(sp, sp.current_user_top_artists())
top_artists_df = get_artists_df(top_artists)
top_artists_df.to_pickle(r"\spotify\top_tracks.pkl")

print("Getting, transforming, and saving top track data...")
top_tracks = offset_api_limit(sp, sp.current_user_top_tracks())
top_tracks_df = get_tracks_df(top_tracks)
top_tracks_df = get_track_audio_df(sp, top_tracks_df)
top_tracks_df.to_pickle(r"\spotify\top_tracks.pkl")

print("Getting, transforming, and saving saved track data...")
saved_tracks = offset_api_limit(sp, sp.current_user_saved_tracks())
saved_tracks_df = get_tracks_df(saved_tracks)
saved_tracks_df = get_track_audio_df(sp, saved_tracks_df)
saved_tracks_df.to_pickle(r"\spotify\saved_tracks.pkl")

print("Getting, transforming, and saving playlist track data...")
playlist_tracks_df = get_all_playlist_tracks_df(sp, sp.current_user_playlists())  # limit of 50 playlists by default
playlist_tracks_df = get_track_audio_df(sp, playlist_tracks_df)
playlist_tracks_df.to_pickle(r"\spotify\playlist_tracks.pkl")
# Create yaml dump
playlist_dict = dict(zip(playlist_tracks_df['playlist_name'], playlist_tracks_df['playlist_id']))
with open(r'\spotify\playlists.yml', 'w') as outfile:
    yaml.dump(playlist_dict, outfile, default_flow_style=False)

print("Getting, transforming, and saving tracks recommendations...")
# Define a sample playlists to yield tracks to get recommendations for, 20 recommendations per track
# Change Playlist Name 
recommendation_tracks = get_recommendations(sp, playlist_tracks_df[playlist_tracks_df['playlist_name'].isin(
    ["Música Agropecuaria", "APPEASEMENT", "AT EASE", "DJing", "FIESTA ELITE"
     ])].drop_duplicates(subset='id', keep="first")['id'].tolist())
recommendation_tracks_df = get_tracks_df(recommendation_tracks)
recommendation_tracks_df = get_track_audio_df(sp, recommendation_tracks_df)
recommendation_tracks_df.to_pickle(r"\spotify\recommendation_tracks.pkl")
