import os

from data.html import url2html
from data.utils.sitemap import DIR_EXT, FILENAME_SITEMAP_OVERVIEW_TMP, get_sitemap_csv, process_sitemap
from relation_extraction.html_parsing.utils import _tmp_filename
from scripts.extract_cpsv_ap import extract_cpsv_ap_from_html

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


def pipeline_all(filename,
                 from_scratch=False):
    df_all = get_sitemap_csv(filename)

    context = "https://berlare.be"
    country_code = "BE"
    language_code = "NL"
    translations = ["EN", "NL", "FR", "DE",
                    "EL", "UK"  # Optional ones
                    ]

    for i, row in df_all.iterrows():
        print(f'Webpage [{i + 1}/{len(df_all)}]')

        url = row.url

        filename_html = _tmp_filename(url, ext='.html',
                                      dir=DIR_EXT)

        filename_html_parsing = _tmp_filename(url, prefix='parsing_', ext='.html',
                                              dir=DIR_PROCESSED)

        filename_rdf = _tmp_filename(url, ext='.rdf',
                                     dir=DIR_PROCESSED)

        if from_scratch or os.path.exists(filename_rdf):
            continue

        # s_html = get_html(filename_html)

        extract_cpsv_ap_from_html(filename_html=filename_html,
                                  filename_rdf=filename_rdf,
                                  extract_concepts=False,
                                  context=context,
                                  country_code=country_code,
                                  url=url,
                                  general=True,
                                  lang=language_code,
                                  translation=translations,
                                  filename_html_parsing=filename_html_parsing
                                  )

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
