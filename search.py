import requests
import random
import os
# Replace with your TMDb API Key
API_KEY = os.environ.get('API_KEY')
# Define TMDb endpoints
DISCOVER_MOVIE_ENDPOINT = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=en-US"


def get_random_movies(genre_id):
    # Fetch movies from the chosen genre
    params = {
        'with_genres': genre_id,
        'sort_by': 'popularity.desc',
        'page': random.randint(1, 10),  # Random page for variety top 200
    }
    response = requests.get(DISCOVER_MOVIE_ENDPOINT, params=params)
    movies = response.json().get('results', [])
    # Get 10 random movies from the results
    random_movies = random.sample(movies, min(10, len(movies)))
    # Print movie titles
    return random_movies