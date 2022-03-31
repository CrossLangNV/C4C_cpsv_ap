import warnings
from typing import Dict, Generator, List

from bs4 import BeautifulSoup

from c4c_cpsv_ap.models import BusinessEvent, Event, LifeEvent
from data.html import FILENAME_HTML_AFFLIGEM_SITEMAP, get_html
from relation_extraction.cities import CityParser, Relations
from relation_extraction.utils import clean_text


class Sitemap:
    name: str
    url: str
    level: int
    children: List

    def __init__(self, name,
                 url,
                 level,
                 parent=None
                 ):
        self.name = name
        self.url = url
        self.level = level
        self.children: List[Sitemap] = []

        if parent is not None:
            self.parent = parent
            self.parent.add_child(self)

    def add_child(self, child):
        self.children.append(child)

    def get_parent(self):
        return self.parent

    def __repr__(self):
        return f'Sitemap(name={self.name}, url={self.url}, level={self.level})'


class AffligemParser(CityParser):
    """
    Parser for Affligem.be
    """

    criterionRequirement = "Voorwaarden"
    rule = "Procedure"
    evidence = "Wat meebrengen"
    cost = "Bedrag"

    # e = "Uitzonderingen"

    def __init__(self, filename_hierarchy=FILENAME_HTML_AFFLIGEM_SITEMAP):
        super(AffligemParser, self).__init__()

        if filename_hierarchy:
            html_hierarhy = get_html(filename_hierarchy)
            self.hierarchy = self.extract_hierarchy(html_hierarhy)

    @staticmethod
    def parse_page(s_html) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

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

    def extract_relations(self, s_html, url, *args, **kwargs) -> Relations:
        """
        (Copied from super method)
        Extracts important CPSV-AP relations from a webpage containing an adminstrative procedure.

        Args:
            s_html: HTML as string
            url: original URL to the webpage

        Returns:
            extracted relations saved in Relations object.
        """

        l = self.parse_page(s_html)

        d = Relations()

        events = list(self.extract_event(s_html, url))
        d.events = events

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

    def extract_event(self, s_html: str, url: str) -> Generator[None, None, Event]:

        try:
            # Check if hierarchy is extracted
            self.hierarchy
        except:
            warnings.warn("Could not hierarcy. Make sure it is provided in init.", UserWarning)
            return

        # TODO
        # Get life vs business event
        # Get event name.

        def match_url(url_actual, url_hierarchy):
            # For affligem

            return url_hierarchy in url_actual

        def iterate(sitemap: Sitemap):

            for child in sitemap.children:

                yield child

                for subchild in iterate(child):
                    yield subchild

        for child in iterate(self.hierarchy):

            if match_url(url, child.url):

                l = []
                parent = child.get_parent()
                while parent.name:
                    l.append(parent.name)

                    parent = parent.get_parent()

                top = l[-1]
                if top.lower() == "leven":
                    # life event:
                    event = LifeEvent(name=' - '.join(l[-2::-1]), identifier=None)
                elif top.lower() == 'werken':
                    event = BusinessEvent(name=' - '.join(l[-2::-1]), identifier=None)
                else:
                    event = Event(name=' - '.join(l[::-1]), identifier=None)

                yield event

        # if url:
        #     url_parsed = urllib.parse.urlparse(url)
        #     url_parsed.path
        #     return url_parsed.path
        #
        # soup = BeautifulSoup(s_html, 'html.parser')
        #
        # unordered_lists = soup.find_all('ul')
        #
        # ul_leven = [ul for ul in unordered_lists if ul]
        #
        # hierarchy = {}
        #
        # a = soup.find('title')
        #
        # def f(tag: bs4.element.Tag) -> bool:
        #
        #     key_href = "href"
        #     if not tag.has_attr(key_href):
        #         return False
        #
        #     href = tag.get(key_href)
        #
        #     return True
        #
        # for _ in soup.find_all("a"):
        #     href = _.get("href")
        #
        # for _ in soup.find("a").find_all(f):
        #     _
        #
        # return

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

        sitemap = Sitemap(None,
                          None,
                          level=0)

        d_latest_lvl: Dict[int, Sitemap] = {}
        d_latest_lvl[sitemap.level] = sitemap

        for li in main_content.find('ul').find_all('li'):
            class_ = li.get("class")[0]
            level = int(class_.rsplit('_', 1)[-1])

            hyperlink = li.find('a')
            name = hyperlink.get_text()  # TODO clean.
            url = hyperlink.get("href")

            parent = d_latest_lvl[level - 1]

            # Update parents children
            new_sitemap = Sitemap(name=name,
                                  url=url,
                                  level=level,
                                  parent=parent)

            # Update latest
            d_latest_lvl[new_sitemap.level] = new_sitemap

        # soup.find_all('ul')

        return sitemap
