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

# Display posters with responsive layout
def display_posters_with_titles(names, posters):
    html_content = """
    <style>
    .poster-grid {
        display: flex;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
    }
    .poster-item {
        text-align: center;
    }
    .poster-item img {
        width: 180px;
        height: auto;
        border-radius: 10px;
    }
    .poster-title {
        color: white;
        font-weight: bold;
        margin-top: 5px;
    }

    /* Mobile layout: 3 posters top row, 2 posters centered bottom row */
    @media (max-width: 768px) {
        .poster-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            justify-items: center;
        }
        .poster-item:nth-child(4) {
            grid-column: 2; /* Center 4th item in second row */
        }
        .poster-item img {
            width: 100px;
        }
    }
    </style>
    <div class="poster-grid">
    """
    for name, poster in zip(names, posters):
        html_content += f"""
        <div class="poster-item">
            <img src="{poster}" alt="{name}">
            <div class="poster-title">{name}</div>
        </div>
        """
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)

# Streamlit UI with responsive title
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
    display_posters_with_titles(names, posters)
