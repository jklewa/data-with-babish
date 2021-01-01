"""
Tests for existing utilities to solidify current state

Sync
    Youtube ID extract
    General HTML extract

"""

import unittest
import requests_mock
from callee import String
from ibdb.populate_db import (
    add_youtube_resources,
    extract_inspired_by,
    extract_youtube_id,
    extract_youtube_link,
    fetch_basics_episode_list,
    fetch_binging_episode_list,
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


class TestHtmlExtract(unittest.TestCase):
    mock_binging = {
        "items": [
            {
                "addedOn": 1602698027044,
                "updatedOn": 1602698027398,
                "publishOn": 1602698027044,
                "urlId": "restaurant-wars-steven-universe",
                "title": "Restaurant Wars inspired by Steven Universe",
                "body": "<div class=\"sqs-layout sqs-grid-12 columns-12\" data-layout-label=\"Post Body\" data-type=\"item\" data-updated-on=\"1602620992870\" id=\"item-5f860c85f164a947c743dc6a\"><div class=\"row sqs-row\"><div class=\"col sqs-col-12 span-12\"><div class=\"sqs-block html-block sqs-block-html\" data-block-type=\"2\" id=\"block-0deeafc005102c891099\"><div class=\"sqs-block-content\"><h2 style=\"white-space:pre-wrap;\">This week, by virtue of some long fermentation times and triple-cooking methods, we're taking a look at the cheffy versions of frozen snacks served up at Steven Universe's haute Beach City eatery. Can we make ketchup-stuffed french fries and cream cheese-stuffed pizza bagels worthy of a Michelin Star?</h2></div></div><div class=\"sqs-block image-block sqs-block-image\" data-block-type=\"5\" id=\"block-44136a064bcbc4c01d4b\"><div class=\"sqs-block-content\">\n\n\n\n\n\n\n\n\n  \n\n    \n  \n    <div\n        class=\"\n          image-block-outer-wrapper\n          layout-caption-hidden\n          design-layout-inline\n          combination-animation-none\n          individual-animation-none\n          individual-text-animation-none\n        \"\n        data-test=\"image-block-inline-outer-wrapper\"\n    >\n\n      \n\n      \n        <figure\n            class=\"\n              sqs-block-image-figure\n              intrinsic\n            \"\n            style=\"max-width:2500.0px;\"\n        >\n          \n        \n        \n\n        \n          <a\n              class=\"\n                sqs-block-image-link\n                \n          \n        \n              \"\n              href=\"https://www.youtube.com/watch?feature=youtu.be&v=J2eU4Ol3IDU\"\n              \n          >\n            \n          <div\n              \n                style=\"padding-bottom:56.160003662109375%;\"\n              \n              class=\"\n                image-block-wrapper\n                \n          \n        \n                has-aspect-ratio\n              \"\n              data-animation-role=\"image\"\n              \n  \n\n          >\n            <noscript><img src=\"https://images.squarespace-cdn.com/content/v1/590be7fd15d5dbc6bf3e22d0/1602620905156-OHYAGQMBM2HRTF187PUZ/ke17ZwdGBToddI8pDm48kAegX-1irUL6qWVp5YHdPlZ7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0mjKWc80r5PD-660Rc3KKl-EIGwdh7NUl8wqqSWoiGqWWkt1uV2bgdYZttL59vHUoQ/Screen+Shot+2020-10-13+at+3.27.55+PM.png\" alt=\"Screen Shot 2020-10-13 at 3.27.55 PM.png\" /></noscript><img class=\"thumb-image\" data-src=\"https://images.squarespace-cdn.com/content/v1/590be7fd15d5dbc6bf3e22d0/1602620905156-OHYAGQMBM2HRTF187PUZ/ke17ZwdGBToddI8pDm48kAegX-1irUL6qWVp5YHdPlZ7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0mjKWc80r5PD-660Rc3KKl-EIGwdh7NUl8wqqSWoiGqWWkt1uV2bgdYZttL59vHUoQ/Screen+Shot+2020-10-13+at+3.27.55+PM.png\" data-image=\"https://images.squarespace-cdn.com/content/v1/590be7fd15d5dbc6bf3e22d0/1602620905156-OHYAGQMBM2HRTF187PUZ/ke17ZwdGBToddI8pDm48kAegX-1irUL6qWVp5YHdPlZ7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0mjKWc80r5PD-660Rc3KKl-EIGwdh7NUl8wqqSWoiGqWWkt1uV2bgdYZttL59vHUoQ/Screen+Shot+2020-10-13+at+3.27.55+PM.png\" data-image-dimensions=\"2500x1404\" data-image-focal-point=\"0.5,0.5\" alt=\"Screen Shot 2020-10-13 at 3.27.55 PM.png\" data-load=\"false\" data-image-id=\"5f860dd75cc2eb720d7cf11b\" data-type=\"image\" />\n          </div>\n        \n          </a>\n        \n\n        \n      \n        </figure>\n      \n\n    </div>\n  \n\n\n  \n\n\n</div></div><div class=\"sqs-block spacer-block sqs-block-spacer sized vsize-1\" data-aspect-ratio=\"2.8125\" data-block-type=\"21\" id=\"block-85c430a17fe5b446bf13\"><div class=\"sqs-block-content\">&nbsp;</div></div><div class=\"row sqs-row\"><div class=\"col sqs-col-5 span-5\"><div class=\"sqs-block html-block sqs-block-html\" data-block-type=\"2\" id=\"block-971e80c405e57ac1344d\"><div class=\"sqs-block-content\"><h3 style=\"margin-left:40px;white-space:pre-wrap;\">Ingredients</h3><p class=\"\" style=\"white-space:pre-wrap;\"><strong>Bagels Ingredients:</strong></p><ul data-rte-list=\"default\"><li><p class=\"\" style=\"white-space:pre-wrap;\">250 g bread flour</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">1 tsp active dry yeast</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">350 g room temperature water</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">25 g barley malt syrup</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">450 g bread flour (separate)</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">10 g kosher salt</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">San Marzano tomato sauce</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Mozzarella cheese</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Cream cheese</p></li></ul><p class=\"\" data-rte-preserve-empty=\"true\" style=\"white-space:pre-wrap;\"></p><p class=\"\" style=\"white-space:pre-wrap;\"><strong>French Fries &amp; Brine Ingredients:</strong></p><ul data-rte-list=\"default\"><li><p class=\"\" style=\"white-space:pre-wrap;\">1 kg russet potatoes, peeled and cut</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">1 L water</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">15 g kosher salt</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">10 g glucose syrup (or granulated sugar)</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">2 ½ g baking soda</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Peanut oil</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">2 qt duck fat</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Ketchup</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Parsley</p></li></ul></div></div></div><div class=\"col sqs-col-7 span-7\"><div class=\"sqs-block html-block sqs-block-html\" data-block-type=\"2\" id=\"block-7c15e6420b4f6938fe4e\"><div class=\"sqs-block-content\"><h1 style=\"margin-left:40px;white-space:pre-wrap;\">Method</h1><p class=\"\" style=\"white-space:pre-wrap;\"><strong>Bagels Method:</strong></p><ol data-rte-list=\"default\"><li><p class=\"\" style=\"white-space:pre-wrap;\">Start by combining 250 grams of bread flour, 1 teaspoon of active dry yeast, and 350 grams of room temperature water.&nbsp; Mix into a paste, cover, and let sit at room temperature for at least 4 hours or up to overnight.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Add in 25 grams of barley malt syrup, 450 grams of bread flour, and 10 grams of kosher salt. Using a dough hook, knead for 10 full minutes.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Form into a taut ball and place back into the bowl. Cover and let proof at room temperature for 1 hour.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Portion out the pieces of dough into balls weighing 130 grams each. Place on a lined rimmed baking sheet, covered with a moistened towel, and let sit at room temperature for another 30 minutes.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Gently punch a hole through the middle using a thumb and widened into a bagel using two spinning fingers. Rinse and repeat with the remaining pieces of dough.</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Generously oil some plastic wrap and cover the bagels before placing it into the fridge for at least 24 hours, ideally up to 72 hours.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Add 1 gallon of water with 1 tablespoon of barley malt syrup, and 1 teaspoon of baking soda. Mix together and bring to a boil.</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Once boiling, add the bagels straight from the freezer for 20 seconds on each side.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Place on a lightly greased wire rack on a rimmed baking sheet and bake in a 425°F oven for 20-25 minutes. After 15 minutes flip once seeing spotty browning and place back into the oven for the remainder of the 20-25 minutes. Set aside to cool.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Once cooled, slice a bagel in half and scoop out the bagels interiors. Pipe in cream cheese and spread smoothly then top with a cooked San Marzano tomato sauce and bits of fresh mozzarella cheese.</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Bake at 425°F for 5-10 minutes. Top with fresh chopped basil.</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Plate and enjoy.&nbsp;</p></li></ol><p class=\"\" style=\"white-space:pre-wrap;\"><br></p><p class=\"\" style=\"white-space:pre-wrap;\"><strong>French Fries Method:</strong></p><ol data-rte-list=\"default\"><li><p class=\"\" style=\"white-space:pre-wrap;\">Start by peeling and cutting 1 kilogram of russet potatoes into giant-sized french fries. Place into cool water after peeling and cutting.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">For the brine, in 1 liter of water add 15 grams of kosher salt, 10 grams of glucose syrup (granulated sugar), and 2 ½ grams of baking soda. Mix together.&nbsp;&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Carefully add half the fries and half the brine into a vacuumed sealed bag and seal shut.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Add into a 195°F sous vide bath, cover tightly with plastic wrap, and cook for 20 minutes.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Using gloves, carefully remove and drain before carefully placing onto a wire rack set in a rimmed baking sheet. Make sure no fries are touching. Place into the freezer for 30 minutes.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Straight out of the freezer place the fries carefully into 260°F peanut oil for 5-8 minutes until just starting to turn blonde around the edges. Rinse and repeat with the rest in small batches.</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Place the fries back onto the wire rack and into the freezer for at least 2 hours, ideally overnight.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">In a saucepot, add 2 quarts of duck fat and heat to 350°F. Carefully add in the fries and let fry between 2-5 minutes until golden brown and crisp.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Using a giant barbecue needle filled with warm ketchup, slowly insert the needle into the fry lengthwise then slowly remove while filling the fry with ketchup. Rinse and repeat.</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Arrange the fries on a plate with a sprig of parsley and enjoy. </p></li></ol></div></div></div></div></div></div></div>",
                "fullUrl": "/recipes/restaurant-wars-steven-universe",
                "assetUrl": "https://images.squarespace-cdn.com/content/v1/590be7fd15d5dbc6bf3e22d0/1602620962351-XUFO2G1Q1Y83UQS7V9V4/ke17ZwdGBToddI8pDm48kAegX-1irUL6qWVp5YHdPlZ7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0mjKWc80r5PD-660Rc3KKl-EIGwdh7NUl8wqqSWoiGqWWkt1uV2bgdYZttL59vHUoQ/Screen+Shot+2020-10-13+at+3.27.55+PM.png",
            },
        ],
    }

    @requests_mock.Mocker()
    def test_binging_episode_list(self, m):
        m.register_uri(requests_mock.ANY, requests_mock.ANY, json=self.mock_binging)

        expected = [
            dict(
                id="restaurant-wars-steven-universe",
                name="Restaurant Wars inspired by Steven Universe",
                official_link="https://www.bingingwithbabish.com/recipes/restaurant-wars-steven-universe",
                youtube_link="https://www.youtube.com/watch?v=J2eU4Ol3IDU",
                image_link="https://img.youtube.com/vi/J2eU4Ol3IDU/mqdefault.jpg",
                published_date="2020-10-14",
                body=String(),
            ),
        ]
        self.assertEqual(expected, list(fetch_binging_episode_list()))

    mock_basics = {
        "items": [
            {
                "addedOn": 1600379063885,
                "updatedOn": 1602010863561,
                "publishOn": 1600379063885,
                "urlId": "short-ribs",
                "title": "BRAISED SHORT RIBS",
                "sourceUrl": "",
                "body": "<div class=\"sqs-layout sqs-grid-12 columns-12\" data-layout-label=\"Post Body\" data-type=\"item\" data-updated-on=\"1600376234450\" id=\"item-5f63cd87cefb254659365fc6\"><div class=\"row sqs-row\"><div class=\"col sqs-col-12 span-12\"><div class=\"sqs-block html-block sqs-block-html\" data-block-type=\"2\" id=\"block-a14a3992f8bdfe2cb7f2\"><div class=\"sqs-block-content\"><h2 style=\"white-space:pre-wrap;\">This week on Basics, we take a look at cooking up the braised short ribs.</h2></div></div><div class=\"sqs-block image-block sqs-block-image\" data-block-type=\"5\" id=\"block-425bc525c748a5b7a8c8\"><div class=\"sqs-block-content\">\n\n\n\n\n\n\n\n\n  \n\n    \n  \n    <div\n        class=\"\n          image-block-outer-wrapper\n          layout-caption-hidden\n          design-layout-inline\n          combination-animation-none\n          individual-animation-none\n          individual-text-animation-none\n        \"\n        data-test=\"image-block-inline-outer-wrapper\"\n    >\n\n      \n\n      \n        <figure\n            class=\"\n              sqs-block-image-figure\n              intrinsic\n            \"\n            style=\"max-width:2500.0px;\"\n        >\n          \n        \n        \n\n        \n          <a\n              class=\"\n                sqs-block-image-link\n                \n          \n        \n              \"\n              href=\"https://www.youtube.com/watch?feature=youtu.be&v=DUTyGfwdBaY\"\n              \n          >\n            \n          <div\n              \n                style=\"padding-bottom:56.599998474121094%;\"\n              \n              class=\"\n                image-block-wrapper\n                \n          \n        \n                has-aspect-ratio\n              \"\n              data-animation-role=\"image\"\n              \n  \n\n          >\n            <noscript><img src=\"https://images.squarespace-cdn.com/content/v1/59d40133017db2fd8a60b3fe/1600376349732-0HPQG7IV0QZXRL66IJD2/ke17ZwdGBToddI8pDm48kNmCHhiNRUqL9XGAHAdeyfh7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0pwo7TkYf7-UW-UiblSyrjPBHiRGKSPYtZ_jRLT7z5OWlfFuuqdIUt8rR7SijLgh8A/Screen+Shot+2020-09-17+at+3.49.34+PM.png\" alt=\"Screen Shot 2020-09-17 at 3.49.34 PM.png\" /></noscript><img class=\"thumb-image\" data-src=\"https://images.squarespace-cdn.com/content/v1/59d40133017db2fd8a60b3fe/1600376349732-0HPQG7IV0QZXRL66IJD2/ke17ZwdGBToddI8pDm48kNmCHhiNRUqL9XGAHAdeyfh7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0pwo7TkYf7-UW-UiblSyrjPBHiRGKSPYtZ_jRLT7z5OWlfFuuqdIUt8rR7SijLgh8A/Screen+Shot+2020-09-17+at+3.49.34+PM.png\" data-image=\"https://images.squarespace-cdn.com/content/v1/59d40133017db2fd8a60b3fe/1600376349732-0HPQG7IV0QZXRL66IJD2/ke17ZwdGBToddI8pDm48kNmCHhiNRUqL9XGAHAdeyfh7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0pwo7TkYf7-UW-UiblSyrjPBHiRGKSPYtZ_jRLT7z5OWlfFuuqdIUt8rR7SijLgh8A/Screen+Shot+2020-09-17+at+3.49.34+PM.png\" data-image-dimensions=\"2500x1415\" data-image-focal-point=\"0.5,0.5\" alt=\"Screen Shot 2020-09-17 at 3.49.34 PM.png\" data-load=\"false\" data-image-id=\"5f63ce097fcaed18cb8a393e\" data-type=\"image\" />\n          </div>\n        \n          </a>\n        \n\n        \n      \n        </figure>\n      \n\n    </div>\n  \n\n\n  \n\n\n</div></div><div class=\"sqs-block horizontalrule-block sqs-block-horizontalrule\" data-block-type=\"47\" id=\"block-af50501268fee29ab371\"><div class=\"sqs-block-content\"><hr /></div></div><div class=\"row sqs-row\"><div class=\"col sqs-col-5 span-5\"><div class=\"sqs-block html-block sqs-block-html\" data-block-type=\"2\" id=\"block-857848ff7f6fc42f1f4c\"><div class=\"sqs-block-content\"><p class=\"\" style=\"white-space:pre-wrap;\">Ingredients</p><p class=\"\" style=\"white-space:pre-wrap;\"><strong>Braised Short Rib Ingredients:</strong></p><ul data-rte-list=\"default\"><li><p class=\"\" style=\"white-space:pre-wrap;\">1 whole rack short ribs</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">½ lb carrots, peeled and chopped</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">5 stalks celery, chopped</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">2 large onions, peeled and sliced</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">1 Tbsp vegetable oil</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">3 Tbsp tomato paste&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">5 cloves garlic</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Soy sauce</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">2 cups chicken stock</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">2 cups amber ale (or red wine)</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">½ cup prune juice</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Sprig thyme</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Sprig parsley</p></li></ul></div></div></div><div class=\"col sqs-col-7 span-7\"><div class=\"sqs-block html-block sqs-block-html\" data-block-type=\"2\" id=\"block-e0580c632981ceb93b18\"><div class=\"sqs-block-content\"><h2 style=\"white-space:pre-wrap;\"><strong>Method</strong> </h2><p class=\"\" style=\"white-space:pre-wrap;\"><strong>Braised Short Rib Method:</strong></p><ol data-rte-list=\"default\"><li><p class=\"\" style=\"white-space:pre-wrap;\">Start by removing the excess layer of skin and fat from the ribs. Season generously with kosher salt and freshly ground pepper on all sides.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Peel ½ pound of carrots and chop into manageable pieces. Cut the heads off a few stalks of celery and cut into manageable pieces. Peel and slice 2 large onions.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">On the stovetop, heat a tablespoon of vegetable oil over medium-high heat until whisps of smoke emerge.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">At which point, in batches, place the pieces of short rib into the pot and brown them on all sides. To prevent the fond from burning, place the ribs back down in the exact spot that they were before flipping. If exposed fond during the final batch, place a handful of onions to prevent the fond from burning.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Once every short rib is seared, add in the onions (or rest of the onions) and saute until soft and brown. Add in 3 tablespoons of tomato paste, sauteing and whisking together for an additional 2-3 minutes.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Add in the celery and carrots, sauteing to warm up, add in 5 cloves of garlic, 2 cups of an amber ale (or dry red wine), 2 cups of chicken stock, a splash of soy sauce, and ½ cup of prune juice. Stir to combine.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Add a few sprigs of fresh thyme and parsley.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Nestle in the pieces of short rib making sure each piece peaks just above the liquid. Least browned side up.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Cover and place into a 275°F oven for 4-5 hours. Check after 3.5 hours to check doneness. If there is no resistance after poking with a paring knife then the short ribs are done.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Once done, remove the short ribs from the pot and into the fridge (if made ahead of time) and strain the remaining solids out of the braising liquid.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">If made for immediate use, let the liquid settle and skim the fat off the top of the liquid.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">If made ahead of time, for a rapid cooling place a few big pieces of ice into the liquid and let sit for 15 minutes. Wrap with plastic wrap and place into the refrigerator for at least 4 hours and up to overnight. Once chilled, remove the solid layer of fat floating on top.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Once the fat is removed, boil the liquid in a high walled skillet until reduced by 80%. This can take 1-2 hours.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">Once the sauce coats the back of a spoon, place the short ribs into the skillet and base with the sauce before covering and letting it sit for 20 minutes.&nbsp;</p></li><li><p class=\"\" style=\"white-space:pre-wrap;\">When ready to serve, place onto a pomme puree and top with sauce and garnished with fresh parsley. Enjoy!</p></li></ol><p class=\"\" style=\"white-space:pre-wrap;\"> </p></div></div></div></div><div class=\"sqs-block spacer-block sqs-block-spacer sized vsize-1\" data-block-type=\"21\" id=\"block-36235e74aabc211c00c9\"><div class=\"sqs-block-content\">&nbsp;</div></div></div></div></div>",
                "author": {
                    "displayName": "Emilija Saxe",
                    "firstName": "Emilija",
                    "lastName": "Saxe"
                },
                "fullUrl": "/basicsepisodes/short-ribs",
                "assetUrl": "https://images.squarespace-cdn.com/content/v1/59d40133017db2fd8a60b3fe/1600376409547-5J7JE93J2QJQJMEA75JS/ke17ZwdGBToddI8pDm48kNmCHhiNRUqL9XGAHAdeyfh7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z4YTzHvnKhyp6Da-NYroOW3ZGjoBKy3azqku80C789l0pwo7TkYf7-UW-UiblSyrjPBHiRGKSPYtZ_jRLT7z5OWlfFuuqdIUt8rR7SijLgh8A/Screen+Shot+2020-09-17+at+3.49.34+PM.png",
            },
        ],
    }

    @requests_mock.Mocker()
    def test_basics_episode_list(self, m):
        m.register_uri(requests_mock.ANY, requests_mock.ANY, json=self.mock_basics)

        expected = [
            dict(
                id="short-ribs",
                name="BRAISED SHORT RIBS",
                official_link="https://basicswithbabish.co/basicsepisodes/short-ribs",
                youtube_link="https://www.youtube.com/watch?v=DUTyGfwdBaY",
                image_link="https://img.youtube.com/vi/DUTyGfwdBaY/mqdefault.jpg",
                published_date="2020-09-17",
                body=String(),
            ),
        ]

        self.assertEqual(expected, list(fetch_basics_episode_list()))


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
