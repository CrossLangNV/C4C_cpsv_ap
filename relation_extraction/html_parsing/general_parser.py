import warnings
from typing import FrozenSet, List

import inscriptis
import justext
import lxml
import lxml.html
from bs4 import BeautifulSoup

from relation_extraction.html_parsing.justext_wrapper import GeneralParagraph, JustextWrapper
from relation_extraction.html_parsing.parsers import Section
from relation_extraction.html_parsing.utils import _get_language_full_from_code, clean_tag_text, dom_write, \
    get_lxml_el_from_paragraph


class GeneralSection(Section):
    """
    A section contains a title and text
    """


class GeneralHTMLParser2:
    """
    After refactoring...
    """

    _stoplist: FrozenSet[str]

    def __init__(self,
                 html: str,
                 language: str,
                 justext_wrapper: JustextWrapper = None):
        """

        Args:
            html: HTML as string
            language: language code. ISO language name (e.g. English, Dutch...)
            justext_wrapper: (Optional), JustextWrapper for paragraph extraction.
        """

        self._html = html

        self.set_stoplist(language)

        if justext_wrapper is None:
            justext_wrapper = JustextWrapper()

        self._justext_wrapper = justext_wrapper

    def set_stoplist(self, language):
        try:
            stoplist = justext.get_stoplist(language)
        except ValueError as e:  # Perhaps language code is given instead of language
            warnings.warn(f"Expected full language name: \"{language}\". Trying to cast to language code instead ",
                          UserWarning)
            try:
                _language = _get_language_full_from_code(language_code=language)
            except:
                raise e
            else:
                self._stoplist = justext.get_stoplist(_language)
        else:
            self._stoplist = stoplist

    def get_paragraphs(self) -> List[GeneralParagraph]:
        """
        Get all the paragraphs from the HTML for further processing.

        Returns:

        """

        paragraphs = self._justext_wrapper.justext(self._html,
                                                   self._stoplist)

        return paragraphs

    def get_sections(self) -> List[GeneralSection]:

        last_section = None
        l_sections = []

        for paragraph in self.get_paragraphs():

            if paragraph.is_boilerplate:
                continue  # Skip

            text = paragraph.text

            if paragraph.is_heading:
                if last_section is not None:
                    l_sections.append(last_section)

                # Make a new section.
                last_section = GeneralSection(title=text,
                                              paragraphs=[])

            else:
                if last_section is None:
                    last_section = GeneralSection(title=None,
                                                  paragraphs=[])

                last_section.add_paragraph(text)

        if last_section != l_sections[-1]:
            l_sections.append(last_section)

        return l_sections

    @property
    def dom(self):
        return self._justext_wrapper.get_dom_clean(self._html)

    def get_lxml_element_from_paragraph(self, paragraph: GeneralParagraph):

        el = get_lxml_el_from_paragraph(self.dom,
                                        paragraph)

        return el


