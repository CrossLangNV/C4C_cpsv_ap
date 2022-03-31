import codecs
import os

import requests
from bs4 import BeautifulSoup

# Example

FILENAME_HTML = os.path.join(os.path.dirname(__file__),
                             "relation_extraction",
                             'Financial plan_ how to prepare an effective financial plan.html')

URL_HTML_AFFLIGEM = "https://www.affligem.be/Affligem/Nederlands/Leven/identiteitsbewijzen,-rijbewijzen-en-afschriften/afschriften-uittreksels-getuigschriften/wettiging-van-handtekening/page.aspx/169#"
FILENAME_HTML_AFFLIGEM = os.path.join(os.path.dirname(__file__),
                                      "relation_extraction",
                                      'AFFLIGEM_HANDTEKENING.html')

FILENAME_HTML_AFFLIGEM_SITEMAP = os.path.join(os.path.dirname(__file__),
                                              "relation_extraction",
                                              'AFFLIGEM_SITEMAP.html')


def get_html(filename, encoding='utf-8') -> str:
    with codecs.open(filename, 'r', encoding=encoding) as f:
        return f.read()


def url2html(url, filename=None):
    # def get_encoding(rawdata):
    #     result = chardet.detect(rawdata)
    #     charenc = result['encoding']
    #     return charenc
    #
    # with urllib.request.urlopen(url) as fp:
    #     mybytes = fp.read()
    #
    #     enc = get_encoding(mybytes)
    #
    #     s_html = mybytes.decode(enc)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    s_html = soup.prettify()

    if filename:
        with open(filename, "w+", encoding="utf-8") as fp:
            fp.write(soup.prettify())

    return s_html
