from typing import List

import justext
from justext.core import classify_paragraphs, ParagraphMaker, revise_paragraph_classification

from relation_extraction.html_parsing.general_parser import GeneralParagraph, get_lxml_el_from_paragraph
from relation_extraction.html_parsing.utils import clean_tag_text, dom_write


class JustextWrapper:
    """
    Wrapper around Justext.

    Will have identical functionality as the original one, but make it more convenient to change and adapt the flow.
    """

    def justext(self,
                html_text: str,
                stoplist,
                **kwargs
                ) -> List[GeneralParagraph]:
        """
        (!) Identical to justext.justext(*args, **kwargs) 3.0.0

        Converts an HTML page into a list of classified paragraphs. Each paragraph
        is represented as instance of class ˙˙justext.paragraph.Paragraph˙˙.
        """

        dom = self.get_dom_clean(html_text, **kwargs)

        paragraphs = self.make_paragraphs(dom)

        # (!) paragraph.headig is decided here by calling paragraph.is_heading
        classify_paragraphs(paragraphs, stoplist, **kwargs)
        revise_paragraph_classification(paragraphs, **kwargs)

        # paragraphs = justext.justext(html_text, stoplist, *args, **kwargs)

        return paragraphs

    def get_dom_clean(self, html_text, *args, **kwargs):
        dom = self._html_to_dom(html_text, *args, **kwargs)
        dom = self._preprocessor(dom)

        return dom

    def make_paragraphs(self, dom) -> List[GeneralParagraph]:
        """Init of the paragraphs"""

        paragraphs = ParagraphMaker.make_paragraphs(dom)

        # (!) New
        paragraphs = list(map(GeneralParagraph.from_justext_paragraph, paragraphs))

        return paragraphs

    def _html_to_dom(self, html_text, *args, **kwargs):
        """(!) Without preprocessing. You probably want to use *get_dom_clean* instead."""
        return justext.core.html_to_dom(html_text, *args, **kwargs)

    def _preprocessor(self, dom):
        return justext.core.preprocessor(dom)

    def _export_debugging(self, html, stoplist,
                          filename_out,
                          style_header="background-color: #70D6FF;",  # color:white;
                          style_boilerplate="background-color :#FF934F;"  # color:#f88f93;
                          ):

        """
        Do same processing, but save as HTML with important annotations.
        """

        paragraphs = self.justext(html, stoplist)

        dom_debug = self.get_dom_clean(html)

        for paragraph in paragraphs:
            el = get_lxml_el_from_paragraph(dom_debug,
                                            paragraph)

            if paragraph.is_heading:
                el.attrib["style"] = el.attrib.get("style", "") + style_header
                # el.attrib["style"] = el.attrib.get("style", "") + style_header

            # Overwrite all else
            if paragraph.is_boilerplate:
                el.attrib["style"] = style_boilerplate
                # "background-color:powderblue;

        dom_write(dom_debug,
                  filename_out
                  )


class BoldJustextWrapper(JustextWrapper):
    """
    Headers that are in full bold will also be detected as heading

    TODO
     * Detect both <b/> and <strong/>
    """

    def make_paragraphs(self, dom) -> List[GeneralParagraph]:
        """
        Change heading already to include <strong/> and <b/> as headers

        Args:
            dom:

        Returns:

        TODO
         * Include <b/>

        """

        paragraphs = super(BoldJustextWrapper, self).make_paragraphs(dom)

        # (!) Initialise is_heading.
        # TODO might be nicer to change the "is_heading" classifier in Paragraph class
        paragraphs = self._heading_include_strong(paragraphs, dom)

        return paragraphs

    def _heading_include_strong(self, paragraphs, dom):
        """
        Heuristic: If a paragraph is fully <strong/>, it is most likely a title.

        Overwrites input paragraphs
        """

        for paragraph in paragraphs:
            el = get_lxml_el_from_paragraph(dom,
                                            paragraph)

            # is there a <strong/> or <b/>?
            if l_strong_children := (el.xpath(".//strong") + el.xpath(".//b")):
                strong = l_strong_children[0]

                if clean_tag_text(strong) == clean_tag_text(el):
                    # All text is "strong":

                    # (!) Do not use paragraph.is_heading
                    paragraph.heading = True

        return paragraphs
