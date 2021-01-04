import unittest
import os
import tempfile

from ibdb.export import write_response


class TestExport(unittest.TestCase):
    def test_write_response(self):
        route = '/episodes'
        to = 'episodes.json'
        with tempfile.TemporaryDirectory() as tempdir:
            out_filepath = os.path.join(tempdir, to)
            write_response(route, out_filepath)
            self.assertTrue(os.path.exists(out_filepath))
