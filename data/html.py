import codecs
import os
# Example
import urllib.request

import chardet

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
    def get_encoding(rawdata):
        result = chardet.detect(rawdata)
        charenc = result['encoding']
        return charenc

    with urllib.request.urlopen(url) as fp:
        mybytes = fp.read()

        enc = get_encoding(mybytes)

        mystr = mybytes.decode(enc)

    if filename:
        with open(filename, "w+", encoding="utf-8") as fp:
            fp.write(mystr)

    return mystr
