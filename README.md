# _Data with Babish_

This project aims to analyze the recipes of the popular YouTube channel [Binging with Babish](http://bingingwithbabish.com) and convert them into beautiful data.

## Datasets

 * [babish.json](#babishjson) - Parsed recipe ingredients, grouped by episode

### babish.json

  Contains ingredients from [BWB Recipes](http://bingingwithbabish.com/recipes) in the format:

  ```python
  [
    {
      "episode_name": "Episode Name",
      "episode_link": "https://www.bingingwithbabish.com/recipes/...",
      "youtube_link": "https://www.youtube.com/watch?v=...",
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
Required tools: **Python 3**, [Jupyter Notebook](http://ipython.org/notebook.html)

1. Install packages `pip install -r requirements.txt`
2. Start Jupyter on [http://localhost:8888](http://localhost:8888) `jupyter notebook`
3. Open `Babish Recipe Extract.ipynb` or `Babish Data Analysis.ipynb`

**NOTE:** Be aware that `Babish Recipe Extract.ipynb` will make **LOTS** of network calls to the official bingingwithbabish.com website. Calls are cached and rate limited but please be very considerate and only run those notebook sections if absolutely necessary.

### Docs
* [Code of Conduct](./CODE_OF_CONDUCT.md), [GNU General Public License v3.0](./LICENSE)