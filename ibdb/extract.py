import json
import logging
import re
import time

import string

import bs4
import requests
from functional import seq
from furl import furl

from ibdb.recipe_parser import RecipeParser

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


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
    num_requests = 1

    while route:
        r = None
        link = furl(base_url + route).add({'format': 'json'})
        try:
            r = requests.get(link)
            res = r.json(encoding='utf-8')

            items += res.get('items', [])
            route = res.get('pagination', {}).get('nextPageUrl', None)
            if route:
                time.sleep(1.5 ** num_requests)
                num_requests += 1
        except Exception:
            logging.error(f'Failed request: {link}')
            logging.error(f'Status code: {r is not None and r.status_code}')
            logging.error(f'Response:\n{r is not None and r.text}')
            raise

    return seq(items)


def match_lists(ings, methods):
    if len(ings) == len(methods):
        return zip([[i] for i in ings], methods)

    return [
        ([i for i in ings if i.text in m.text], m)
        for m in methods
    ]


def extract_recipes(episode):
    recipes = []
    soup = bs4.BeautifulSoup(episode['body'], 'html.parser')

    recipe_locations = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'], string=re.compile('Ingredients'))

    for loc in recipe_locations:
        ingredient_lists = loc.parent.find_all(['ul'])

        for iloc in ingredient_lists:
            # TODO: This logic is messy and brittle. Refactor it.

            # Get method name, usually right before the list itself
            method_name = iloc.find_previous_sibling(['p', 'h2', 'h3'])
            if method_name is not None:
                method_name = method_name.get_text().replace('Ingredients', '').strip(string.whitespace + '\u00a0:,')

            if method_name is None or method_name == '':
                # Look for the method name above the recipe instead
                h = iloc.parent.find_next(['h1', 'h2'])
                if h:
                    method_name = h.get_text().strip()
                    method_name = re.sub('^(Method)', '', method_name).strip(string.whitespace + '\u00a0:,')
                else:
                    # No luck, fall back to default
                    method_name = ''

            # Default to the episode name
            if method_name == '':
                method_name = episode['name']

            def flatten(loc):
                out = []
                for i in loc.children:
                    # flatten nested lists
                    if isinstance(i, bs4.element.Tag) and i.select('ul,ol'):
                        for i2 in i.select('ul,ol'):
                            out += flatten(i2)
                    else:
                        out.append(i)
                return out

            # Convert the ul to parsed Ingredients
            try:
                raw_ingredients = flatten(iloc)
                ingredients = [RecipeParser.parse_ingredient(i) for i in raw_ingredients]
            except Exception:
                print("ERROR: Failed to parse ingredients from ep: {0} method: {1} raw_list: {2}".format(
                    episode['name'],
                    method_name,
                    list(iloc.children)
                ))
                raise

            if len(ingredients) == 0:
                print(
                    "WARN: Could not find ingredients for {0} (Episode {1})".format(
                        method_name, episode['name']))

            recipe = {
                'name': method_name,
                'image_link': None,
                'raw_ingredient_list': '\n'.join(i.get_text().strip() for i in raw_ingredients),
                'raw_procedure': '',
                'episode_id': episode['id'],
            }
            recipes.append(recipe)

    return recipes
