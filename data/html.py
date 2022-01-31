import codecs
import os

# Example
FILENAME_HTML = os.path.join(os.path.dirname(__file__),
                             "relation_extraction",
                             'Financial plan_ how to prepare an effective financial plan.html')


def get_html(filename, encoding='utf-8') -> str:
    with codecs.open(filename, 'r', encoding=encoding) as f:
        return f.read()
