import os
import warnings
from typing import List, Optional
from urllib.parse import urljoin

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel

from data.html import get_html, url2html

DIR_ROOT = os.path.join(os.path.dirname(__file__), '../../..')
DIR_EXT = os.path.abspath(os.path.join(DIR_ROOT, 'data/external'))

FILENAME_SITEMAP_HTML_TMP = os.path.join(DIR_EXT, "tmp_sitemap.html")
FILENAME_SITEMAP_OVERVIEW_TMP = os.path.join(DIR_EXT, 'tmp.csv')


class SitemapUrl(BaseModel):
    name: str
    url: Optional[str]

    event: Optional[str]  # Name of the event (without the name of the link)

    children: List[BaseModel] = []  # SitemapUrl children

    def __repr__(self):
        return self.name


def process_sitemap(url_sitemap,
                    filename_export=FILENAME_SITEMAP_OVERVIEW_TMP,
                    csv_file_delimiter="@@@"):
    """

    Args:
        url_sitemap:
        filename_export:
        csv_file_delimiter:

    Returns:

    """
    l_links = scrape_sitemap(url_sitemap)

    # Iterate over all links and only keep end links

    l_d = []

    for link in l_links:
        if link.children:
            continue

        if not link.url:
            continue  # No url, no point of scraping

        d = {'url': link.url,
             'name': link.name,
             'event': link.event}

        l_d.append(d)

    df_all = pd.DataFrame(l_d)

    # to allow multi char delimiter
    np.savetxt(filename_export, df_all,
               delimiter=csv_file_delimiter, header=csv_file_delimiter.join(df_all.columns.values),
               fmt='%s', comments='', encoding=None)

    return df_all


def get_sitemap_csv(filename_export=FILENAME_SITEMAP_HTML_TMP,
                    csv_file_delimiter="@@@"):
    df_all = pd.read_csv(filename_export, sep=csv_file_delimiter).replace({'None': None})

    return df_all


def scrape_sitemap(url,
                   filename_html_sitemap_tmp=FILENAME_SITEMAP_HTML_TMP) -> List[SitemapUrl]:
    """

    Args:
        url: to the sitemap

    Returns:
        List with objects containing the urls
    """

    if not os.path.exists(filename_html_sitemap_tmp):
        url2html(url,
                 filename_html_sitemap_tmp
                 )
    html_sitemap = get_html(filename_html_sitemap_tmp)

    # Find h1, then all
    soup = BeautifulSoup(html_sitemap, 'html.parser')

    # Find all pages (at least for WONEN and WERKEN & ONDERNEMEN)

    l_a = soup.find_all("h1")

    if len(l_a) >= 2:
        warnings.warn("Only expected one <h1/>, we will be using the first one.", UserWarning)

    assert len(l_a) > 0, 'Could not find a title (h1 actually) field'
    h1 = l_a[0]

    sitemap_content_list = h1.find_next('ul')

    def find_urls(ul,
                  parents: List[str] = None,
                  l_urls: List[SitemapUrl] = None) -> List[SitemapUrl]:

        if parents is None:
            parents = []

        if l_urls is None:
            l_urls = []

        # Go
        for li_i in ul.findChildren('li', recursive=False):
            # Get the (only) href
            a = li_i.findChild('a', recursive=False)

            if a is None:
                # No hyperlink
                text = li_i.get_text('\n', True).splitlines()[0]
                url_href = None
            else:
                # Found hyperlink
                text = a.get_text(separator=' ', strip=True)
                _url_rel = a.attrs.get('href')
                url_href = urljoin(base=url, url=_url_rel)

            text_event = ' - '.join(parents)

            link = SitemapUrl(name=text,
                              url=url_href,
                              event=text_event if text_event else None,
                              )
            l_urls.append(link)

            # repeat for children

            ul_i = li_i.findChild('ul', recursive=False)
            if ul_i is not None:
                l_urls_children = find_urls(ul_i, parents=parents + [text])

                link.children.extend(l_urls_children)

                l_urls.extend(l_urls_children)

        return l_urls

    l_urls = find_urls(sitemap_content_list)

    return l_urls
