import json
import logging
import re

import bs4
import requests
from functional import seq
from furl import furl


def extract_inspired_by(name):
    inspired_by = re.match('.*(?:inspired by|from) (.+)$', name, re.IGNORECASE)
    if inspired_by:
        return [inspired_by[1].strip()]
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
