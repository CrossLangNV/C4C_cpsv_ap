import urllib
from typing import Dict, List

import bs4
from bs4 import BeautifulSoup

from relation_extraction.cities import CityParser, Relations


class AffligemParser(CityParser):
    """
    Parser for Affligem.be
    """

    criterionRequirement = "Voorwaarden"
    rule = "Procedure"
    evidence = "Wat meebrengen"
    cost = "Bedrag"

    # e = "Uitzonderingen"

    def parse_page(self, s_html) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

        def clean_text(text):
            return text.strip(" \n\r\xa0\t").replace("\xa0", " ")

        h1 = soup.find('h1')
        page_procedure = h1.parent

        l = [[]]

        for tag in page_procedure.find_all():

            text = clean_text(tag.text)
            if not text:
                continue

            if tag.name in ['h1', 'h2', "h3"]:  # title
                l.append([text])

            elif tag.name in ["div"]:
                l[-1].append(text)

        # Filter empty subs:
        l = list(filter(lambda l_sub: len(l_sub), l))

        return l

    def extract_relations(self, s_html) -> Relations:

        l = self.parse_page(s_html)

        d = Relations()

        for l_sub in l:
            title = l_sub[0]
            paragraphs = l_sub[1:]
            paragraphs_clean = "\n".join(filter(lambda s: s, paragraphs))

            if title == self.criterionRequirement:
                d.criterionRequirement = paragraphs_clean

            elif title == self.rule:
                d.rule = paragraphs_clean

            elif title == self.evidence:
                d.evidence = paragraphs_clean

            elif title == self.cost:
                d.cost = paragraphs_clean

        return d

    def extract_event(self, s_html, url: None):

        if url:
            url_parsed = urllib.parse.urlparse(url)
            url_parsed.path
            return url_parsed.path

        soup = BeautifulSoup(s_html, 'html.parser')

        unordered_lists = soup.find_all('ul')

        ul_leven = [ul for ul in unordered_lists if ul]

        hierarchy = {}

        a = soup.find('title')

        def f(tag: bs4.element.Tag) -> bool:

            key_href = "href"
            if not tag.has_attr(key_href):
                return False

            href = tag.get(key_href)

            return True

        for _ in soup.find_all("a"):
            href = _.get("href")

        for _ in soup.find("a").find_all(f):
            _

        return

    def extract_hierarchy(self, html_sitemap):
        """
        Extract the hierarchy from the sitemap page.

        * Leven
        *** bouwen en wonen
        ***** advies en informatie
        ***** adresverandering
        ***** duurzaam bouwen
        ******* energieprestatieregelgeving
        ******* gratis energiescan voor bepaalde doelgroepen
          .
          .
          .

        Args:
            html_sitemap:

        Returns:

        """

        soup = BeautifulSoup(html_sitemap, 'html.parser')

        # Get sitemap
        main_content = soup.find(lambda tag: tag.get("id") == "main_content")

        class Sitemap:
            name: str
            url: str
            level: int
            children: List

            def __init__(self, name,
                         url,
                         level):
                self.name = name
                self.url = url
                self.level = level
                self.children = []

            def __repr__(self):
                return f'Sitemap(name={self.name}, url={self.url}, level={self.level})'

        sitemap = Sitemap("Sitemap",
                          None,
                          level=0)

        d_latest_lvl: Dict[int, Sitemap] = {}
        d_latest_lvl[sitemap.level] = sitemap

        for li in main_content.find('ul').find_all('li'):
            class_ = li.get("class")[0]
            level = int(class_.rsplit('_', 1)[-1])
            name = li.text
            url = li.find('a').get("href")

            new_sitemap = Sitemap(name=name,
                                  url=url,
                                  level=level)

            # Update parents children
            d_latest_lvl[new_sitemap.level - 1].children.append(new_sitemap)

            # Update latest
            d_latest_lvl[new_sitemap.level] = new_sitemap

        # soup.find_all('ul')

        return sitemap
