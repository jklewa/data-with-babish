# coding: utf-8

import bs4
import json
import re
import requests
import os
import time
import logging
import string

from functional import seq

from ibdb.recipe_parser import RecipeParser
from ibdb.utils import timeit, Stats


class PopulateBabishJSON:

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
            for _ in range(retries):
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
        youtube_pattern = re.compile(r'youtube.+v=([^#\&\?]+)')

        episodes = []
        for link in self.episode_links:
            path = 'tmp/raw-episodes/' + link.lstrip('/')
            with open(path, 'rb') as f:
                soup = bs4.BeautifulSoup(f, 'html.parser')

            episode_name = soup.title.string.strip().replace(' — Binging With Babish', '')

            youtube_link = (json.loads((soup.find('div', class_='video-block') or {}).get('data-block-json') or 'null') or {}).get('url')

            if not youtube_link:
                y_links = soup.find_all('a', href=youtube_pattern)
                youtube_link = None
                if y_links:
                    for yl in y_links:
                        m = re.search(youtube_pattern, yl['href'])
                        _youtube_link = 'https://www.youtube.com/watch?v=' + m.group(1)
                        if youtube_link and _youtube_link != youtube_link:
                            logging.warning(f'Multiple youtube links for ep: {link} {y_links}')
                            break
                        youtube_link = _youtube_link

            m = re.search(youtube_pattern, youtube_link or '')
            if m:
                youtube_link = 'https://www.youtube.com/watch?v=' + m.group(1)

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
                        method_name = episode_name

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
                            episode_name,
                            method_name,
                            list(iloc.children)
                        ))
                        raise

                    if len(ingredients) == 0:
                        print(
                            "WARN: Could not find ingredients for {0} (Episode {1})".format(
                                method_name, episode_name))

                    recipe = {
                        'method': method_name,
                        'ingredients': ingredients,
                    }

                    ep['recipes'].append(recipe)

            episodes.append(ep)

        with open('../datasets/babish.json', 'w', encoding='utf8') as f:
            json.dump(episodes, f, indent=2, ensure_ascii=False)

        self.stats.bytes_written = os.path.getsize('../datasets/babish.json')

        logging.info('Wrote babish.json successfully, %s bytes written', self.stats.bytes_written)

    def show_stats(self):
        print(self.stats)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    BABISH = PopulateBabishJSON()

    BABISH.fetch_episode_list()
    BABISH.fetch_missing_episodes()
    BABISH.generate_babish_json()

    BABISH.show_stats()
