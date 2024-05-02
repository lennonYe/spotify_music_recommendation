import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from urllib.parse import urlparse, parse_qs
from joblib import dump, load
from streamlit_option_menu import option_menu
from render_home import display_home
from render_top_tracks import display_top_tracks
from render_top_tracks import display_user_favorite_in_sidebar
from render_data_analysis import display_data_analysis
from render_recommendations import display_recommendation
import pandas as pd
import matplotlib



if __name__ == "__main__":
    # define the scope according to your requirement
    scope = 'user-library-read playlist-read-private user-top-read user-read-recently-played user-read-private'
    user_data = {}
    cache_path = ".spotifycache"
    # set page configuration
    st.set_page_config(
    page_title="Spotify analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Spotify recommendation system. This is an *extremely* cool app!"
    }
    )

    auth_manager = SpotifyOAuth(
        scope=scope,
        client_id=os.environ['SPOTIPY_CLIENT_ID'],
        client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
        redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'],
        show_dialog=True,
        cache_path= cache_path
    )
    # Initialize session state
    if 'auth_manager' not in st.session_state:
        st.session_state['auth_manager'] = auth_manager
    if 'need_login' not in st.session_state:
        st.session_state['need_login'] = True
    if 'clicked' not in st.session_state:
        st.session_state['clicked'] = False
    if 'premium' not in st.session_state:
        st.session_state['premium'] = False

    if st.query_params.get_all('code'):
        code = st.query_params.get_all('code')
        token = auth_manager.get_access_token(code)
        if token:
            st.session_state['auth_token'] = token
            st.query_params.clear() 
            st.session_state['need_login'] = False

    # Check login status
    if st.session_state['need_login']:
        auth_url = auth_manager.get_authorize_url()
        login_button_html = f"<a href='{auth_url}' target='_blank'><button style='color: white; background-color: #1DB954; border: none; padding: 10px 20px; text-align: center; display: inline-block; font-size: 18px; border-radius: 18px; width: 250px; cursor: pointer;'>Login using Spotify</button></a>"
        st.sidebar.markdown(login_button_html, unsafe_allow_html=True)
    else:
        # User is logged in, fetch user data and update sidebar content
        sp = spotipy.Spotify(auth_manager=auth_manager)
        user_data = {
            'top_tracks': sp.current_user_top_tracks(limit=20),
            'playlists': sp.current_user_playlists(limit=20)
        }
        user_info = sp.current_user()
        product_type = user_info['product']


        # check for premium
        st.session_state['premium'] = product_type == 'premium'
    

        if st.sidebar.button('Logout'):
            st.session_state['need_login'] = True
            if os.path.exists(cache_path):
                os.remove(cache_path)
            st.session_state.pop('auth_manager', None)
            st.session_state.clear()
            st.rerun() 


    with st.sidebar:
        selected = option_menu("Menu", ["Home", "Top Tracks", "Recommendations", "Data Analysis"],
                            icons=['house', 'music-note-list', 'heart-fill', 'graph-up'],
                            menu_icon="cast", default_index=0)
    # st.balloons()

    # Display content based on selected menu item
    if selected == "Home":
        if st.session_state['need_login'] == False:
            recently_played = sp.current_user_recently_played()

            artist_ids = [track['artists'][0]['id'] for track in user_data["top_tracks"]['items']]
            genres_list = []

            for artist_id in artist_ids:
                artist_info = sp.artist(artist_id)
                genres = artist_info['genres']
                genres_list.extend(genres) 
            display_home(user_info,user_data,genres_list, recently_played)
        else:
            display_home()
    elif selected == "Top Tracks":
        if st.session_state['need_login'] == False:
            display_top_tracks(user_data['top_tracks'])
        else:
            display_top_tracks()

    elif selected == "Recommendations":
        if st.session_state['need_login'] == False:
            display_recommendation(user_data,sp)
        else:
            display_top_tracks()
    elif selected == "Data Analysis":
        display_data_analysis()

    if st.session_state.get('show_sidebar_player'):
        user_favorite_track = user_data['top_tracks']['items'][0] if user_data['top_tracks']['items'] else None
        favorite_track_info = {
                'name': user_favorite_track['name'],
                'artist': user_favorite_track['artists'][0]['name'],
                'spotify_uri': user_favorite_track['uri']
            }
        display_user_favorite_in_sidebar(favorite_track_info)


    