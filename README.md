# _Data with Babish_

This project aims to analyze the recipes of the popular YouTube channel [Binging with Babish](http://bingingwithbabish.com) and convert them into beautiful data.

## Visualizations

* [jklewa/data-with-babish-example](https://github.com/jklewa/data-with-babish-example) - An interactive episode data viewer [Demo](https://jklewa.github.io/data-with-babish-example/)

## Datasets

 * [ibdb.episodes.json](#ibdbepisodesjson) - Episodes and related guests, recipes and inspiration
 * [ibdb.guests.json](#ibdbguestsjson) - Guests and their appearances
 * [ibdb.recipes.json](#ibdbrecipesjson) - Recipes and their origin episode
 * [ibdb.references.json](#ibdbreferencesjson) - TV Shows, Movies, etc. and when they were referenced
 * [ibdb.shows.json](#ibdbshowsjson) - Babish's Shows and their episode lists
 * [babish.json](#babishjson) - Parsed recipe ingredients, grouped by episode (Deprecated)

### ibdb.episodes.json

  **Episodes** and related guests, recipes and inspiration in the format:

  ```python
  [
    {
      "episode_id": "epid",
      "name": "Episode Name",
      "published_date": "YYYY-MM-DDT00:00:00+00:00",
      "youtube_link": "https://www.youtube.com/watch?v=...",
      "official_link": "https://www.bingingwithbabish.com/recipes/...",
      "image_link": "https://preview.image.host/image.png",
      "related": {
        "show": {
          "show_id": 1,
          "name": "Binging with Babish"
        },
        "guests": [
          {
            "guest_id": 1,
            "name": "Guest Name"
          }
        ],
        "inspired_by": [
          {
            "reference_id": 1,
            "type": "tv_show|movie|youtube_channel|video_game|other",
            "name": "Reference Name",
            "description": "A description of the reference.",
            "external_link": "https://link.to.more/"
          }
        ],
        "recipes": [
          {
            "recipe_id": 1,
            "name": "Recipe Name",
            "raw_ingredient_list": "Ingedient 1\nIngredient 2\n...",
            "raw_procedure": "Step 1.\nStep 2.\n..."
          }
        ]
      }
    },
    # ...
  ]
  ```

### ibdb.guests.json

  **Guests** and their appearances in the format:

  ```python
  [
    {
      "guest_id": 1,
      "name": "Guest Name",
      "appearances": [
        {
          "episode_id": "epid",
          "name": "Episide Name",
          "published_date": "YYYY-MM-DDT00:00:00+00:00",
          "youtube_link": "https://www.youtube.com/watch?v=...",
          "official_link": "https://www.bingingwithbabish.com/recipes/...",
          "image_link": "https://preview.image.host/image.png"
        }
      ]
    },
    # ...
  ]
  ```

### ibdb.recipes.json

  **Recipes** and their origin episode in the format:

  ```python
  [
    {
      "recipe_id": 1,
      "name": "Recipe Name",
      "raw_ingredient_list": "Ingedient 1\nIngredient 2\n...",
      "raw_procedure": "Step 1.\nStep 2.\n...",
      "source": {
        "episode_id": "epid",
        "name": "Episide Name",
        "published_date": "YYYY-MM-DDT00:00:00+00:00",
        "youtube_link": "https://www.youtube.com/watch?v=...",
        "official_link": "https://www.bingingwithbabish.com/recipes/...",
        "image_link": "https://preview.image.host/image.png"
      }
    },
    # ...
  ]
  ```

### ibdb.references.json

  TV Shows, Movies, etc. **References** and when they were referenced in the format:

  ```python
  [
    {
      "reference_id": 1,
      "type": "tv_show|movie|youtube_channel|video_game|other",
      "name": "Reference Name",
      "description": "A description of the reference.",
      "external_link": "https://link.to.more/",
      "episodes_inspired": [
        {
          "episode_id": "epid",
          "name": "Episide Name",
          "published_date": "YYYY-MM-DDT00:00:00+00:00",
          "youtube_link": "https://www.youtube.com/watch?v=...",
          "official_link": "https://www.bingingwithbabish.com/recipes/...",
          "image_link": "https://preview.image.host/image.png"
        }
      ]
    },
    # ...
  ]
  ```

### ibdb.shows.json

  **Babish's Shows** and their episode lists in the format:

  ```python
  [
    {
      "show_id": 1,
      "name": "Binging with Babish",
      "episodes": [
        {
          "episode_id": "epid",
          "name": "Episide Name",
          "published_date": "YYYY-MM-DDT00:00:00+00:00",
          "youtube_link": "https://www.youtube.com/watch?v=...",
          "official_link": "https://www.bingingwithbabish.com/recipes/...",
          "image_link": "https://preview.image.host/image.png"
        }
      ]
    },
    # ...
  ]
  ```

### babish.json

  **(Deprecated)**

  Contains ingredients from [BWB Recipes](http://bingingwithbabish.com/recipes) in the format:

  ```python
  [
    {
      "episode_name": "Episode Name",
      "episode_link": "https://www.bingingwithbabish.com/recipes/...",
      "youtube_link": "https://www.youtube.com/watch?v=...",
      "published": "YYYY-MM-DD",
      "recipes": [
        {
          "method": "Method Name (from Episode Name)",
          "ingredients": [
            [
              1.0,                   # quantity
              "tablespoon",          # unit
              "Butter",              # name
              "1 tablespoon butter"  # raw text from recipe
            ],
            # ...
          ]
        },
        # ...
      ]
    },
    # ...
  ]
  ```

### Resources

* Regex Samples: https://regexr.com/3p7h8 https://regexr.com/3p6pq
* Handling Unicode Fractions: https://stackoverflow.com/questions/1263796/how-do-i-convert-unicode-characters-to-floats-in-python

## Contributing

### Local Development
Required tools: **Python 3**

1. Install packages `pip install -r requirements.txt`
2. Run tests `pytest test/`
3. Scrape and parse `python extract_recipes.py`

You can also explore the script's original version and other data analysis with [Jupyter Notebook](http://ipython.org/notebook.html)
1. `cd notebooks/`
2. Start Jupyter on [http://localhost:8888](http://localhost:8888) `jupyter notebook`
3. Open `Babish Recipe Extract.ipynb` or `Babish Data Analysis.ipynb`

**NOTE:** Be aware that `extract_recipes.py` and `Babish Recipe Extract.ipynb` will make **LOTS** of network calls to the official bingingwithbabish.com website. Calls are cached and rate limited but please be very considerate and only run them if absolutely necessary.

### Tests
Tests covering [extract_recipes.py](./extract_recipes.py) are located in the [tests/](tests/) directory and can be run using [pytest](https://docs.pytest.org/en/latest/).

```bash
pytest tests/ # directory is optional
```

### Docs
* [Code of Conduct](./CODE_OF_CONDUCT.md), [GNU General Public License v3.0](./LICENSE)
