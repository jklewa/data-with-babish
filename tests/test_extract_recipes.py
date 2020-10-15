from ibdb.extract_recipes import Recipe


class TestRecipe(object):
    # TODO: Separate tests from the file, probably use pytest to test functions in this module

    def test_parse_ingredient(self):
        # Tests to validate parse_ingredient()
        tests = [
            'Bread', (None, None, 'Bread'),
            '6 stalks celery', (6.0, None, 'Stalks Celery'),
            '4 eggs', (4.0, None, 'Eggs'),
            '2 ½ pounds of full fat cream cheese, cut', (2.5, 'pound', 'Full Fat Cream Cheese'),
            '25 oreos, finely processed', (25.0, None, 'Oreos'),
            '1-2 variable ingredients', ('1-2', None, 'Variable Ingredients'),
            '2 1/2 things', (2.5, None, 'Things'),
            '1/2 things', (0.5, None, 'Things'),
            '1 large, long sourdough loaf', (1.0, 'large', 'Long Sourdough Loaf'),
            '100ml Water', (100.0, 'ml', 'Water'),
            '1L Water', (1.0, 'L', 'Water')
        ]

        assert len(tests) % 2 == 0, 'A test is missing its expected output'

        for (i, v) in zip(tests[::2], tests[1::2]):
            actual = Recipe.parse_ingredient(i)
            expected = Recipe.Ingredient(*v, i)
            assert actual == expected, "parse_ingredient() incorrectly parsed '{}'\nExpected:\n{}\nActual:\n{}".format(i, expected, actual)

    def test_normalize_qty(self):
        # Tests to validate normalize_qty()

        # Test the special case for None
        assert Recipe.normalize_qty(None) is None
        assert Recipe.normalize_qty('') is None

        # Numeric conversions
        tests = [
            '1', 1.0,
            '1/2', 0.5,
            '1 2/3', (1 + 2 / 3),
            '1 ⅔', (1 + 2 / 3)
        ]

        assert len(tests) % 2 == 0, 'A test is missing its expected output'

        for (i, v) in zip(tests[::2], tests[1::2]):
            actual = Recipe.normalize_qty(i)
            expected = v
            assert abs(actual - expected) < 0.00001, "normalize_qty() incorrectly parsed '{}'\nExpected:\n{}\nActual:\n{}".format(i, expected, actual)

    def test_normalize_unit(self):
        # Tests to validate normalize_unit()
        tests = [
            None, None,

            # Abreviations
            't', 'teaspoon',
            'tsp', 'teaspoon',
            'T', 'tablespoon',
            'Tbsp', 'tablespoon',
            'unknown', 'unknown',

            # Normalize to lowercase
            'CUP', 'cup',
            'Pound', 'pound',
        ]

        assert len(tests) % 2 == 0, 'A test is missing its expected output'

        for (i, v) in zip(tests[::2], tests[1::2]):
            actual = Recipe.normalize_unit(i)
            expected = v
            assert actual == expected, "normalize_unit() incorrectly parsed '{}'\nExpected:\n{}\nActual:\n{}".format(i, expected, actual)

    def test_normalize_name(self):
        # Tests to validate normalize_name()
        tests = [
            'cAnDy CaNe', 'Candy Cane',  # Capitalized words
            'a\t\nb', 'A B',  # Tabs and newlines
            'Whole Milk ', 'Milk',  # Remove qualifiers
            'Hot Water', 'Water',  # Remove temps
            'Cold Milk', 'Milk',
        ]

        assert len(tests) % 2 == 0, 'A test is missing its expected output'

        for (i, v) in zip(tests[::2], tests[1::2]):
            actual = Recipe.normalize_name(i)
            expected = v
            assert actual == expected, "normalize_name() incorrectly parsed '{}'\nExpected:\n{}\nActual:\n{}".format(i, expected, actual)
