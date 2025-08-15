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

# Download missing files silently
for filename, file_id in files.items():
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=True)

# Load model and data
movies_list = pickle.load(open('model.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = movies_list

# Fetch movie poster from TMDB
def fetch_poster(movie_title):
    api_key = "2aa387840c2b9c8e525a08b63027343d"
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0]['poster_path']
        full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
        return full_path
    return "https://via.placeholder.com/500x750?text=No+Image"

# Recommendation function with posters
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

# Streamlit UI
st.markdown(
    """
    <style>
    .title-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
    .responsive-title {
        font-weight: bold;
        color: white;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 1.8rem;
    }
    @media (max-width: 768px) {
        .responsive-title {
            font-size: 1.5rem;
        }
    }
    </style>
    <div class="title-container">
        <h2 class="responsive-title">🎬 Movie Recommender System</h2>
    </div>
    """,
    unsafe_allow_html=True
)

selected_movie_name = st.selectbox(
    'Pick a movie to get recommendations...',
    movies['title'].values
)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie_name)
    
    # Create responsive layout using columns
    st.markdown("""
    <style>
    /* Mobile layout - 3 over 2 */
    @media (max-width: 768px) {
        .poster-columns {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .poster-column:nth-child(4) {
            grid-column: 2;
        }
        .poster-column:nth-child(5) {
            grid-column: 1 / span 3;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .poster-img {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create 5 columns (will automatically become 3-over-2 on mobile)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(
                posters[i],
                width=150,  # Fixed width for desktop
                use_container_width=True,  # Replaces deprecated use_column_width
                output_format="auto"
            )
            st.markdown(
                f"<div style='text-align: center; color: white; font-weight: bold;'>{names[i]}</div>",
                unsafe_allow_html=True
            )
