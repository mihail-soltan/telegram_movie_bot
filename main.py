import os
import telebot
from telebot import types, util
import dotenv
import requests
import json

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
img_base_path="https://image.tmdb.org/t/p/original"
# https://stackoverflow.com/questions/66915567/trying-to-get-backdrops-of-series-from-tmdb

class Movie:
    def __init__(self, genre):
        self.genre = genre
        self.year = None

    def __str__(self):
        return f"Genre: {self.genre}, Year: {self.year}"

class Series(Movie):
    pass

def get_genres(content_type):
    url = f"https://api.themoviedb.org/3/genre/{content_type}/list?language=en"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    genres = response.json()['genres']
    return genres

def get_filtered_movies(message):
    try:
        movie_object = movie_dict[message.chat.id]
        genre = movie_object.genre
        genre_id = movie_genres_lookup.get(genre)
        year = movie_object.year
        url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_genres={genre_id}&year={year}"
        print(url)
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_API_TOKEN}"
        }

        response = requests.get(url, headers=headers)
        movies = response.json()['results']

        return movies
    except Exception as e:
        print(e)


movie_dict = {}
movie_genres = get_genres("movie")
series_genres = get_genres("tv")

movie_genres_lookup = {genre['name']: genre['id'] for genre in movie_genres}
series_genres_lookup = {genre['name']: genre['id'] for genre in series_genres}

# TODO: implement filtering for matching genres in the genres_lookup

def filter_genres(pair):
    pass

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hey, what's up?")


@bot.message_handler(commands=['movies'])
def movie_handler(message):
    try:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        for genre in movie_genres:
            item_btn = types.KeyboardButton(genre['name'])
            markup.add(item_btn)
        text = "Pick a genre: "

        sent_msg = bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(sent_msg, year_handler)
    except Exception as e:
        bot.reply_to(message, 'error')

@bot.message_handler(commands=['series'])
def series_handler(message):
    try:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        for genre in series_genres:
            item_btn = types.KeyboardButton(genre['name'])
            markup.add(item_btn)
        text = "Pick a genre: "
        sent_msg = bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(sent_msg, year_handler)
    except Exception as e:
        bot.reply_to(message, 'error')

@bot.message_handler(commands=['year'])
def year_handler(message):
    try:
        chat_id = message.chat.id
        genre = message.text
        movie = Movie(genre)
        movie_dict[chat_id] = movie
        text = f"Pick a year: "
        sent_msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(sent_msg, pick_movie)
    except Exception as e:
        bot.reply_to(message, 'error')

@bot.message_handler(commands=['movie'])
def pick_movie(message):
    try:
        chat_id = message.chat.id
        year = message.text
        movie = movie_dict[chat_id]

        if year.isdigit():
            movie.year = year
        else:
            raise Exception("please use a number for the year")
        movie_list = get_filtered_movies(message)
        top_5 = movie_list[0:4]
        formatted_reply = "Here are some movies you might like:\n\n"
        bot.reply_to(message, formatted_reply)
        for m in top_5:
            title = m['original_title']
            poster = img_base_path+m['poster_path']
            overview = m['overview']
            rating = m['vote_average']
            formatted_reply += f"{poster}\nTitle: {title}\nOverview:{overview}\nRating:{rating}\n\n"
            bot.send_message(message.chat.id, f"{poster}\nTitle: {title}\nOverview:{overview}\nRating:{rating}\n\n")
        # split_text = util.split_string(formatted_reply, 3000)
        # for text in split_text:
        # bot.reply_to(message, formatted_reply)

    except Exception as e:
        print(e)
        bot.reply_to(message, 'error')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
