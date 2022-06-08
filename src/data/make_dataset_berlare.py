import os

from data.html import get_html, url2html
from data.utils.sitemap import DIR_EXT, FILENAME_SITEMAP_OVERVIEW_TMP, get_sitemap_csv, process_sitemap
from relation_extraction.html_parsing.utils import _tmp_filename

DIR_PROCESSED = os.path.join(DIR_EXT, '../processed')


def download_sitemap(filename) -> None:
    """

    Args:
        filename: with csv containing sitemap info

    Returns:

    """
    df_all = get_sitemap_csv(filename)

    for i, row in df_all.iterrows():
        url = row.url

        filename_html = _tmp_filename(url, ext='.html',
                                      dir=DIR_EXT)

        url2html(url, filename=filename_html)


def pipeline_all(filename):
    df_all = get_sitemap_csv(filename)

    for i, row in df_all.iterrows():
        url = row.url

        filename_html = _tmp_filename(url, ext='.html',
                                      dir=DIR_EXT)

        s_html = get_html(filename_html)

        DIR_PROCESSED

    return


def main(url_sitemap,
         redo=True,
         predownload=False):
    """
    1. Go over sitemap and export name, url and event
    2. Download all HTML's
    3. Generate training data
    Returns:

    """

    # 1.

    if redo or (not os.path.exists(FILENAME_SITEMAP_OVERVIEW_TMP)):
        process_sitemap(url_sitemap, filename_export=FILENAME_SITEMAP_OVERVIEW_TMP)

    # 2.
    if predownload:
        download_sitemap(FILENAME_SITEMAP_OVERVIEW_TMP)

    pipeline_all(FILENAME_SITEMAP_OVERVIEW_TMP)

    return


if __name__ == '__main__':
    url_sitemap = "https://www.berlare.be/sitemap.aspx"
    main(url_sitemap)
