import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url_and_link(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        track_url = track["external_urls"]["spotify"]
        return album_cover_url, track_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", "#"

def recommend(song, num_recommendations=10):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music = []
    recommended_music_posters = []
    similarity_scores = []
    track_urls = []
    
    for i in distances[1:num_recommendations + 1]:
        artist = music.iloc[i[0]].artist
        song_name = music.iloc[i[0]].song
        album_cover_url, track_url = get_song_album_cover_url_and_link(song_name, artist)
        recommended_music_posters.append(album_cover_url)
        recommended_music.append((song_name, artist))
        similarity_scores.append(i[1])  # Append the similarity score
        track_urls.append(track_url)

    return recommended_music, recommended_music_posters, similarity_scores, track_urls

st.header('Symphony Scan')
music = pickle.load(open('df.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

# Create a list of "song by artist" for the dropdown
music_list = [f"{row['song']} by {row['artist']}" for _, row in music.iterrows()]

selected_song = st.selectbox(
    "Select your favourite song from the dropdown",
    music_list
)

if st.button('Show Recommendation'):
    # Extract the song name from the selected option
    selected_song_name = selected_song.split(' by ')[0]
    num_recommendations = 20  # Set the number of recommendations you want to display
    recommended_music, recommended_music_posters, similarity_scores, track_urls = recommend(selected_song_name, num_recommendations)
    
    num_cols = min(num_recommendations, 5)  # Limit to a maximum of 5 columns for better layout
    
    rows = (num_recommendations + num_cols - 1) // num_cols  # Calculate the number of rows needed
    
    for i in range(rows):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            index = i * num_cols + j
            if index < num_recommendations:
                song_name, artist = recommended_music[index]
                track_url = track_urls[index]
                cols[j].markdown(f"[{song_name} by {artist} (Similarity: {similarity_scores[index]:.2f})]({track_url})", unsafe_allow_html=True)
                cols[j].image(recommended_music_posters[index])