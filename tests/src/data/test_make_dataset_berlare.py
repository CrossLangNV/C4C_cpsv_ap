import os
import unittest

from data.make_dataset_berlare import download_sitemap, pipeline_all
from data.utils.sitemap import DIR_EXT, FILENAME_SITEMAP_OVERVIEW_TMP, get_sitemap_csv, process_sitemap
from relation_extraction.html_parsing.utils import _tmp_filename


class TestProcessSitemap(unittest.TestCase):
    def setUp(self) -> None:
        self.url_sitemap = "https://www.berlare.be/sitemap.aspx"

    def test_call(self):
        filename = FILENAME_SITEMAP_OVERVIEW_TMP

        process_sitemap(self.url_sitemap, filename)

        # Open and check content
        with self.subTest('Sanity check - read output'):
            df_all = get_sitemap_csv(filename)

        with self.subTest('name'):
            l_name = df_all.name
            self.assertGreater(len(l_name), 0, 'Expected non-empty')

            for name_i in l_name:
                self.assertIsInstance(name_i, str)

        with self.subTest('url'):
            l_url = df_all.url

            self.assertGreater(len(l_url), 0, 'Expected non-empty')

            for url_i in l_url:

                if url_i is None:
                    continue  # Some Nones are expected

                self.assertIsInstance(url_i, str)

        with self.subTest('event'):
            l_event = df_all.event

            self.assertGreater(len(l_event), 0, 'Expected non-empty')

            for event_i in l_event:
                self.assertIsInstance(event_i, str)


class Test_Download(unittest.TestCase):
    def test_call(self, download=False):
        if download:
            download_sitemap(FILENAME_SITEMAP_OVERVIEW_TMP)

        # Actual test, above should only run once!

        df_all = get_sitemap_csv(FILENAME_SITEMAP_OVERVIEW_TMP)

        for i, row in df_all.iterrows():
            url = row.url

            filename_html = _tmp_filename(url, ext='.html',
                                          dir=DIR_EXT)

            self.assertTrue(os.path.exists(filename_html))


class TestPipelineAll(unittest.TestCase):
    def test_call(self):
        pipeline_all(FILENAME_SITEMAP_OVERVIEW_TMP)


if __name__ == '__main__':
    unittest.main()
