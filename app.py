import pickle
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """Fetch movie poster with retry logic and caching"""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Fetch movie data
            url = "https://api.themoviedb.org/3/movie/{}?api_key=0a00acf6602c982530b75381bb2bc2f4&language=en-US".format(movie_id)
            data = requests.get(url, timeout=15)
            data.raise_for_status()
            data = data.json()
            poster_path = data.get('poster_path')
            
            if poster_path:
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                # Try to actually fetch the image
                img_response = requests.get(full_path, timeout=15)
                img_response.raise_for_status()
                img = Image.open(BytesIO(img_response.content))
                return img
            else:
                return None
                
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed for movie_id {movie_id}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"All retries failed for movie_id {movie_id}")
                return None
    
    return None

def create_placeholder_image():
    """Create a placeholder image for movies without posters"""
    img = Image.new('RGB', (500, 750), color=(26, 26, 26))
    return img

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        if poster is None:
            poster = create_placeholder_image()
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


st.header('Movie Recommender System')
movies = pickle.load(open('movies.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    with st.spinner('Finding recommendations...'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    for idx, col in enumerate(columns):
        with col:
            st.text(recommended_movie_names[idx])
            st.image(recommended_movie_posters[idx], use_container_width=True)