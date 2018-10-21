# coding: utf-8

import bs4
import json
import re
import requests
import os
import time
import logging

from collections import namedtuple
from fractions import Fraction
from functional import seq
from string import capwords
from unicodedata import numeric


class Recipe:

    Ingredient = namedtuple('Ingredient', 'qty unit name raw')
    units_pattern = r'(?:(\s?mg|g|kg|ml|L|oz|ounce|tbsp|Tbsp|tablespoon|tsp|teaspoon|cup|lb|pound|small|medium|large|whole|half)?(?:s|es)?\.?\b)'

    full_pattern = r'^(?:([-\.\/\s0-9\u2150-\u215E\u00BC-\u00BE]+)?{UNITS_PATTERN})?(?:.*\sof\s)?\s?(.+?)(?:,|$)'.format(
        UNITS_PATTERN=units_pattern)

    pattern = re.compile(full_pattern, flags=re.UNICODE)

    # https://en.wikipedia.org/wiki/Cooking_weights_and_measures#United_States_measures
    measures = {
        'drop': {'abrv': 'dr gt gtt', 'oz': 1.0 / 576},
        'smidgen': {'abrv': 'smdg smi', 'oz': 1.0 / 256},
        'pinch': {'abrv': 'pn', 'oz': 1.0 / 128},
        'dash': {'abrv': 'ds', 'oz': 1.0 / 64},
        'saltspoon': {'abrv': 'ssp scruple', 'oz': 1.0 / 32},
        'coffeespoon': {'abrv': 'csp', 'oz': 1.0 / 16},
        'dram': {'abrv': 'dr', 'oz': 1.0 / 8},
        'teaspoon': {'abrv': 'tsp t', 'oz': 1.0 / 6},
        'tablespoon': {'abrv': 'Tbsp T', 'oz': 1.0 / 2},
        'ounce': {'abrv': 'oz fl.oz', 'oz': 1.0},
        'wineglass': {'abrv': 'wgf', 'oz': 2.0},
        'teacup': {'abrv': 'tcf gill', 'oz': 4.0},
        'cup': {'abrv': 'C', 'oz': 8.0},
        'pint': {'abrv': 'pt', 'oz': 16.0},
        'quart': {'abrv': 'qt', 'oz': 32.0},
        'pottle': {'abrv': 'pot', 'oz': 64.0},
        'gallon': {'abrv': 'gal', 'oz': 128.0},
        'pound': {'abrv': 'lbs', 'oz': 16.0},
        'gram': {'abrv': 'g', 'oz': 0.035274},
        'kilogram': {'abrv': 'kg', 'oz': 35.274},
    }

    @classmethod
    def parse_ingredient(cls, i):
        if not isinstance(i, str):
            if i.string is None:
                # multiple tags in child,
                # bs4 gets confused per https://www.crummy.com/software/BeautifulSoup/bs4/doc/#string
                s = ' '.join(i.stripped_strings)
            else:
                s = i.string.strip()
        else:
            s = i
        raw = s.replace('\xa0', '').strip()

        clean = re.sub(r'\(.+?\)', '', raw).replace('’', "'")

        parsed = cls.pattern.match(clean)
        if parsed:
            qty, unit, name = parsed.groups()
        else:
            print("WARN: Unable to parse ingredient '{}'".format(raw))
            return cls.Ingredient(None, None, None, raw)

        qty = cls.normalize_qty(qty)

        unit = cls.normalize_unit(unit)

        name = cls.normalize_name(name)

        return cls.Ingredient(qty, unit, name, raw)

    @classmethod
    def normalize_qty(cls, qty):
        if qty is not None:
            qty = qty.strip()

            if len(qty) == 0:
                qty = None
            elif len(qty) == 1:
                qty = numeric(qty)
            else:
                try:
                    if '/' in qty:
                        # 2 1/2
                        qty = float(sum(Fraction(s) for s in qty.split()))
                    elif qty[-1].isdigit():
                        # normal number, ending in [0-9]
                        qty = float(qty)
                    else:
                        # Assume the last character is a vulgar fraction
                        qty = float(qty[:-1]) + numeric(qty[-1])
                except ValueError:
                    pass  # let it be a string
        return qty

    @classmethod
    def normalize_unit(cls, unit):
        if unit is not None:
            for u, d in cls.measures.items():
                if unit.lower() == u:
                    return u
                if unit in d['abrv'].split(' '):
                    return u
        return unit

    @classmethod
    def normalize_name(cls, name):
        return capwords(name) \
               .strip(',.') \
               .strip() \
               .replace('Whole ', '').replace('Half ', '') \
               .replace('Hot ', '').replace('Warm ', '').replace('Cold ', '') \
               .strip()


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logging.info('Time taken in %s  %2.2f ms' %
                         (method.__name__, (te - ts) * 1000))
        return result
    return timed


class Stats(object):

    def __init__(self, d):
        self.__dict__ = d

    def __repr__(self):
        return 'Stats:\n{0}'.format('\n'.join(' {0}: {1}'.format(stat, val) for stat, val in self.__dict__.items()))


