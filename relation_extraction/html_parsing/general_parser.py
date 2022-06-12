import re
from typing import List, Type

from relation_extraction.html_parsing.justext_wrapper import GeneralParagraph, get_stoplist, JustextWrapper
from relation_extraction.html_parsing.parsers import Section
from relation_extraction.html_parsing.utils import get_lxml_el_from_paragraph


class GeneralSection(Section):
    """
    A section contains a title and text
    """


class GeneralHTMLParser:
    """
    After refactoring...

    Uses Justext for html parsing
    """

    def __init__(self,
                 html: str,
                 language: str,
                 justext_wrapper_class: Type[JustextWrapper] = None):
        """

        Args:
            html: HTML as string
            language: ISO language name (e.g. English, Dutch...)
            justext_wrapper_class: (Optional), JustextWrapper for paragraph extraction.
        """

        self._html = html

        if justext_wrapper_class is None:
            justext_wrapper_class = JustextWrapper

        stoplist = get_stoplist(language)
        self._justext_wrapper = justext_wrapper_class(html_text=self._html,
                                                      stoplist=stoplist)

    def get_paragraphs(self) -> List[GeneralParagraph]:
        """
        Get all the paragraphs from the HTML for further processing.

        Returns:
        """

        return self._justext_wrapper.paragraphs

    def get_sections(self, include_sub=False) -> List[GeneralSection]:

        prev_section = None
        l_sections = []

        for paragraph in self.get_paragraphs():

            if paragraph.is_boilerplate:
                continue  # Skip

            text = paragraph.text

            if paragraph.is_heading:
                if prev_section is not None:
                    l_sections.append(prev_section)

                # Try to get the level of the heading
                try:
                    # Get the last part of the path
                    el_x = paragraph.dom_path.rsplit(".", 1)[-1]
                    level = int(re.findall(r"h(\d)", el_x)[0])
                except:
                    level = None

                # Make a new section.
                prev_section = GeneralSection(title=text,
                                              paragraphs=[],
                                              level=level)

            else:
                # This section has no title (e.g. introduction)
                if prev_section is None:
                    prev_section = GeneralSection(title="",
                                                  paragraphs=[])

                prev_section.add_paragraph(text)

        if prev_section is not None:
            if (l_sections == []) or (prev_section != l_sections[-1]):
                l_sections.append(prev_section)

        return l_sections

    @property
    def dom(self):
        return self._justext_wrapper.get_dom_clean()

    def get_lxml_element_from_paragraph(self, paragraph: GeneralParagraph):

        el = get_lxml_el_from_paragraph(self.dom,
                                        paragraph)

        return el
