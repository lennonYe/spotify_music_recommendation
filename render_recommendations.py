
import streamlit as st
import os
import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.express as px 
import matplotlib.pyplot as plt
from joblib import dump, load
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
from collections import defaultdict
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist

def find_song(name, year,sp):
    song_data = defaultdict()
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    song_data['name'] = [name]
    song_data['year'] = [year]
    song_data['explicit'] = [int(results['explicit'])]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]

    for key, value in audio_features.items():
        song_data[key] = value

    return pd.DataFrame(song_data).iloc[0]




number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']


def get_song_data(song, spotify_data, sp):
    
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name']) 
                                & (spotify_data['year'] == song['year'])].iloc[0]
        return song_data
    
    except IndexError:
        return find_song(song['name'], song['year'],sp)
        

def get_mean_vector(song_list, spotify_data,sp):
    
    song_vectors = []
    
    for song in song_list:
        song_data = get_song_data(song, spotify_data,sp)
        if song_data is None:
            print('Warning: {} does not exist in Spotify or in database'.format(song['name']))
            continue
        song_vector = song_data[number_cols].values
        print(f"Vector length for {song['name']}: {len(song_vector)}")  # 检查长度
        print(song_vector)
        song_vectors.append(song_vector)  
    
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)


def flatten_dict_list(dict_list):
    
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
            
    return flattened_dict


def recommend_songs( song_list, spotify_data,sp, n_songs=10):
    song_cluster_pipeline = load('recommendation_model.joblib')
    metadata_cols = ['name', 'year', 'artists']
    song_dict = flatten_dict_list(song_list)
    
    song_center = get_mean_vector(song_list, spotify_data,sp)
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(spotify_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])
    
    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
    return (rec_songs.to_dict(orient='records')) # 返回整行数据作为字典


def fetch_track_details(track_ids, sp):
    track_details = []
    tracks_info = sp.tracks(tracks=track_ids)
    for track in tracks_info['tracks']:
        details = {
            'name': track['name'],
            'year': track['album']['release_date'][:4],
            'artist': track['artists'][0]['name'],
            'image_url': track['album']['images'][0]['url'],
            'preview_url': track['preview_url'],
            'spotify_url': track['external_urls']['spotify'],
            'uri':track["uri"]
        }
        track_details.append(details)
    return track_details

def display_recommendation(user_data = None,sp = None):
    if st.session_state["need_login"] == False:
        data = pd.read_csv("Spotify_dataset/data.csv")
        top_tracks = user_data["top_tracks"]["items"]
        song_list = [{'name': track['name'], 'year': track['album']['release_date'][:4]} for track in top_tracks]
        song_list = [{'name': item['name'], 'year': int(item['year'])} for item in song_list]
        recommendation_song_list = recommend_songs(song_list,data,sp)
        track_ids = [track['id'] for track in recommendation_song_list]
        detailed_tracks = fetch_track_details(track_ids, sp)
        cols = st.columns(2)  # 创建两列布局
        for index, track in enumerate(detailed_tracks):
            with cols[index % 2]:  # 选择列，交替放置
                if st.session_state['premium']:
                    embed_url = f"https://open.spotify.com/embed/track/{track['uri'].split(':')[-1]}"
                    iframe = f"<iframe src='{embed_url}' width='100%' height='80' frameborder='0' allowtransparency='true' allow='encrypted-media'></iframe>"
                else:
                    preview_url = track.get('preview_url', 'No preview available')
                    iframe = f"<audio src='{preview_url}' controls>Your browser does not support the audio element.</audio>" if preview_url != 'No preview available' else "Preview not available."

                # 使用 HTML 和 CSS 创建一个卡片式布局
                st.markdown(f"""
                <div class="card" style="margin: auto; max-width: 550px; margin-bottom: 20px; text-align: center;">
                    <img class="image" src="{track['image_url']}" alt="{track['name']}" style="width: 100%; height: 550px; border-radius: 20px; object-fit: cover;">
                    <h4 style="margin-top: 10px;">{track['name']}</h4>
                    <p>{track['artist']}</p>
                    {iframe}
                </div>
                """, unsafe_allow_html=True)