class BabishSync:

    def __init__(self):
        self.stats = Stats({
            'episodes': 0,

            'episodes_fetched': 0,
            'episodes_already_cached': 0,
            'requests_made': 0,
            'requests_retried': 0,
            'requests_failed': 0,

            'bytes_written': 0,
        })

    @timeit
    def fetch_episode_list(self):
        # Fetch the current list of BWB episodes

        raw_episode_list = requests.get('https://www.bingingwithbabish.com/recipes/')
        soup = bs4.BeautifulSoup(raw_episode_list.content, 'html5lib')

        self.episode_links = seq(soup.find('div', class_='recipe-row').select('.main-image-wrapper a')
                                 ).map(lambda atag: atag.get('href'))
        self.stats.episodes = sum(1 for x in self.episode_links)

        logging.info('Fetched episode list, %s episodes', self.stats.episodes)

    @timeit
    def fetch_missing_episodes(self):
        # Cache episodes/recipes content locally

        for link in self.episode_links:
            filename = 'tmp/raw-episodes/' + link.lstrip('/')

            if os.path.isfile(filename):
                self.stats.episodes_already_cached += 1
                continue  # skip, already cached

            self.stats.episodes_fetched += 1

            retries = 3
            for t in range(retries):
                self.stats.requests_made += 1
                r = requests.get('https://www.bingingwithbabish.com' + link)
                if r.status_code == 200:
                    episodeHTML = r.content
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, "wb") as f:
                        f.write(episodeHTML)
                    break  # success
                else:
                    print("WARN: {0} returned bad status code ({1})".format(link, r.status_code))
                    self.stats.requests_retried += 1
                    time.sleep(10)
            else:
                print("ERROR: Too many retries on {0}".format(link))
                self.stats.requests_failed += 1
            time.sleep(3)

        logging.info(
            'Episode fetch complete - {episodes_fetched} fetched, {episodes_already_cached} already cached - {requests_made} requests, {requests_retried} retries {requests_failed} failed'.format(
                **self.stats.__dict__))

    @timeit
    def generate_babish_json(self):
        # Parse all episodes into babish.json

        episodes = []
        for link in self.episode_links:
            path = 'tmp/raw-episodes/' + link.lstrip('/')
            with open(path, 'rb') as f:
                soup = bs4.BeautifulSoup(f, 'html.parser')

            episode_name = soup.title.string.strip().replace(' — Binging With Babish', '')

            youtube_link = json.loads(soup.find('div', class_='video-block')['data-block-json'])['url']

            published = soup.find('time', class_='published')['datetime']

            ep = {
                'episode_name': episode_name,
                'episode_link': 'https://www.bingingwithbabish.com' + link,
                'youtube_link': youtube_link,
                'published': published,
                'recipes': []
            }

            recipe_locations = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'], string=re.compile('Ingredients'))

            for loc in recipe_locations:
                ingredient_lists = loc.parent.find_all(['ul'])

                for iloc in ingredient_lists:
                    # TODO: This logic is messy and brittle. Refactor it.

                    # Get method name, usually right before the list itself
                    method_name = iloc.find_previous_sibling(['p', 'h2', 'h3'])
                    if method_name is not None:
                        method_name = method_name.get_text().replace('Ingredients', '').strip('\u00a0:,').strip()

                    if method_name is None or method_name == '':
                        # Look for the method name above the recipe instead
                        h = iloc.parent.find_next(['h1', 'h2'])
                        if h:
                            method_name = h.get_text().strip()
                            method_name = re.sub('^(Method)', '', method_name).strip('\u00a0:,').strip()
                        else:
                            # No luck, fall back to default
                            method_name = ''

                    # Default to the episode name
                    if method_name == '':
                        method_name = episode_name

                    # Convert the ul to parsed Ingredients
                    try:
                        ingredients = [Recipe.parse_ingredient(i.get_text()) for i in iloc.children]
                    except Exception:
                        print("ERROR: Failed to parse ingredients from ep: {0} method: {1} raw_list: {2}".format(
                            episode_name,
                            method_name,
                            list(iloc.children)
                        ))
                        raise

                    if len(ingredients) == 0:
                        print("WARN: Could not find ingredients for {0} (Episode {1})".format(method_name, episode_name))

                    recipe = {
                        'method': method_name,
                        'ingredients': ingredients,
                    }

                    ep['recipes'].append(recipe)

            episodes.append(ep)

        with open('babish.json', 'w', encoding='utf8') as f:
            json.dump(episodes, f, indent=2, ensure_ascii=False)

        self.stats.bytes_written = os.path.getsize('babish.json')

        logging.info('Wrote babish.json successfully, %s bytes written', self.stats.bytes_written)

    def show_stats(self):
        print(self.stats)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    babish = BabishSync()

    babish.fetch_episode_list()
    babish.fetch_missing_episodes()
    babish.generate_babish_json()

    babish.show_stats()
