import logging
import html

from ibdb.api import db
from ibdb.extract import fetch_paginated_seq, extract_inspired_by, \
    add_youtube_resources, extract_guests
from ibdb.models import upsert_episode, upsert_reference, upsert_episode_inspired_by, upsert_guest, \
    upsert_guest_appearance
from ibdb.utils import timestamp_to_date

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def fetch_binging_episode_list():
    # Fetch the current list of Binging with Babish episodes

    base_url = 'https://www.bingingwithbabish.com'
    route = '/recipes'

    raw_episode_list = fetch_paginated_seq(base_url, route)

    episodes = raw_episode_list.map(add_youtube_resources).map(lambda raw: {
        'id': raw.get('urlId', None).split('/')[-1],
        'show_id': 1,
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
        'show_id': 2,
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


def populate_binging(session):
    episodes = fetch_binging_episode_list()

    for ep in episodes:
        print("{published_date} | {name}".format(**ep))
        ep['id'] = upsert_episode(session, ep)

        inspiration_list = extract_inspired_by(ep['name'])
        for inspired_by in inspiration_list:
            ref = {
                'name': inspired_by,
            }
            ref['id'] = upsert_reference(session, ref)
            upsert_episode_inspired_by(session, ep['id'], ref['id'])

        guest_list = extract_guests(ep['name'])
        for guest in guest_list:
            guest = {
                'name': guest,
            }
            guest['id'] = upsert_guest(session, guest)
            upsert_guest_appearance(session, ep['id'], guest['id'])


def populate_basics(session):
    episodes = fetch_basics_episode_list()
    for ep in episodes:
        print("{published_date} | {name}".format(**ep))
        ep['id'] = upsert_episode(session, ep)

        guest_list = extract_guests(ep['name'])
        for guest in guest_list:
            guest = {
                'name': guest,
            }
            guest['id'] = upsert_guest(session, guest)
            upsert_guest_appearance(session, ep['id'], guest['id'])


def populate_db():
    session = db.session()

    populate_binging(session)
    populate_basics(session)

    session.commit()
    print('Done')


if __name__ == '__main__':
    populate_db()
