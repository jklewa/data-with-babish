from context import Recipe, BabishSync


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
        pass

    def test_normalize_unit(self):
        pass

    def test_normalize_name(self):
        pass
