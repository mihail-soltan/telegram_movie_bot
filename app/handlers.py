from telebot import types
from app.models import Content
from app.api_client import get_genres, get_filtered_content
from app.helpers import match_genres, convert_release_date
from app import bot

img_base_path="https://image.tmdb.org/t/p/original"

content_dict = {}

MOVIE_GENRES_LIST = get_genres("movie")
TV_GENRES_LIST = get_genres("tv")

MOVIE_GENRES_LOOKUP = {genre['name']: genre['id'] for genre in MOVIE_GENRES_LIST}
TV_GENRES_LOOKUP = {genre['name']: genre['id'] for genre in TV_GENRES_LIST}

ALL_GENRES_ID_TO_NAME_LOOKUP = {genre['id']: genre['name'] for genre in MOVIE_GENRES_LIST + TV_GENRES_LIST}

c1 = types.BotCommand(command='help', description='How the bot works')
c2 = types.BotCommand(command='movies', description='Get movies')
c3 = types.BotCommand(command='tv', description='Get tv-series')

bot.set_my_commands([c1, c2, c3])

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))
    welcome_text = (
        "<b>Hey, what's up?</b>\n\n"
        "I can help you find something to watch. "
        "Use the menu button or type one of the commands to get started:\n\n"
        "/movies - Get movie recommendations\n"
        "/tv - Get TV series recommendations"
    )
    bot.reply_to(message, welcome_text)
@bot.message_handler(commands=['movies', 'tv'])
def content_handler(message):
    try:
        chat_id = message.chat.id
        command = message.text[1:]

        if command == 'movies':
            content_type_for_api = 'movie'
            genres_for_markup = MOVIE_GENRES_LOOKUP.keys()
        else:
            content_type_for_api = 'tv'
            genres_for_markup = TV_GENRES_LOOKUP.keys()

        content_dict[chat_id] = Content(content_type=content_type_for_api)
        markup = types.ReplyKeyboardMarkup(row_width=2)

        for genre_name in genres_for_markup:
            markup.add(types.KeyboardButton(genre_name))

        text = "Pick a genre: "

        sent_msg = bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(sent_msg, year_handler)
    except Exception as e:
        bot.reply_to(message, 'error')

def year_handler(message):
    try:
        chat_id = message.chat.id
        genre = message.text

        user_content_object = content_dict[chat_id]
        user_content_object.genre = genre

        text = f"Pick a year: "
        sent_msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(sent_msg, pick_content)

    except Exception as e:
        bot.reply_to(message, 'error')

def pick_content(message):
    try:
        chat_id = message.chat.id
        user_content_object = content_dict[chat_id]
        year = message.text
        user_content_object.year = year
        genre_name = user_content_object.genre
        if user_content_object.content_type == 'movie':
            genre_id = MOVIE_GENRES_LOOKUP.get(genre_name)
        else:
            genre_id = TV_GENRES_LOOKUP.get(genre_name)
        if not genre_id:
            bot.reply_to(message, "Sorry, I couldn't recognize that genre.")
            return

        content_list = get_filtered_content(user_content_object.content_type, genre_id, user_content_object.year)
        if not content_list:
            bot.reply_to(message, f"Sorry, I couldn't find any results for {genre_name} in {year}.")
            return

        top_5 = content_list[:4]
        formatted_reply = "Here are some results you might like:\n\n"
        bot.reply_to(message, formatted_reply)

        for m in top_5:
            title = m.get('original_title') or m.get('original_name', 'Title Not Found')
            poster_path = m.get('poster_path')
            poster = f"<a href=\"{img_base_path + poster_path}\"> </a>" if poster_path else ""
            overview = m.get('overview', 'No overview available.')
            rating = m.get('vote_average', 'N/A')

            release_date_str = m.get('release_date') or m.get('first_air_date')
            release_date = convert_release_date(release_date_str) if release_date_str else "N/A"

            matched_genres = match_genres(ALL_GENRES_ID_TO_NAME_LOOKUP, m.get('genre_ids', []))
            genre_string = ", ".join(matched_genres)

            movie_card = f"{poster}\n<b>Title:</b> {title}\n<b>Overview:</b>\n{overview}\n<b>Genres:</b> {genre_string}\n<b>Release Date:</b> {release_date}\n<b>Rating:</b>{rating}\n\n"
            bot.send_message(message.chat.id, movie_card)

    except KeyError:
        bot.reply_to(message, "Looks like we had an issue. Please start again with /movies or /tv.")

    except Exception as e:
        print(f"Error in pick_content: {e}")
        bot.reply_to(message, 'error')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)