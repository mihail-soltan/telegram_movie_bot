import os
import requests

TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")

def get_genres(content_type):
    url = f"https://api.themoviedb.org/3/genre/{content_type}/list?language=en"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    genres = response.json()['genres']
    return genres

def get_filtered_content(content_type, genre_id, year):
    try:
        url = f"https://api.themoviedb.org/3/discover/{content_type}?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_genres={genre_id}&primary_release_year={year}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_API_TOKEN}"
        }

        response = requests.get(url, headers=headers)
        content = response.json()['results']

        return content

    except Exception as e:
        print(e)