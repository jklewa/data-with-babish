import psycopg2
import requests
import bs4
import logging
import json

from datetime import datetime
# from pprint import pprint
from functional import seq
from furl import furl

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def fetch_paginated_seq(base_url, route):
    items = []

    while route:
        link = furl(base_url + route).add({'format': 'json'})
        res = requests.get(link).json()

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


def fetch_binging_episode_list():
    # Fetch the current list of Binging with Babish episodes

    base_url = 'https://www.bingingwithbabish.com'
    route = '/recipes'

    raw_episode_list = fetch_paginated_seq(base_url, route)

    episodes = raw_episode_list.map(lambda raw: {
        'id': raw.get('urlId', None).split('/')[-1],
        'name': raw.get('title', None),
        'official_link': base_url + raw.get('fullUrl', ''),
        'youtube_link': extract_youtube_link(raw['body']),
        'published_date': timestamp_to_date(raw.get('publishOn', None)),
    })
    episode_count = sum(1 for x in episodes)

    logging.info('Fetched episode list, %s episodes', episode_count)
    return reversed(episodes.to_list())


def fetch_basics_episode_list():
    # Fetch the current list of Basics with Babish episodes

    base_url = 'https://basicswithbabish.co'
    route = '/basicsepisodes'

    raw_episode_list = fetch_paginated_seq(base_url, route)

    episodes = raw_episode_list.map(lambda raw: {
        'id': raw.get('urlId', None).split('/')[-1],
        'name': raw.get('title', None),
        'official_link': base_url + raw.get('fullUrl', ''),
        'youtube_link': extract_youtube_link(raw['body']),
        'published_date': timestamp_to_date(raw.get('publishOn', None)),
    })
    episode_count = sum(1 for x in episodes)

    logging.info('Fetched episode list, %s episodes', episode_count)
    return reversed(episodes.to_list())

conn = psycopg2.connect("dbname=babish_db user=postgres host=localhost port=54320")

EPISODES = fetch_binging_episode_list()

with conn.cursor() as cur:
    for ep in EPISODES:
        print("{published_date} | {name}".format(**ep))
        cur.execute("INSERT INTO episode (id, name, youtube_link, official_link, published_date, show_id) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET (name, youtube_link, official_link, published_date, show_id) = (EXCLUDED.name, EXCLUDED.youtube_link, EXCLUDED.official_link, EXCLUDED.published_date, EXCLUDED.show_id)",
                    (ep['id'], ep['name'], ep['youtube_link'], ep['official_link'], ep['published_date'], 1))

conn.commit()

EPISODES = fetch_basics_episode_list()

with conn.cursor() as cur:
    for ep in EPISODES:
        print("{published_date} | {name}".format(**ep))
        cur.execute("INSERT INTO episode (id, name, youtube_link, official_link, published_date, show_id) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET (name, youtube_link, official_link, published_date, show_id) = (EXCLUDED.name, EXCLUDED.youtube_link, EXCLUDED.official_link, EXCLUDED.published_date, EXCLUDED.show_id)",
                    (ep['id'], ep['name'], ep['youtube_link'], ep['official_link'], ep['published_date'], 2))

conn.commit()

print('Done')
