import warnings
from typing import FrozenSet, List

import justext

from relation_extraction.html_parsing.justext_wrapper import GeneralParagraph, JustextWrapper
from relation_extraction.html_parsing.parsers import Section
from relation_extraction.html_parsing.utils import _get_language_full_from_code, get_lxml_el_from_paragraph


class GeneralSection(Section):
    """
    A section contains a title and text
    """


class GeneralHTMLParser:
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
