import unittest

from ibdb.extract import (
    add_youtube_resources,
    extract_youtube_id,
    extract_youtube_link,
    extract_inspired_by,
)


class TestYouTube(unittest.TestCase):
    def test_youtube_link(self):
        test_cases = [
            dict(should="prefer json", expected="https://www.youtube.com/watch?v=URLFROMJSON", html="""
                <div class="video-block" data-block-json='{"url": "https://www.youtube.com/watch?v=URLFROMJSON"}'>
                <a href="https://www.youtube.com/watch?v=URLFROMLINK">
            """),
            dict(should="fall back to any youtube link", expected="https://www.youtube.com/watch?v=URLFROMLINK", html="""
                <a href="https://www.youtube.com/watch?v=URLFROMLINK">
            """),
            dict(should="handle multiple links found", expected="https://www.youtube.com/watch?v=FIRST", html="""
                <a href="https://www.youtube.com/watch?v=FIRST">
                <a href="https://www.youtube.com/watch?v=SECOND">
            """),
            dict(should="handle missing link", expected="", html="""
                <div>No link to be found</div>
            """),
        ]
        for t in test_cases:
            self.assertEqual(t['expected'], extract_youtube_link(post_body=t['html']), t['should'])

    def test_youtube_id(self):
        test_cases = [
            dict(expected="J2eU4Ol3IDU", link="https://www.youtube.com/watch?v=J2eU4Ol3IDU"),
        ]
        for t in test_cases:
            self.assertEqual(t['expected'], extract_youtube_id(youtube_link=t['link']))

    def test_youtube_resources(self):
        test_cases = [
            dict(expected=dict(youtube_id="URLFROMJSON", youtube_link="https://www.youtube.com/watch?v=URLFROMJSON", youtube_image_link="https://img.youtube.com/vi/URLFROMJSON/mqdefault.jpg"),
                 raw=dict(body="""<div class="video-block" data-block-json='{"url": "https://www.youtube.com/watch?v=URLFROMJSON"}'>""")),
            dict(expected=dict(youtube_id=None, youtube_link="https://corrupted.url/", youtube_image_link=None),
                 raw=dict(body="""<div class="video-block" data-block-json='{"url": "https://corrupted.url/"}'>""")),
        ]
        for t in test_cases:
            self.assertEqual({**t['raw'], **t['expected']}, add_youtube_resources(raw=t['raw']))


class TestInspiredBy(unittest.TestCase):
    def test_extract_inspired_by(self):
        tests = [
            ('', []),
            ("Brock's Onigiri inspired by Pokémon", ['Pokémon']),
            ("Homer Simpson's Patented Space Age Out-Of-This-World Moon Waffles", []),
            ('Bad Breath Sundae inspired by SpongeBob Squarepants', ['SpongeBob Squarepants']),
            ('Banoffee Pie inspired by Love, Actually', ['Love, Actually']),
            ('Bear Stew inspired by Red Dead Redemption 2', ['Red Dead Redemption 2']),
            ('Binging with Babish 4 Million Subscriber Special: Death Sandwich from Regular Show', ['Regular Show']),
            ('Crème de la Crème à la Edgar inspired by The Aristocats', ['The Aristocats']),
            ('Egg Sandwich (with Homemade Ciabatta) inspired by Birds of Prey', ['Birds of Prey']),
            ('Eggs Woodhouse For Good from Archer', ['Archer']),
            ('Meat Tornado inspired by Parks & Rec ', ['Parks & Rec']),
            ('Pineapple-Curry Fried Rice inspired by Food Wars!: Shokugeki no Soma', ['Food Wars!: Shokugeki no Soma']),
        ]

        for episode_name, expected in tests:
            self.assertEqual(expected, extract_inspired_by(episode_name))

    @unittest.skip("Advanced cases aren't supported yet")
    def test_extract_inspired_by_advanced(self):
        tests = [
            # character cleanup
            ('Chocolate Pudding (4 Ways) inspired by Rugrats"', ['Rugrats']),
            ('Fried Green Tomatoes inspired by...Fried Green Tomatoes', ['Fried Green Tomatoes']),

            # parts
            ("It's Always Sunny in Philadelphia Special (Part II)", ["It's Always Sunny in Philadelphia"]),
            ('Shrimp inspired by Forrest Gump Part II', ["Forrest Gump"]),
            ('Shrimp inspired by Forrest Gump | Part 1', ['Forrest Gump']),

            # multi
            ('Nachos inspired by The Good Place (plus Naco Redemption)', ['The Good Place', 'Naco Redemption']),
            ('Beignets inspired by Chef (and Princess and the Frog)', ['Chef', 'Princess and the Frog']),

            # specials
            ('The Good Place Special', ["The Good Place"]),
            ('King of the Hill Special', ['King of the Hill']),
            ('Seinfeld Volume II', ['Seinfeld']),
            ('Charlie Brown Thanksgiving', ['Charlie Brown']),
            ('Parks & Rec Burger Cookoff', ['Parks & Rec']),

            # comments
            ("Cinnamon Rolls inspired by Jim Gaffigan's Stand Up (sort of)", ["Jim Gaffigan's Stand Up"]),
            ('The Garbage Plate inspired by The Place Beyond The Pines (sort of)', ['The Place Beyond The Pines']),
            ('Direwolf Bread inspired by Game of Thrones (feat. Maisie Williams)', ['Game of Thrones']),
            ('Arrested Development Special (feat. Sean Evans)', ['Arrested Development']),
            ('Chocolate Lava Cakes inspired by Chef with Jon Favreau and Roy Choi', ['Chef']),
            ('The Every-Meat Burrito inspired by Regular Show: 2 Million Subscriber Special', ['Regular Show']),
            ('Szechuan Sauce Revisited (From Real Sample!)', []),  # excluded "Real Sample!"

            # exclusions
            ('Eggs in a Nest inspired by Lots of Stuff', []),  # excluded "Lots of Stuff"
        ]
        for episode_name, expected in tests:
            self.assertEqual(expected, extract_inspired_by(episode_name))
