import os
import telebot
from telebot import types
import dotenv
import requests

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_TOKEN = os.getenv("TMDB_API_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

class Movie:
    def __init__(self, genre):
        self.genre = genre
        self.year = None

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
    genre = movie_dict[message.chat.id]['genre']
    year = movie_dict[message.chat.id]['year']
    url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_genres={genre}&year={year}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_TOKEN}"
    }

    response = requests.get(url, headers=headers)


movie_dict = {}
movie_genres = get_genres("movie")
series_genres = get_genres("tv")


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

    except Exception as e:
        bot.reply_to(message, 'error')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
