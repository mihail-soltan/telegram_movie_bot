from datetime import datetime

def match_genres(id_to_name_lookup, item_genre_ids):
    return [id_to_name_lookup.get(gid) for gid in item_genre_ids if gid in id_to_name_lookup]

def convert_release_date(date):
    date_format = '%Y-%m-%d'
    datetime_str = datetime.strptime(date, date_format)
    day = datetime_str.strftime("%d")
    month = datetime_str.strftime("%B")
    year = datetime_str.strftime("%Y")
    formatted_release_date = f"{month} {day}, {year}"
    return formatted_release_date