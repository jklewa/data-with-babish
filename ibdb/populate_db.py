import psycopg2
import requests
import bs4
import logging
import json
import re
import string
import html

from datetime import datetime
# from pprint import pprint
from functional import seq
from furl import furl

YOUTUBE_ID_MATCHER = re.compile(
    r'^.*(?:(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/)|(?:(?:watch)?\?v(?:i)?=|\&v(?:i)?=))([^#\&\?]+).*')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def fetch_paginated_seq(base_url, route):
    items = []

    while route:
        link = furl(base_url + route).add({'format': 'json'})
        res = requests.get(link).json(encoding='utf-8')

        items += res.get('items', [])
        route = res.get('pagination', {}).get('nextPageUrl', None)

    return seq(items)


def timestamp_to_date(ts_in_milli):
    if not ts_in_milli:
        return None
    return datetime.fromtimestamp(ts_in_milli / 1000).strftime('%Y-%m-%d')


def extract_youtube_link(post_body):
    soup = bs4.BeautifulSoup(post_body, 'html.parser')
    youtube_link = json.loads(soup.find('div', class_='video-block')['data-block-json'])['url']
    return youtube_link


def extract_youtube_id(youtube_link):
    m = YOUTUBE_ID_MATCHER.match(youtube_link)
    return m.group(1) if m else ''


def add_youtube_resources(raw):
    raw_youtube_link = extract_youtube_link(raw['body'])
    youtube_id = extract_youtube_id(raw_youtube_link)

    if youtube_id:
        raw['youtube_id'] = youtube_id
        raw['youtube_link'] = f'https://www.youtube.com/watch?v={youtube_id}'
        raw['youtube_image_link'] = f'https://img.youtube.com/vi/{youtube_id}/mqdefault.jpg'
    else:
        raw['youtube_id'] = None
        raw['youtube_link'] = raw_youtube_link
        raw['youtube_image_link'] = None

    return raw


# def extract_recipe_method_names(post_body):
#     soup = bs4.BeautifulSoup(post_body, 'html.parser')
#     locations = soup.find_all(['p', 'h2', 'h3', 'h4', 'h5'])
#     locations = [loc for loc in locations if loc.find('strong')]

#     method_names = []

#     for loc in locations:
#         method_name = loc.get_text(strip=True)
#         method_name = re.sub('^(method|for the|for |the )', '', method_name, flags=re.IGNORECASE)
#         method_name = re.sub('(inspired by).+$', '', method_name, flags=re.IGNORECASE)
#         method_name = re.sub(r'\(.+\)', '', method_name, flags=re.IGNORECASE)
#         method_name = method_name.strip(string.whitespace + u'\u00a0:,')

#         method_names.append(method_name)

#     ignored = ('ingredients', 'shopping list', 'other ingredients', 'equipment list', 'special equipment list')

#     return [name for name in set(method_names) if name and name.lower() not in ignored and len(name) < 50]


def match_lists(ings, methods):
    if len(ings) == len(methods):
        return zip([[i] for i in ings], methods)

    return [
        ([i for i in ings if i.text in m.text], m)
        for m in methods
    ]


def fetch_binging_episode_list():
    # Fetch the current list of Binging with Babish episodes

    base_url = 'https://www.bingingwithbabish.com'
    route = '/recipes'

    raw_episode_list = fetch_paginated_seq(base_url, route)

    episodes = raw_episode_list.map(add_youtube_resources).map(lambda raw: {
        'id': raw.get('urlId', None).split('/')[-1],
        'name': html.unescape(raw.get('title', '')),
        'official_link': base_url + raw.get('fullUrl', ''),
        'youtube_link': raw['youtube_link'],
        'image_link': raw['youtube_image_link'] or raw.get('assetUrl', None),
        'published_date': timestamp_to_date(raw.get('publishOn', None)),
        'body': raw['body'],
    })
    episode_count = sum(1 for x in episodes)

    logging.info('Fetched episode list, %s episodes', episode_count)
    return reversed(episodes.to_list())


def fetch_basics_episode_list():
    # Fetch the current list of Basics with Babish episodes

    base_url = 'https://basicswithbabish.co'
    route = '/basicsepisodes'

    raw_episode_list = fetch_paginated_seq(base_url, route)

    episodes = raw_episode_list.map(add_youtube_resources).map(lambda raw: {
        'id': raw.get('urlId', None).split('/')[-1],
        'name': html.unescape(raw.get('title', '')),
        'official_link': base_url + raw.get('fullUrl', ''),
        'youtube_link': raw['youtube_link'],
        'image_link': raw['youtube_image_link'] or raw.get('assetUrl', None),
        'published_date': timestamp_to_date(raw.get('publishOn', None)),
        'body': raw['body'],
    })
    episode_count = sum(1 for x in episodes)

    logging.info('Fetched episode list, %s episodes', episode_count)
    return reversed(episodes.to_list())

conn = psycopg2.connect("dbname=babish_db user=postgres host=localhost port=54320")

EPISODES = fetch_binging_episode_list()

with conn.cursor() as cur:
    for ep in EPISODES:
        print("{published_date} | {name}".format(**ep))
        cur.execute("INSERT INTO episode (id, name, youtube_link, official_link, image_link, published_date, show_id) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET (name, youtube_link, official_link, image_link, published_date, show_id) = (EXCLUDED.name, EXCLUDED.youtube_link, EXCLUDED.official_link, EXCLUDED.image_link, EXCLUDED.published_date, EXCLUDED.show_id)",
                    (ep['id'], ep['name'], ep['youtube_link'], ep['official_link'], ep['image_link'], ep['published_date'], 1))

        # methods = extract_recipe_method_names(ep['body'])
        # print(' ' * 13 + ', '.join(methods))

conn.commit()

EPISODES = fetch_basics_episode_list()

with conn.cursor() as cur:
    for ep in EPISODES:
        print("{published_date} | {name}".format(**ep))
        cur.execute("INSERT INTO episode (id, name, youtube_link, official_link, image_link, published_date, show_id) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET (name, youtube_link, official_link, image_link, published_date, show_id) = (EXCLUDED.name, EXCLUDED.youtube_link, EXCLUDED.official_link, EXCLUDED.image_link, EXCLUDED.published_date, EXCLUDED.show_id)",
                    (ep['id'], ep['name'], ep['youtube_link'], ep['official_link'], ep['image_link'], ep['published_date'], 2))

        # methods = extract_recipe_method_names(ep['body'])
        # print(' ' * 13 + ', '.join(methods))

conn.commit()

print('Done')
