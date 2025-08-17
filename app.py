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

# --- CSS MARGIN IS UPDATED IN THIS SECTION ---
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background-color: #000000;
    }

    /* CSS FOR THE ORANGE BUTTON */
    .stButton>button {
        color: white;
        background-color: #FF4500;
        border: none;
        padding: 8px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        font-weight: bold;
        /* THIS LINE IS CHANGED to set equal top/bottom margin */
        margin: 5px 0; 
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }

    /* This rule defines the button's style when you hover over it */
    .stButton>button:hover {
        background-color: #E03E00;
        color: white;
    }
    
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

    /* Poster hover effects */
    .poster-container {
        position: relative;
        border-radius: 7px;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .poster-container:hover {
        box-shadow: 0 0 25px rgba(229, 9, 20, 0.8);
        transform: scale(1.05);
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

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
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
