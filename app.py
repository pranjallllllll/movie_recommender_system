import os
import gdown
import pickle
import streamlit as st
import requests

# --- CORE LOGIC (UNCHANGED) ---

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
        with st.spinner(f"Downloading {filename}..."):
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


# --- NEW STREAMLIT UI (PRESENTATION LAYER) ---

# Inject custom CSS for the new UI
st.markdown(
    """
    <style>
    /* Main Title Style */
    .responsive-title {
        font-weight: bold;
        color: white;
        margin-bottom: 20px; /* Added margin for spacing */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 1.8rem;
    }

    /* Recommendation Button Style */
    .stButton>button {
        background-color: #8B0000; /* Dark Red */
        color: white;
        border: 2px solid #8B0000;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        width: 100%; /* Make button full width */
    }
    .stButton>button:hover {
        background-color: #A52A2A; /* Lighter red on hover */
        color: white;
        border-color: #8B0000;
    }
    .stButton>button:active {
        background-color: #6e0000; /* Even darker red when clicked */
    }

    /* Horizontal Carousel Container */
    .carousel-container {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        padding: 20px 10px;
        margin-top: 20px;
        scrollbar-width: thin;
        scrollbar-color: #8B0000 #1E1E1E;
    }
    /* For Webkit browsers like Chrome, Safari */
    .carousel-container::-webkit-scrollbar {
        height: 8px;
    }
    .carousel-container::-webkit-scrollbar-track {
        background: #2E2E2E;
        border-radius: 10px;
    }
    .carousel-container::-webkit-scrollbar-thumb {
        background-color: #8B0000;
        border-radius: 10px;
    }

    /* Individual Movie Card */
    .movie-card {
        display: inline-block;
        width: 180px;
        margin: 0 15px;
        text-align: center;
        vertical-align: top;
        flex-shrink: 0; /* Prevent cards from shrinking */
    }
    
    /* Poster container for hover effect */
    .poster-wrapper {
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.3s ease; /* Smooth transition on hover */
    }
    .poster-wrapper:hover {
        transform: scale(1.05); /* Slightly enlarge on hover */
        box-shadow: 0 0 25px 5px rgba(255, 20, 20, 0.7); /* Neon Red Glow */
    }
    .poster-wrapper img {
        display: block;
        width: 100%;
        border-radius: 10px;
    }
    
    /* Movie Title Style */
    .movie-title {
        font-weight: bold;
        color: white;
        margin-top: 10px;
        white-space: normal; /* Allow title to wrap */
        height: 3em; /* Limit title height to approx. 2 lines */
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 0.95rem;
    }

    /* Responsive adjustments */
    @media (max-width: 720px) {
        .responsive-title {
            font-size: 1.5rem !important;  
        }
        .movie-card {
            width: 150px;
            margin: 0 10px;
        }
    }
    </style>

    <h2 class="responsive-title">🎬 Movie Recommender System</h2>
    """,
    unsafe_allow_html=True
)

# UI Elements
selected_movie_name = st.selectbox(
    'Pick a movie to get recommendations...',
    movies['title'].values
)

if st.button('Show Recommendation'):
    with st.spinner('Finding similar movies...'):
        names, posters = recommend(selected_movie_name)

        # Building the HTML for the horizontal carousel dynamically
        carousel_html = "<div class='carousel-container'>"
        for name, poster in zip(names, posters):
            carousel_html += f"""
            <div class="movie-card">
                <div class="poster-wrapper">
                    <img src="{poster}" alt="{name} Poster">
                </div>
                <p class="movie-title">{name}</p>
            </div>
            """
        carousel_html += "</div>"

        # Displaying the dynamically generated carousel
        st.markdown(carousel_html, unsafe_allow_html=True)
