import json
from typing import List, Dict, Optional

MOVIE_FILE = 'movies.json'

def load_movies() -> List[Dict]:
    try:
        with open(MOVIE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_movies(movies: List[Dict]):
    with open(MOVIE_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=4, ensure_ascii=False)

def add_movie(movie: Dict):
    movies = load_movies()
    movies.append(movie)
    save_movies(movies)

def edit_movie(index: int, updated_movie: Dict) -> bool:
    movies = load_movies()
    if 0 <= index < len(movies):
        movies[index] = updated_movie
        save_movies(movies)
        return True
    return False

def delete_movie(index: int) -> bool:
    movies = load_movies()
    if 0 <= index < len(movies):
        movies.pop(index)
        save_movies(movies)
        return True
    return False

def get_movie(index: int) -> Optional[Dict]:
    movies = load_movies()
    if 0 <= index < len(movies):
        return movies[index]
    return None
