import json
import logging
import re

import bs4
import requests
from functional import seq
from furl import furl


def extract_inspired_by(name):
    for sub in ('"', '“', '...', 'Real Sample', 'Part II', 'Part I', 'Lots of Stuff', 'Duck Carbonara',
                'Cocktail Special', 'Subscriber Special'):
        name = name.replace(sub, ' ')
    inspired_by = re.match(r'.*(?:inspired by|from) ([^(|["“!;:]{2,}?)([(|["“!;:]|with|feat\.|$)', name, re.IGNORECASE & re.UNICODE)
    if inspired_by:
        inspiration_list = [i.strip() for i in re.split(r'\s(?:and(?! the| Rec))\s', inspired_by[1])]

        additional = re.match(r'.*\((?:and|plus) ([^\s]+.+)\)', name, re.IGNORECASE & re.UNICODE)
        if additional:
            inspiration_list.extend(i.strip() for i in re.split(r'\s(?:and(?! the))\s', additional[1]))

        return inspiration_list

    special = re.match(r'(.+) (?:Special|Volume I|Burger Cookoff$|Thanksgiving$)', name, re.IGNORECASE & re.UNICODE)
    if special:
        return [special[1].strip()]
    return []


def extract_guests(name):
    for sub in ('"', '“', '...', 'Homemade Ciabatta', 'with Babish', 'Wild Game inspired by Game of Thrones'):
        name = name.replace(sub, ' ')
    guest = re.match(r'.*(?:feat\.|featuring|with) ([^\s][^)]+)(?:$|\))', name, re.IGNORECASE & re.UNICODE)
    if guest:
        return [g.strip() for g in re.split(r'\s(?:and(?! the))\s', guest[1])]
    return []


YOUTUBE_ID_MATCHER = re.compile(
    r'^.*(?:(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/)|(?:(?:watch)?\?v(?:i)?=|\&v(?:i)?=))([^#\&\?]+).*')


def extract_youtube_link(post_body):
    soup = bs4.BeautifulSoup(post_body, 'html.parser')
    try:
        youtube_link = json.loads(soup.find('div', class_='video-block')['data-block-json'])['url']
        return youtube_link
    except Exception:
        pass

    try:
        youtube_link = None
        y_links = soup.find_all('a', href=YOUTUBE_ID_MATCHER)
        for yl in y_links:
            m = re.search(YOUTUBE_ID_MATCHER, yl['href'])
            _youtube_link = 'https://www.youtube.com/watch?v=' + m.group(1)
            if youtube_link and _youtube_link != youtube_link:
                logging.warning(f'Multiple youtube links for ep: {y_links}')
                break
            youtube_link = _youtube_link
        return youtube_link or ''
    except Exception:
        return ''


def extract_youtube_id(youtube_link):
    if youtube_link:
        m = YOUTUBE_ID_MATCHER.match(youtube_link)
        return m.group(1) if m else ''
    else:
        return ''


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


def fetch_paginated_seq(base_url, route):
    items = []

    while route:
        link = furl(base_url + route).add({'format': 'json'})
        res = requests.get(link).json(encoding='utf-8')

        items += res.get('items', [])
        route = res.get('pagination', {}).get('nextPageUrl', None)

    return seq(items)


def match_lists(ings, methods):
    if len(ings) == len(methods):
        return zip([[i] for i in ings], methods)

    return [
        ([i for i in ings if i.text in m.text], m)
        for m in methods
    ]
