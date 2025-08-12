import pickle
import streamlit as st

# Load data
movies_list = pickle.load(open('model.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = movies_list

# Recommendation function without posters
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies

# Streamlit UI
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox('Pick a movie to get recommendations...', movies['title'].values)

if st.button('Show Recommendation'):
    recommended_movie_names = recommend(selected_movie_name)
    for name in recommended_movie_names:
        st.text(name)
