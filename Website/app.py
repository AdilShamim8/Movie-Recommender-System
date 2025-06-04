import pickle
import streamlit as st
import requests
from PIL import Image
import io
import base64

# Set page config
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon=None,
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        padding: 10px 25px;
        font-weight: bold;
    }
    .movie-title {
        font-size: 1.2em;
        font-weight: bold;
        color: white;
    }
    .movie-rating {
        color: #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url)
        data.raise_for_status()
        return data.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching movie details: {str(e)}")
        return None

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url)
        data.raise_for_status()
        data = data.json()
        poster_path = data['poster_path']
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {str(e)}")
        return None

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movies = []
        
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            movie_title = movies.iloc[i[0]].title
            movie_details = fetch_movie_details(movie_id)
            poster_url = fetch_poster(movie_id)
            
            if movie_details and poster_url:
                recommended_movies.append({
                    'title': movie_title,
                    'poster': poster_url,
                    'rating': movie_details.get('vote_average', 'N/A'),
                    'overview': movie_details.get('overview', 'No overview available'),
                    'release_date': movie_details.get('release_date', 'N/A')
                })
        
        return recommended_movies
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return []

# Header with custom styling
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Discover your next favorite movie!</p>", unsafe_allow_html=True)

# Load data
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Search functionality
search_query = st.text_input("Search for a movie", "")
if search_query:
    filtered_movies = movies[movies['title'].str.contains(search_query, case=False)]
    movie_list = filtered_movies['title'].values
else:
    movie_list = movies['title'].values

# Movie selection
selected_movie = st.selectbox(
    "Select a movie from the dropdown",
    movie_list
)

if st.button('Get Recommendations'):
    with st.spinner('Finding the perfect movies for you...'):
        recommended_movies = recommend(selected_movie)
        
        if recommended_movies:
            # Display selected movie details
            st.markdown("### Selected Movie")
            selected_movie_id = movies[movies['title'] == selected_movie]['movie_id'].iloc[0]
            selected_movie_details = fetch_movie_details(selected_movie_id)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(fetch_poster(selected_movie_id), use_container_width=True)
            with col2:
                st.markdown(f"### {selected_movie}")
                st.markdown(f"**Rating:** ⭐ {selected_movie_details.get('vote_average', 'N/A')}")
                st.markdown(f"**Release Date:** {selected_movie_details.get('release_date', 'N/A')}")
                st.markdown(f"**Overview:** {selected_movie_details.get('overview', 'No overview available')}")
            
            st.markdown("### Recommended Movies")
            cols = st.columns(5)
            
            for idx, movie in enumerate(recommended_movies):
                with cols[idx]:
                    st.image(movie['poster'], use_container_width=True)
                    st.markdown(f"<div class='movie-title'>{movie['title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='movie-rating'>⭐ {movie['rating']}</div>", unsafe_allow_html=True)
                    with st.expander("More Info"):
                        st.markdown(f"**Release Date:** {movie['release_date']}")
                        st.markdown(f"**Overview:** {movie['overview']}")
        else:
            st.warning("No recommendations found. Please try another movie.")
