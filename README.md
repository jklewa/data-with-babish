# _Data with Babish_

This project publishes structured data derived from the recipes of the popular YouTube channel [Binging with Babish](https://www.babi.sh). The committed YAML and JSON datasets are the source of truth for downstream consumers.

## Visualizations

* [jklewa.github.io/data-with-babish-example](https://jklewa.github.io/data-with-babish-example/) ([repo](https://github.com/jklewa/data-with-babish-example)) An interactive episode data viewer

## Datasets

 * [ibdb.episodes.json](datasets/ibdb.episodes.json) ([docs](#ibdbepisodesjson)) Episodes and related guests, recipes and inspiration
 * [ibdb.guests.json](datasets/ibdb.guests.json) ([docs](#ibdbguestsjson)) Guests and their appearances
 * [ibdb.recipes.json](datasets/ibdb.recipes.json) ([docs](#ibdbrecipesjson)) Recipes and their origin episode
 * [ibdb.references.json](datasets/ibdb.references.json) ([docs](#ibdbreferencesjson)) TV Shows, Movies, etc. and when they were referenced
 * [ibdb.tags.json](datasets/ibdb.tags.json) ([docs](#ibdbtagsjson)) Tags applied to episodes (Source / Series / Category / Meal / Difficulty)

The same data is also available as a tree of YAML files under [`data/`](data/), one directory per entity. Each entity has a `data.yml` (the canonical fields) and a `meta.yml` sidecar with field-level provenance.

### [ibdb.episodes.json](datasets/ibdb.episodes.json)

  **Episodes** and related guests, recipes and inspiration in the format:

  ```python
  [
    {
      "episode_id": "epid",
      "name": "Episode Name",
      "published_date": "YYYY-MM-DD",
      "youtube_link": "https://www.youtube.com/watch?v=...",
      "official_link": "https://www.babi.sh/recipes/...",
      "image_link": "https://preview.image.host/image.png",
      "related": {
        "tags": [
          {
            "tag_id": 1,
            "axis": "Meal",
            "name": "Dinner"
          }
        ],
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

### [ibdb.guests.json](datasets/ibdb.guests.json)

  **Guests** and their appearances in the format:

  ```python
  [
    {
      "guest_id": 1,
      "name": "Guest Name",
      "appearances": [
        {
          "episode_id": "epid",
          "name": "Episode Name",
          "published_date": "YYYY-MM-DD",
          "youtube_link": "https://www.youtube.com/watch?v=...",
          "official_link": "https://www.babi.sh/recipes/...",
          "image_link": "https://preview.image.host/image.png"
        }
      ]
    },
    # ...
  ]
  ```

### [ibdb.recipes.json](datasets/ibdb.recipes.json)

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
        "name": "Episode Name",
        "published_date": "YYYY-MM-DD",
        "youtube_link": "https://www.youtube.com/watch?v=...",
        "official_link": "https://www.babi.sh/recipes/...",
        "image_link": "https://preview.image.host/image.png"
      }
    },
    # ...
  ]
  ```

### [ibdb.references.json](datasets/ibdb.references.json)

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
          "name": "Episode Name",
          "published_date": "YYYY-MM-DD",
          "youtube_link": "https://www.youtube.com/watch?v=...",
          "official_link": "https://www.babi.sh/recipes/...",
          "image_link": "https://preview.image.host/image.png"
        }
      ]
    },
    # ...
  ]
  ```

### [ibdb.tags.json](datasets/ibdb.tags.json)

  **Tags** applied to episodes. Each tag belongs to one of five `axis` values: `Source`, `Series`, `Category`, `Meal`, or `Difficulty`.

  ```python
  [
    {
      "tag_id": 1,
      "axis": "Meal",
      "name": "Dinner",
      "episodes": [
        {
          "episode_id": "epid",
          "name": "Episode Name",
          "published_date": "YYYY-MM-DD",
          "youtube_link": "https://www.youtube.com/watch?v=...",
          "official_link": "https://www.babi.sh/recipes/...",
          "image_link": "https://preview.image.host/image.png"
        }
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
Required tools: **Docker, Docker Compose**

1. Build `docker-compose build`
2. Run DB and API `docker-compose up -d`
3. Browse http://localhost:5000/
4. Re-export datasets from the DB `docker-compose exec ibdb sync export`
5. See other commands `docker-compose exec ibdb --help`

The Postgres container is initialized from [ibdb/db_dump.sql](ibdb/db_dump.sql), so the API is queryable as soon as the stack is up. [export.py](ibdb/export.py) regenerates [datasets/](datasets) from the DB's contents.

### Tests
Tests covering [recipe_parser.py](ibdb/recipe_parser.py) are located in the [tests/](tests/) directory and can be run using [pytest](https://docs.pytest.org/en/latest/).

Required tools: **Python 3.8**

1. Install packages `pip install -r requirements.txt`
2. Run tests `python -m pytest`

### Docs
* [Code of Conduct](CODE_OF_CONDUCT.md), [GNU General Public License v3.0](LICENSE)
