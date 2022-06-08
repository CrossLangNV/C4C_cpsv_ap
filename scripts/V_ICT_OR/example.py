"""
docker compose run cpsv_ap python scripts/extract_cpsv_ap.py -g -o scripts/V_ICT_OR/example1.rdf --html_parsing scripts/V_ICT_OR/example1.html -l NL -c BE -m https://www.berlare.be/adreswijziging-binnen-berlare_2.html
"""
import os.path
from typing import List

from data.html import get_html, url2html
from data.utils.sitemap import scrape_sitemap, SitemapUrl
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser
from relation_extraction.html_parsing.justext_wrapper import BoldJustextWrapper
from scripts.extract_cpsv_ap import extract_cpsv_ap_from_html

DIR_VICTOR = os.path.dirname(__file__)


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


def all_html_parsing(l_links: List[SitemapUrl]):
    for link in l_links:

        if bool(link.children):
            continue

        if 0:
            if not os.path.exists(filename_html_sitemap):
                url2html(url,
                         filename_html_sitemap
                         )
            html_sitemap = get_html(filename_html_sitemap)
        html = url2html(link.url)
        lang_code = "NL"
        justext_wrapper_class = BoldJustextWrapper

        html_parser = GeneralHTMLParser(html,
                                        language=lang_code,
                                        justext_wrapper_class=justext_wrapper_class
                                        )

        filename_html_parsing = os.path.join(DIR_VICTOR, "parse_html_i.html")
        # html_parser._justext_wrapper._export_debugging(filename_html_parsing)

        sections = html_parser.get_sections()

        section0 = sections[0]

        section0.level


if __name__ == '__main__':

    b = 1
    if b:
        l_links = scrape_sitemap("https://www.berlare.be/sitemap.aspx")

        b = 0
        if b:
            process_links(l_links)

        b = 1
        if b:
            all_html_parsing(l_links)

    b = 0
    if b:
        url = "https://www.berlare.be/adreswijziging-binnen-berlare_2.html"
        main_single_example(url)
