import os
import pickle
import pandas as pd
import requests
import gzip # Use gzip for .pgz files
import numpy as np # Needed for array operations like de-quantization
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- TMDB API Configuration ---
# IMPORTANT: Replace 'YOUR_TMDB_API_KEY' with your actual TMDB API key.
# For production deployments, it's highly recommended to use environment variables:
# TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'YOUR_TMDB_API_KEY')
TMDB_API_KEY = '3e3ffe152a55d3764f508bfe8f5c9b83' # Replace this!
TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Placeholder image URL if a poster is not found or API call fails
PLACEHOLDER_IMAGE_URL = "https://placehold.co/500x750/cccccc/333333?text=No+Poster"

# Define the scaling factor for de-quantization (MUST MATCH the one used during compression)
DEQUANTIZATION_SCALE_FACTOR = 255.0

# --- Load data ---
try:
    # Load movies data
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)

    # Load the compressed and quantized similarity matrix
    # Ensure 'similarity_quantized.pgz' is in the same directory as app.py
    with gzip.open('similarity_quantized.pgz', 'rb') as f:
        similarity_matrix_quantized = pickle.load(f)

    # De-quantize the similarity matrix back to float32 for calculations
    # Convert uint8 integers back to floats between 0.0 and 1.0
    similarity_matrix = similarity_matrix_quantized.astype(np.float32) / DEQUANTIZATION_SCALE_FACTOR
    print(f"Similarity matrix loaded as numpy array with dtype: {similarity_matrix.dtype}")

    print("Data loaded successfully (movies_dict.pkl and similarity_quantized.pgz)!")

except FileNotFoundError as e:
    print(f"ERROR: File not found - {e.filename}. Please ensure all required data files "
          "('movies_dict.pkl', 'similarity_quantized.pgz') are in the same directory as app.py.")
    print("If 'similarity_quantized.pgz' is missing, run 'reduce_and_compress_data.py' first.")
    exit() # Exit the application if essential data files are missing
except Exception as e:
    print(f"ERROR: An unexpected error occurred while loading data files: {e}")
    exit()

# --- Helper function to fetch movie details (including poster path) from TMDB ---
def fetch_movie_details(movie_id):
    """
    Fetches movie details (title, poster_path) from TMDB API using movie ID.
    """
    if not TMDB_API_KEY or TMDB_API_KEY == 'YOUR_TMDB_API_KEY':
        print("Warning: TMDB_API_KEY is not set or is default. Cannot fetch movie posters.")
        return None

    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5) # Add a timeout for robustness
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        poster_path = data.get('poster_path')
        full_poster_url = f"{POSTER_BASE_URL}{poster_path}" if poster_path else PLACEHOLDER_IMAGE_URL
        return {
            'title': data.get('title'),
            'poster_url': full_poster_url
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for movie ID {movie_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching movie details: {e}")
        return None

# --- Recommendation function ---
def recommend(movie_title, movies_df, similarity_matrix):
    """
    Recommends movies based on the selected movie title and a precomputed similarity matrix,
    including fetching poster URLs.
    """
    if movie_title not in movies_df['title'].values:
        print(f"Movie '{movie_title}' not found in the dataset.")
        return []

    movie_index = movies_df[movies_df['title'] == movie_title].index[0]
    distances = similarity_matrix[movie_index]

    # Get the 5 most similar movies (excluding itself)
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies_details = []
    for i in movies_list:
        # Assuming your movies_df has a 'movie_id' column for TMDB IDs
        tmdb_movie_id = movies_df.iloc[i[0]].get('movie_id')

        movie_data = {
            'title': movies_df.iloc[i[0]].title,
            'poster_url': PLACEHOLDER_IMAGE_URL # Default to placeholder
        }

        if tmdb_movie_id:
            details = fetch_movie_details(tmdb_movie_id)
            if details and details.get('poster_url'): # Check if details and poster_url are valid
                movie_data['poster_url'] = details['poster_url']
            else:
                print(f"Could not fetch poster for '{movie_data['title']}' (ID: {tmdb_movie_id}), using placeholder.")
        else:
            print(f"No 'movie_id' found for '{movie_data['title']}'. Cannot fetch poster.")

        recommended_movies_details.append(movie_data)

    return recommended_movies_details

# --- Flask Routes ---
@app.route('/')
def index():
    """
    Renders the main index.html page.
    Passes the list of movie titles to the frontend for the dropdown.
    """
    movie_titles = movies_df['title'].tolist()
    return render_template('index.html', movie_titles=movie_titles)

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """
    Handles POST requests for movie recommendations.
    Expects 'movie_name' in the JSON request body.
    Returns a JSON array of recommended movies with titles and poster URLs.
    """
    data = request.get_json()
    selected_movie_name = data.get('movie_name')

    if not selected_movie_name:
        return jsonify({"error": "No movie name provided"}), 400

    recommended_movies = recommend(selected_movie_name, movies_df, similarity_matrix)
    return jsonify(recommended_movies)

# --- Run the Flask App ---
if __name__ == '__main__':
    # Use environment variable for port in production (e.g., Render)
    # Default to 5000 for local development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
