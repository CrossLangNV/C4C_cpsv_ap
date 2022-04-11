import copy
from typing import List

import justext
import lxml.html
from justext.core import classify_paragraphs, ParagraphMaker, revise_paragraph_classification

from connectors.bert_classifier import BERTConnector
from relation_extraction.html_parsing.utils import clean_tag_text, dom_write, get_lxml_el_from_paragraph


class GeneralParagraph(justext.core.Paragraph):
    """
    A group of sentences that belong together
    """

    heading: bool

    @classmethod
    def from_justext_paragraph(cls, paragraph: justext.core.Paragraph):
        """
        Our adjustment of the justext Paragraph

        Args:
            paragraph:

        Returns:

        """

        class Object(object):
            pass

        path = Object()
        path.dom = None
        path.xpath = None
        self = cls(path)  # Emtpy init
        self.__dict__ = copy.deepcopy(paragraph.__dict__)

        return self

    def __repr__(self):
        class_name = self.__class__.__module__ + "." + self.__class__.__name__

        return f"<{class_name}> {self.text}"

    @property
    def is_heading(self) -> bool:
        """
        self.heading overwrites this call. This forces is_heading to not use regex pattern.
        """

        try:
            # Check if exists
            return self.heading
        except AttributeError:
            return super(GeneralParagraph, self).is_heading


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
                          style_boilerplate="background-color :#FF934F;",
                          style_regular="background-color: white;"  # color:#f88f93;
                          ):

        """
        Do same processing, but save as HTML with important annotations.
        """

        paragraphs = self.justext(html, stoplist)

        dom_debug = self.get_dom_clean(html)

        for paragraph in paragraphs:
            el = get_lxml_el_from_paragraph(dom_debug,
                                            paragraph)

            # Overwrite all else
            if paragraph.is_boilerplate:
                el.attrib["style"] = el.attrib.get("style", "") + style_boilerplate
                # "background-color:powderblue;

            elif paragraph.is_heading:
                el.attrib["style"] = el.attrib.get("style", "") + style_header
                # el.attrib["style"] = el.attrib.get("style", "") + style_header

            # Text
            else:
                el.attrib["style"] = el.attrib.get("style", "") + style_regular

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


class TitleClassificationJustextWrapper(JustextWrapper):
    """
    Headers will be detected with a text classifier.
    """

    def __init__(self, *args, **kwargs):
        super(TitleClassificationJustextWrapper, self).__init__(*args, **kwargs)

        # Initialise classifier model
        self._title_classifier_connector = BERTConnector(url="http://title_classifier:5000")
        labels = self._title_classifier_connector.get_labels()
        self._i_label_title = labels.names.index("title")

    def make_paragraphs(self,
                        dom,
                        verbose=1) -> List[GeneralParagraph]:
        """
        Change heading already to include <strong/> and <b/> as headers

        Args:
            dom:

        Returns:

        TODO
         * Include <b/>

        """

        paragraphs = super(TitleClassificationJustextWrapper, self).make_paragraphs(dom)

        # One at a time
        one_at_a_time = False
        if one_at_a_time:
            for i, paragraph in enumerate(paragraphs):
                if verbose:
                    print(f"Paragraph extraction {i + 1}/{len(paragraphs)}")

                el = get_lxml_el_from_paragraph(dom,
                                                paragraph)

                # Pre-classify headings.
                if self._classify_title(paragraph, el):
                    paragraph.heading = True

        # ALl at once
        else:

            l_el = [get_lxml_el_from_paragraph(dom,
                                               par) for par in paragraphs]

            if verbose:
                print(f"Paragraph extraction - Start")

            l_b_titles = self._classify_title_all(paragraphs, l_el)

            if verbose:
                print(f"Paragraph extraction - End")

            for i, (paragraph, b_title) in enumerate(zip(paragraphs, l_b_titles)):

                # Pre-classify headings.
                if b_title:
                    paragraph.heading = True

        return paragraphs

    def _classify_title(self,
                        paragraph: GeneralParagraph,
                        element: lxml.html.HtmlElement,
                        threshold: float = .5,  # Optional, to possibly play with later.
                        ) -> bool:

        result = self._title_classifier_connector.post_classify_text(paragraph.text)
        p_title = result.probabilities[self._i_label_title]

        return p_title >= threshold

    def _classify_title_all(self,
                            l_paragraph: List[GeneralParagraph],
                            l_element: List[lxml.html.HtmlElement],
                            threshold: float = .5,  # Optional, to possibly play with later.
                            ) -> List[bool]:

        text_lines = [par.text for par in l_paragraph]

        results = self._title_classifier_connector.post_classify_text_lines(text_lines)
        l_p_title = [l_p_i[self._i_label_title] for l_p_i in results.probabilities]

        l_b_title = [p >= threshold for p in l_p_title]

        return l_b_title
