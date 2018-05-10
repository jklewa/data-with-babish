# _Data is Babish (and Beautiful)_

This project aims to analyze the recipes of the popular YouTube channel [Binging With Babish](http://bingingwithbabish.com) and convert them into beautiful data.

## The Babish

 * [babish.json](#babishjson)

### babish.json

  Contains ingredients from [BWB Recipes](http://bingingwithbabish.com/recipes) in the format:

  ```python
  [
    {
      "episode_name": "Episode Name",
      "episode_link": "https://www.bingingwithbabish.com/recipes/...",
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
