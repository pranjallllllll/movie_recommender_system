import os
import gdown
import pickle
import streamlit as st
import requests

# Google Drive file IDs
files = {
    "model.pkl": "1_aln5OR51Y3wnyjdjvJCMW5uZuvHRhBP",
    "similarity.pkl": "13aKOoUmbd1l11ichaiW_7hPzkLYDRYIN",
    "tmdb_5000_credits.csv": "1TxnI11HkLDRDegMvLGbtM_kMtHgWtV2D",
    "tmdb_5000_movies.csv": "17nlbJvCsQYm6wWKSK9QpsGbE7aQdjMXB"
}

# Download missing files once
for filename, file_id in files.items():
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=True)

# Load data with caching
@st.cache_resource
def load_data():
    movies_list = pickle.load(open('model.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies_list, similarity

movies, similarity = load_data()

# Fetch movie poster (cached)
@st.cache_data
def fetch_poster(movie_title):
    api_key = "2aa387840c2b9c8e525a08b63027343d"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0]['poster_path']
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Image"

# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list_idx = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list_idx:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))
    return recommended_movies, recommended_posters

# --- CHANGE 1: THE CSS IS UPDATED HERE ---
st.markdown(
    """
    <style>
    .responsive-title {
        font-weight: bold;
        color: white;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 1.5rem;   
    }
    @media (max-width: 720px) {
        .responsive-title {
            font-size: 1.4rem !important;  
        }
    }

    /* CSS FOR THE POSTER GLOW AND ZOOM EFFECT */
    .poster-container {
        position: relative;
        border-radius: 7px;
        overflow: hidden;
        /* This makes the zoom and glow effects smooth */
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .poster-container:hover {
        /* This creates the red neon glow */
        box-shadow: 0 0 25px rgba(229, 9, 20, 0.8);
        /* This makes the poster zoom in */
        transform: scale(1.05);
        /* This ensures the glowing poster appears on top of others */
        z-index: 10;
    }

    .poster-img {
        width: 100%;
        height: auto;
        display: block;
    }
    </style>
    
    <h2 class="responsive-title">🎬 Movie Recommender System</h2>
    """,
    unsafe_allow_html=True
)

selected_movie_name = st.selectbox(
    'Pick a movie to get recommendations...',
    movies['title'].values
)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            # --- CHANGE 2: THE POSTER DISPLAY LOGIC IS UPDATED HERE ---
            # We replace st.image() with st.markdown to apply our custom CSS classes.
            st.markdown(
                f"""
                <div class="poster-container">
                    <img class="poster-img" src="{poster}" alt="{name} Poster">
                </div>
                <p style='text-align:center; font-weight:bold; margin-top:8px;'>{name}</p>
                <br><br>
                """,
                unsafe_allow_html=True
            )
            # --- END OF THE CHANGE ---
