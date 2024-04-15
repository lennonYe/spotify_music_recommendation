import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import plotly.express as px

def map_hour_to_period(hour):
    if 0 <= hour < 6:
        return 'Night'
    elif 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    else:
        return 'Evening'


def extract_listening_patterns(listening_history):
    # Validate that listening_history has the correct data
    if 'items' in listening_history and len(listening_history['items']) > 0:
        # Extract 'played_at' from each track and create DataFrame
        df = pd.DataFrame([item['played_at'] for item in listening_history['items']], columns=['played_at'])
        df['played_at'] = pd.to_datetime(df['played_at'])
        df['hour'] = df['played_at'].dt.hour
        df['time_period'] = df['hour'].apply(map_hour_to_period)  # Map each hour to a time period
        df['weekday'] = df['played_at'].dt.day_name()
        
        time_period_counts = df['time_period'].value_counts().reindex(['Night', 'Morning', 'Afternoon', 'Evening'], fill_value=0)
        weekday_counts = df['weekday'].value_counts()
        
        return time_period_counts, weekday_counts
    else:
        st.error("No valid listening history data available.")
        return pd.Series(), pd.Series()
# def extract_listening_patterns(listening_history):
#     # 验证 listening_history 是否有正确的数据
#     if 'items' in listening_history and len(listening_history['items']) > 0:
#         # 从每个 track 中提取 'played_at' 并创建 DataFrame
#         df = pd.DataFrame([item['played_at'] for item in listening_history['items']], columns=['played_at'])
#         df['played_at'] = pd.to_datetime(df['played_at'])
#         df['hour'] = df['played_at'].dt.hour
#         df['weekday'] = df['played_at'].dt.day_name()
        
#         hour_counts = df['hour'].value_counts().sort_index()
#         weekday_counts = df['weekday'].value_counts()
        
#         return hour_counts, weekday_counts
#     else:
#         st.error("No valid listening history data available.")
#         return pd.Series(), pd.Series()
    
def display_home(user_info=None, user_data=None,genres_list = None,recently_played = None):
    plt.rcParams['font.family'] = 'Songti SC'
    st.markdown("# Home Page", unsafe_allow_html=True)
    # st.write("Keys in the first item of recently played:", first_item_keys)
    if user_info and user_data:
        st.markdown(f"<span style='font-size: 30px;'>Welcome, {user_info['display_name']}! 👋</span>", unsafe_allow_html=True)
        st.markdown("<h2><span style='font-size: 30px;'>Explore your music trends and insights below 🌟</span></h2>", unsafe_allow_html=True)
        if st.button('🌟 Generate your music trends and Insight! 🌟'):
            st.session_state["clicked"] = True

        if st.session_state["clicked"] == True:
            favorite_artist = user_data['top_tracks']['items'][0]['artists'][0]['name']
            favorite_genre = genres_list[0] if genres_list else "No data"
            # Extracting data for visualization
            top_tracks = user_data['top_tracks']
            top_artists = pd.DataFrame([track['artists'][0]['name'] for track in top_tracks['items']], columns=['artist'])

            artist_counts = top_artists['artist'].value_counts().head(10)
            # Show favorite artist and genre
            st.markdown(f"<span style='font-size: 24px;'>🌟 Rocking out mostly to <b>{favorite_artist}</b> these days! 🎤</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: 24px;'>🎶 Can't get enough of that <b>{favorite_genre}</b> vibe! 🎷</span>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h1 style='text-align: center; color:#B0BEC5'> Favorite Artists</h1>", unsafe_allow_html=True)
                plt.figure(figsize=(8, 6))
                ay = sns.barplot(x=artist_counts.index, y=artist_counts.values, palette='viridis')
                plt.title("Top 10 Artists")
                plt.ylabel('')
                plt.xlabel('')
                plt.yticks([])
                plt.xticks(rotation=45,fontsize=10)
                ay.yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure x-axis has only integer labels
                plt.ylabel('')
                plt.yticks([])
                st.pyplot(plt)

            top_genres = pd.DataFrame(genres_list, columns=['genres'])
            genre_counts = top_genres['genres'].value_counts().head(10)
            with col2:
                st.markdown("<h1 style='text-align: center; color:#B0BEC5'> Favorite Genres</h1>", unsafe_allow_html=True)
                plt.figure(figsize=(8, 6.2))
                by = sns.barplot(x=genre_counts.index, y=genre_counts.values, palette='coolwarm')
                plt.xticks(rotation=45,fontsize=10)
                plt.title("Top 10 Music Genres")
                plt.xlabel('')
                # plt.xlabel("Genres")
                by.yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure x-axis has only integer labels
                # plt.ylabel("Frequency")
                plt.ylabel('')
                plt.yticks([])
                st.pyplot(plt)

            st.markdown("<h2><span style='font-size: 30px;'>Explore your music listening time</span></h2>", unsafe_allow_html=True)
            # hour_counts, weekday_counts = extract_listening_patterns(recently_played)
            time_period_counts, weekday_counts = extract_listening_patterns(recently_played)
            most_listened_period = time_period_counts.idxmax()
            most_listened_day = weekday_counts.idxmax()

            st.markdown(f"<span style='font-size: 24px;'>You seem to groove the most during the **{most_listened_period}**! 🌙☀️</span>",unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: 24px;'>Looks like **{most_listened_day}** is your top day to chill with tunes! 🎵</span>",unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Listening Time Periods")
                plt.figure(figsize=(10, 6))
                sns.barplot(y=time_period_counts.index, x=time_period_counts.values, palette='viridis')
                plt.yticks(fontsize=15)
                plt.xlabel('')
                plt.ylabel('')
                st.pyplot(plt)

            with col2:
                st.markdown("### Listening Days")
                plt.figure(figsize=(10, 6))
                sns.barplot(y=weekday_counts.index, x=weekday_counts.values, palette='coolwarm')
                plt.ylabel('')
                plt.yticks(fontsize=15)
                plt.xlabel('')
                st.pyplot(plt)
            # Additional insights can be added here based on available data
    else:
        st.markdown("<p><span style='font-size: 30px;'>Welcome to the home page! Please login on the sidebar to continue.</span></p>", unsafe_allow_html=True)
