# coding: utf-8

import bs4
import json
import re
import requests
import os
import time

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
            qty = qty.strip()  # whitespace

            if len(qty) == 1:
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
        return capwords(name)        .strip(' \t\n\r,.')        .replace('Whole ', '')        .replace(
            'Half ', '')        .replace('Hot ', '')        .replace('Warm ', '')        .replace('Cold ', '').strip()


class BabishSync:

    def fetch_episode_list(self):
        # Fetch the current list of BWB episodes

        raw_episode_list = requests.get('https://www.bingingwithbabish.com/recipes/')
        soup = bs4.BeautifulSoup(raw_episode_list.content, 'html5lib')

        self.episode_links = seq(soup.find('div', class_='recipe-row').select('.main-image-wrapper a')
                                 )    .map(lambda atag: atag.get('href'))

    def fetch_missing_episodes(self):
        # Cache episodes/recipes content locally

        for link in self.episode_links:
            filename = 'tmp/raw-episodes/' + link.lstrip('/')

            if os.path.isfile(filename):
                continue  # skip, already cached

            retries = 3
            for t in range(retries):
                r = requests.get('https://www.bingingwithbabish.com' + link)
                if r.status_code == 200:
                    episodeHTML = r.content
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, "wb") as f:
                        f.write(episodeHTML)
                    break  # success
                else:
                    print("WARN: {0} returned bad status code ({1})".format(link, r.status_code))
                    time.sleep(10)
            else:
                print("ERROR: Too many retries on {0}".format(link))
            time.sleep(3)

    def generate_babish_json(self):
        # Parse all episodes into babish.json

        episodes = []
        for link in self.episode_links:
            path = 'tmp/raw-episodes/' + link.lstrip('/')
            with open(path, 'rb') as f:
                soup = bs4.BeautifulSoup(f, 'html.parser')

            episode_name = soup.title.string.strip().replace(' — Binging With Babish', '')

            youtube_link = json.loads(soup.find('div', class_='video-block')['data-block-json'])['url']

            ep = {
                'episode_name': episode_name,
                'episode_link': 'https://www.bingingwithbabish.com' + link,
                'youtube_link': youtube_link,
                'recipes': []
            }

            recipe_locations = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'], string=re.compile('Ingredients'))

            for loc in recipe_locations:
                method = loc.find_next(['h1', 'h2', 'h3', 'h4', 'h5'])
                if method:
                    method = method.string.strip()
                else:
                    method = 'Default - {}'.format(episode_name)

                ingredients = list(loc.find_next_sibling(['ul', 'ol']).children)

                if len(ingredients) > 0:
                    ingredients = list(seq(ingredients).map(parse_ingredient))
                else:
                    print("WARN: Could not location ingredients for {0} (Episode {1})".format(method, episode_name))

                recipe = {
                    'method': method,
                    'ingredients': ingredients,
                }

                ep['recipes'].append(recipe)

            episodes.append(ep)

        with open('babish.json', 'w') as f:
            json.dump(episodes, f, indent=2)
