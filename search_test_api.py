import requests
import random
import sys
# Replace with your TMDb API Key
API_KEY = 'api_key'
# Define TMDb endpoints
GENRE_LIST_ENDPOINT = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=en-US"
DISCOVER_MOVIE_ENDPOINT = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=en-US"

# Get genre ID
response = requests.get(GENRE_LIST_ENDPOINT)
genres = response.json().get('genres', [])
# print(genres)
categories = {}
# for genre in genres:
#     print(genre['id'])
# sys.exit()
# Choose a genre (e.g., Action) and get its ID
genre_name = "Action"  # Change as needed
genre_id = next((genre['id'] for genre in genres if genre['name'].lower() == genre_name.lower()), None)

# If genre is not found, raise an error
if genre_id is None:
    raise ValueError(f"Genre '{genre_name}' not found.")

# Fetch movies from the chosen genre
params = {
    'with_genres': genre_id,
    'sort_by': 'popularity.desc',
    'page': random.randint(1, 10),  # Random page for variety
}

response = requests.get(DISCOVER_MOVIE_ENDPOINT, params=params)
movies = response.json().get('results', [])
print(movies[0])
# Get 10 random movies from the results
random_movies = random.sample(movies, min(10, len(movies)))

# Print movie titles
for movie in random_movies:
    print(movie['title'])
