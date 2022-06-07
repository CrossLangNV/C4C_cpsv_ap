"""
docker compose run cpsv_ap python scripts/extract_cpsv_ap.py -g -o scripts/V_ICT_OR/example1.rdf --html_parsing scripts/V_ICT_OR/example1.html -l NL -c BE -m https://www.berlare.be/adreswijziging-binnen-berlare_2.html
"""
import os.path
import warnings
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic import BaseModel

from data.html import get_html, url2html
from scripts.extract_cpsv_ap import extract_cpsv_ap_from_html

DIR_VICTOR = os.path.dirname(__file__)


class SitemapUrl(BaseModel):
    name: str
    url: Optional[str]

    event: Optional[str]  # Name of the event (without the name of the link)

    children: List[BaseModel] = []  # SitemapUrl children

    def __repr__(self):
        return self.name


def scrape_sitemap(url) -> List[SitemapUrl]:
    """

    Args:
        url: to the sitemap

    Returns:
        List with objects containing the urls
    """

    filename_html_sitemap = os.path.join(DIR_VICTOR, "sitemap.html")

    if not os.path.exists(filename_html_sitemap):
        url2html(url,
                 filename_html_sitemap
                 )
    html_sitemap = get_html(filename_html_sitemap)

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


def process_links(l_links: List[SitemapUrl]):
    for link in l_links:
        if len(link.children) > 0:
            continue

        link.url
        link.name
        link.event

        # TODO call pipeline

    return


def main_single_example(url,
                        in_html=os.path.join(DIR_VICTOR, "example1.html"),
                        html_parsed=os.path.join(DIR_VICTOR, "example1_parse.html"),
                        out_rdf=os.path.join(DIR_VICTOR, "example1.rdf")):
    url2html(url, in_html)

    extract_cpsv_ap_from_html(in_html,
                              out_rdf,
                              context="https://www.berlare.be",
                              country_code="BE",
                              lang="NL",
                              url=url,
                              general=True,
                              filename_html_parsing=html_parsed,
                              translation=[])

    return


if __name__ == '__main__':

    l_links = scrape_sitemap("https://www.berlare.be/sitemap.aspx")

    process_links(l_links)

    b = 0
    if b:
        url = "https://www.berlare.be/adreswijziging-binnen-berlare_2.html"
        main_single_example(url)
