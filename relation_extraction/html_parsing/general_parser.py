import inscriptis
import justext
import trafilatura
from bs4 import BeautifulSoup
from readabilipy import simple_json_from_html_string
from readability import Document


class GeneralHTMLParser():
    """
    For further processing, process the HTML such that junk is removed.
    """

    def __init__(self, html):
        self.html = html

    def _sandbox(self,
                 case=5
                 ):

        # Trafilatura
        if case == 0:
            text = trafilatura.extract(self.html,
                                       favor_recall=True)
            xml = trafilatura.extract(self.html,
                                      favor_recall=True,
                                      )

        # Justext
        elif case == 1:
            language = "English"
            language = "Italian"
            paragraphs = justext.justext(self.html, justext.get_stoplist(language))

            class hashabledict(dict):
                def __hash__(self):
                    return hash(tuple(sorted(self.items())))

            s = set()

            for paragraph in paragraphs:
                d = hashabledict()
                d.update({"heading": paragraph.is_heading,
                          "boiler": paragraph.is_boilerplate,
                          "class": paragraph.class_type,
                          "cf": paragraph.cf_class
                          })

                s.add(d)

            # All combinations
            for e in s:
                print(e)

            # Debug
            for e in s:
                if e["boiler"] == True:
                    print(e)

            # Headers
            for paragraph in paragraphs:
                if paragraph.is_heading:
                    print(paragraph.text)

            for paragraph in paragraphs:
                if paragraph.class_type != 'bad':
                    print(paragraph.text)

            for paragraph in paragraphs:
                if paragraph.class_type == 'good':
                    print(paragraph.text)

        # BeautifulSoup
        elif case == 2:
            soup = BeautifulSoup(self.html, 'html.parser')

        # Inscriptis
        elif case == 3:

            text = inscriptis.get_text(self.html)
            print(text)
            pass

        elif case == 4:
            article = simple_json_from_html_string(self.html)
            # article = simple_json_from_html_string(self.html, use_readability=True)
            article

        elif case == 5:
            doc = Document(self.html)
            html_cleaned = doc.summary()

            self._export(html_cleaned)

        return

    @staticmethod
    def _export(html, filename="GEN_PARSER_DEBUG.html"):
        with open(filename, "w") as f:
            f.write(html)
