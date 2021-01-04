# coding: utf-8

import bs4
import json
import re
import os
import logging
import string

from ibdb import settings
from ibdb.populate_db import fetch_binging_episode_list
from ibdb.recipe_parser import RecipeParser
from ibdb.utils import timeit, Stats

OUTPUT_DIR = settings.OUTPUT_DIR


class PopulateBabishJSON:

    def __init__(self):
        self.episodes = []
        self.stats = Stats({
            'episodes': 0,
            'bytes_written': 0,
        })

    @timeit
    def fetch_episode_list(self):
        # Fetch the current list of BWB episodes

        self.episodes = [e for e in fetch_binging_episode_list()]
        self.stats.episodes = len(self.episodes)

    @timeit
    def generate_babish_json(self):
        # Parse all episodes into babish.json

        episodes = []
        for episode in self.episodes:
            soup = bs4.BeautifulSoup(episode['body'], 'html.parser')

            ep = {
                'episode_name': episode['name'],
                'episode_link': episode['official_link'],
                'youtube_link': episode['youtube_link'],
                'published': episode['published_date'],
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
                        'method': method_name,
                        'ingredients': ingredients,
                    }

                    ep['recipes'].append(recipe)

            episodes.append(ep)

        with open(os.path.join(OUTPUT_DIR, 'babish.json'), 'w', encoding='utf8') as f:
            json.dump(episodes, f, indent=2, ensure_ascii=False)

        self.stats.bytes_written = os.path.getsize(os.path.join(OUTPUT_DIR, 'babish.json'))

        logging.info('Wrote babish.json successfully, %s bytes written', self.stats.bytes_written)

    def show_stats(self):
        print(self.stats)


def populate_babish_json():
    BABISH = PopulateBabishJSON()

    BABISH.fetch_episode_list()
    BABISH.generate_babish_json()

    BABISH.show_stats()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    populate_babish_json()
