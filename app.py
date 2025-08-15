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
    api_key = "2aa387840c2b9c8e525a08b63027343d"  # Replace with your TMDB API key
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

# Streamlit UI with responsive title
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
        text-align: center;
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
    movies['title'].values,
    key='movie_select'
)

if st.button('Show Recommendations', key='recommend_btn'):
    names, posters = recommend(selected_movie_name)
    
    # HTML/CSS for responsive grid
    html_content = """
    <style>
    /* Base styles for all devices */
    .poster-grid-container {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-top: 1.5rem;
    }
    .poster-grid {
        display: grid;
        justify-content: center;
        align-items: start;
        gap: 1.5rem;
    }
    .poster-item {
        text-align: center;
        transition: transform 0.2s;
    }
    .poster-item:hover {
        transform: scale(1.05);
    }
    .poster-img {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        object-fit: cover;
    }
    .poster-title {
        color: white;
        font-weight: bold;
        margin-top: 0.5rem;
        font-size: 1rem;
        text-align: center;
        padding: 0 0.5rem;
    }

    /* Desktop layout - 5 posters in a row */
    @media (min-width: 769px) {
        .poster-grid {
            grid-template-columns: repeat(5, 180px);
        }
        .poster-img {
            width: 180px;
            height: 270px;
        }
    }

    /* Mobile layout - 3 over 2 */
    @media (max-width: 768px) {
        .poster-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            width: 100%;
            max-width: 400px;
        }
        .poster-item:nth-child(1) {
            grid-column: 1;
            grid-row: 1;
        }
        .poster-item:nth-child(2) {
            grid-column: 2;
            grid-row: 1;
        }
        .poster-item:nth-child(3) {
            grid-column: 1;
            grid-row: 2;
        }
        .poster-item:nth-child(4) {
            grid-column: 2;
            grid-row: 2;
        }
        .poster-item:nth-child(5) {
            grid-column: 1 / span 2;
            grid-row: 3;
            justify-self: center;
            max-width: 180px;
        }
        .poster-img {
            width: 100%;
            height: auto;
            max-height: 240px;
        }
    }

    /* Very small mobile devices */
    @media (max-width: 400px) {
        .poster-grid {
            gap: 0.8rem;
        }
        .poster-title {
            font-size: 0.9rem;
        }
    }
    </style>

    <div class="poster-grid-container">
        <div class="poster-grid">
    """
    
    for i, (name, poster) in enumerate(zip(names, posters), start=1):
        html_content += f"""
            <div class="poster-item">
                <img class="poster-img" src="{poster}" alt="{name}" 
                     onerror="this.src='https://via.placeholder.com/180x270?text=Poster+Not+Found'">
                <div class="poster-title">{name}</div>
            </div>
        """
    
    html_content += """
        </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)

    # Add some spacing at the bottom
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