class GeneralHTMLParser:
    """
    For further processing, process the HTML such that junk is removed.
    """

    def __init__(self, html, language):
        self.html = html
        self.language = language

    def clean(self,
              filename,
              ):
        """
        Based on Justext, we try to clean the HTML.
         * (Done) Remove unnecessary tags. E.g. <form/>
         * (WIP)  Remove boilerplate text.

        This is needed to be able to use the output from Justext and go back to the original HTML.

        Returns:
        """

        justext_preprocessor = justext.core.preprocessor

        paragraphs = justext.justext(self.html, justext.get_stoplist(self.language),
                                     preprocessor=justext_preprocessor)

        html_root = lxml.html.fromstring(self.html)
        # Same cleaning is needed to be able to go back from paragraphs to DOM (make use of the Xpath info).
        html_root = justext_preprocessor(html_root)

        # bold/strong headers
        def _make_strong_header(html_root, paragraphs):
            """
            Heuristic: If a paragraph is fully <strong>, it is most likely a title
            """

            for paragraph in paragraphs:
                el = get_lxml_el_from_paragraph(html_root,
                                                paragraph)

                # is there a <strong>?
                if l_strong_children := el.xpath(".//strong"):
                    strong = l_strong_children[0]

                    if clean_tag_text(strong) == clean_tag_text(el):
                        # All text is "strong":

                        # (!) Do not use paragraph.is_heading
                        paragraph.heading = True

            return html_root, paragraphs

        html_root, paragraphs = _make_strong_header(html_root, paragraphs)

        html_root, paragraphs = self._annot_html(html_root, paragraphs)

        dom_write(html_root,
                  filename)

        return

    def get_paragraphs(self) -> List[justext.paragraph.Paragraph]:
        justext_preprocessor = justext.core.preprocessor

        paragraphs = justext.justext(self.html, justext.get_stoplist(self.language),
                                     preprocessor=justext_preprocessor)

        return paragraphs

    def _annot_html(self, html_root, paragraphs,
                    style_boiler="color: gray; text-decoration: line-through;",
                    style_header="text-decoration: underline;text-decoration-color: red;"
                    ):
        for paragraph in paragraphs:
            e = get_lxml_el_from_paragraph(html_root,
                                           paragraph)

            if paragraph.is_boilerplate:
                e.attrib["style"] = e.attrib.get("style", "") + style_boiler

            if paragraph.heading:
                e.attrib["style"] = e.attrib.get("style", "") + style_header

        return html_root, paragraphs

    def _sandbox(self,
                 case=1
                 ):

        # Trafilatura
        if case == 0:
            text = trafilatura.extract(self.html,
                                       favor_recall=True,
                                       )
            #
            xml = trafilatura.extract(self.html,
                                      favor_recall=True,
                                      output_format="xml",
                                      include_comments=True,
                                      )
            self._export(xml)

            body, text, l = trafilatura.baseline(self.html)

            html_out = lxml.etree.tostring(body,
                                           pretty_print=True,
                                           encoding="utf-8").decode()
            print(html_out)

            self._export(html_out)

            # Does not work
            metadata = trafilatura.extract_metadata(self.html,
                                                    # default_url=None, date_config=None, fastmode=False,
                                                    # author_blacklist=None
                                                    )

        # Justext
        elif case == 1:
            language = "English"
            language = "Italian"
            language = "Dutch"
            paragraphs = justext.justext(self.html, justext.get_stoplist(language))

            i = 248
            par_i = paragraphs[i]

            xpath_i = par_i.xpath

            import re
            pattern = r"/(\w+)\[(\d+)\]"
            l_tags = re.findall(pattern, xpath_i)

            html_tree = lxml.html.fromstring(self.html)
            roottree = html_tree.getroottree()
            e_i = html_tree.xpath(xpath_i)[0]

            _xpath_i = roottree.getpath(e_i)

            for paragraph in paragraphs:
                paragraph.x

            for paragraph in paragraphs:
                if paragraph.is_heading:
                    print(paragraph.text)

            l_tags[1][0]

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

        return

    @staticmethod
    def _export(html, filename="GEN_PARSER_DEBUG.html"):
        with open(filename, "w") as f:
            f.write(html)

    def _sandbox_inscriptis(self):
        """
        Inscriptis is good at:
         * Correctly "rendering" text out of HTML tags. e.g. lists, urls etc.
         * TODO Good to use for html2text conversion!
         * Structure given by indentations which are calculated by the depth info of tags.
        """
        text = inscriptis.get_text(self.html)

        # annot = inscriptis.get_annotated_text(self.html)

        rules = {'h1': ['heading', 'h1'],
                 'h2': ['heading', 'h2'],
                 'b': ['emphasis'],
                 'table': ['table']
                 }

        from inscriptis.css_profiles import CSS_PROFILES
        css = CSS_PROFILES['strict'].copy()

        config = inscriptis.model.config.ParserConfig(annotation_rules=rules,
                                                      css=css)

        annot = inscriptis.get_annotated_text(self.html, config)

        from lxml.html import fromstring

        html_tree = fromstring(self.html)

        body = html_tree.body  # html_tree.getchildren()[1]
        div0 = body.getchildren()[0]

        parser = inscriptis.Inscriptis(html_tree,
                                       config)

        parser.get_text()

        print(text)
        return text
