
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


def display_data_analysis():
    data = pd.read_csv('Spotify_dataset/data.csv')
    genre_data = pd.read_csv('Spotify_dataset/data_by_genres.csv')
    year_data = pd.read_csv('Spotify_dataset/data_by_year.csv')
    song_cluster_pipeline = load('recommendation_model.joblib')
    cluster_pipeline = load("genre_cluster_pipeline.joblib")
    st.title('Data Analysis Visualizations')
    
    # Features over year
    st.subheader('Features Over Years')
    fig = px.line(year_data, x='year', y=['acousticness', 'danceability', 'energy'])
    st.plotly_chart(fig,use_container_width=True)
    # Genre data
    st.subheader('Genre Characteristics')
    top10_genres = genre_data.nlargest(10, 'popularity')
    fig = px.bar(top10_genres, x='genres', y=['valence', 'energy', 'danceability', 'acousticness'], barmode='group')
    st.plotly_chart(fig,use_container_width=True)
    # K-Means on genre data visualization
    st.subheader('Clustering Genres with K-Means')
    X = genre_data.select_dtypes(np.number)
    cluster_pipeline.fit(X)
    genre_data['cluster'] = cluster_pipeline.predict(X)
    scaler = StandardScaler()
    tsne_pipeline = Pipeline([('scaler', StandardScaler()), ('tsne', TSNE(n_components=2, verbose=1))])
    genre_embedding = tsne_pipeline.fit_transform(X)
    projection = pd.DataFrame(columns=['x', 'y'], data=genre_embedding)
    projection['genres'] = genre_data['genres']
    projection['cluster'] = genre_data['cluster']
    fig = px.scatter(
        projection, x='x', y='y', color='cluster', hover_data=['x', 'y', 'genres'])
    st.plotly_chart(fig,use_container_width=True)

    st.subheader('Clustering Song titles with K-Means')
    X = data.select_dtypes(np.number)
    song_cluster_pipeline.fit(X)
    song_cluster_labels = song_cluster_pipeline.predict(X)
    data['cluster_label'] = song_cluster_labels
    pca_pipeline = Pipeline([('scaler', StandardScaler()), ('PCA', PCA(n_components=2))])
    song_embedding = pca_pipeline.fit_transform(X)
    projection = pd.DataFrame(columns=['x', 'y'], data=song_embedding)
    projection['title'] = data['name']
    projection['cluster'] = data['cluster_label']
    fig = px.scatter(
        projection, x='x', y='y', color='cluster', hover_data=['x', 'y', 'title'])
    st.plotly_chart(fig,use_container_width=True)
