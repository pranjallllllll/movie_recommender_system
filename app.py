import os
import gdown
import pickle
import streamlit as st

files = {
    "model.pkl": "1_aln5OR51Y3wnyjdjvJCMW5uZuvHRhBP",
    "similarity.pkl": "13aKOoUmbd1l11ichaiW_7hPzkLYDRYIN",
    "tmdb_5000_credits.csv": "1TxnI11HkLDRDegMvLGbtM_kMtHgWtV2D",
    "tmdb_5000_movies.csv": "17nlbJvCsQYm6wWKSK9QpsGbE7aQdjMXB"
}

for filename, file_id in files.items():
    if not os.path.exists(filename):
        st.write(f"Downloading {filename}...")
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=False)

movies_list = pickle.load(open('model.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = movies_list

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies

# Streamlit UI
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
            font-size: 1.2rem !important;
        }
    }
    </style>
    <h2 class="responsive-title">🎬 Movie Recommender System</h2>
    """,
    unsafe_allow_html=True
)


selected_movie_name = st.selectbox('Pick a movie to get recommendations...', movies['title'].values)

if st.button('Show Recommendation'):
    recommended_movie_names = recommend(selected_movie_name)
    for name in recommended_movie_names:
        st.text(name)








