import copy
import warnings
from typing import FrozenSet, Iterator, List, Tuple

import justext
import lxml.html
from justext.core import classify_paragraphs, ParagraphMaker, revise_paragraph_classification

from connectors.bert_classifier import BERTConnector
from relation_extraction.html_parsing.utils import _get_language_full_from_code, clean_tag_text, dom_write


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

    def __init__(self,
                 html_text: str,
                 stoplist,
                 **kwargs):
        """
        (!) Identical to justext.justext(*args, **kwargs) 3.0.0

        Converts an HTML page into a list of classified paragraphs. Each paragraph
        is represented as instance of class ˙˙justext.paragraph.Paragraph˙˙.
        """

        self._html_text = html_text

        paragraphs = self._make_paragraphs()

        # (!) paragraph.headig is decided here by calling paragraph.is_heading
        classify_paragraphs(paragraphs, stoplist, **kwargs)
        revise_paragraph_classification(paragraphs, **kwargs)

        self._paragraphs = paragraphs

    @property
    def paragraphs(self) -> List[GeneralParagraph]:
        return self._paragraphs

    def get_dom_clean(self, *args, **kwargs) -> lxml.html.HtmlElement:

        dom = self._html_to_dom(self._html_text, *args, **kwargs)
        dom = self._preprocessor(dom)

        return dom

    def _make_paragraphs(self) -> List[GeneralParagraph]:
        """Init of the paragraphs"""

        paragraphs = ParagraphMaker.make_paragraphs(self.get_dom_clean())

        # (!) New
        paragraphs = list(map(GeneralParagraph.from_justext_paragraph, paragraphs))

        return paragraphs

    def _html_to_dom(self, html_text, *args, **kwargs):
        """(!) Without preprocessing. You probably want to use *get_dom_clean* instead."""
        return justext.core.html_to_dom(html_text, *args, **kwargs)

    def _preprocessor(self, dom):
        return justext.core.preprocessor(dom)

    def iterator_paragraph_element(self,
                                   paragraphs: List[GeneralParagraph] = None,
                                   dom=None) -> Iterator[Tuple[GeneralParagraph, lxml.html.HtmlElement]]:

        if paragraphs is None:
            paragraphs = self.paragraphs
        if dom is None:
            dom = self.get_dom_clean()

        for paragraph in paragraphs:
            el = self._get_element_from_paragraph(paragraph,
                                                  dom=dom)

            yield paragraph, el

    def _get_element_from_paragraph(self,
                                    paragraph,
                                    dom=None):

        if dom is None:
            dom = self.get_dom_clean()

        l_e = dom.xpath(paragraph.xpath)
        if len(l_e) != 1:
            raise LookupError(f"Expected exactly one element: {l_e}")

        return l_e[0]

    def _export_debugging(self,
                          filename_out,
                          heading_bg="#70D6FF",
                          boilerplate_bg="#FF934F",
                          regular_bg="white",
                          ):

        """
        Do same processing, but save as HTML with important annotations.
        """

        dom_debug = self.get_dom_clean()

        for paragraph, el in self.iterator_paragraph_element(dom=dom_debug):

            # Wrap content
            # el.attrib["display"] = el.attrib.get("display", "") + "display: inline-block"

            """
            style_header="background-color: white; border:2px dashed #70D6FF; padding:0.03em 0.25em;",
            style_boilerplate="background-color :#FF934F;",
            style_regular="background-color: white;"
            """

            # Both heading and boilerplate:
            if paragraph.is_boilerplate and paragraph.is_heading:

                el.attrib["style"] = el.attrib.get("style",
                                                   "") + f"background: repeating-linear-gradient(-55deg, {boilerplate_bg}, {boilerplate_bg} 20px, {heading_bg} 10px, {heading_bg} 30px);"

                continue

            elif paragraph.is_heading:
                el.attrib["style"] = el.attrib.get("style", "") + f"background-color: {heading_bg};"
                # el.attrib["style"] = el.attrib.get("style", "") + style_header

            # Overwrite all else
            elif paragraph.is_boilerplate:
                el.attrib["style"] = el.attrib.get("style", "") + f"background-color: {boilerplate_bg};"
                # "background-color:powderblue;

                # Text
            else:
                el.attrib["style"] = el.attrib.get("style", "") + f"background-color: {regular_bg};"

        dom_write(dom_debug,
                  filename_out
                  )


class BoldJustextWrapper(JustextWrapper):
    """
    Headers that are in full bold will also be detected as heading
    """

    def _make_paragraphs(self) -> List[GeneralParagraph]:
        """
        Change heading already to include <strong/> and <b/> as headers

        Args:
            dom:

        Returns:

        TODO
         * Include <b/>

        """

        dom = self.get_dom_clean()

        paragraphs = super(BoldJustextWrapper, self)._make_paragraphs()

        # (!) Initialise is_heading.
        # TODO might be nicer to change the "is_heading" classifier in Paragraph class
        paragraphs = self._heading_include_strong(paragraphs, dom)

        return paragraphs

    def _heading_include_strong(self, paragraphs=None, dom=None):
        """
        Heuristic: If a paragraph is fully <strong/>, it is most likely a title.

        Overwrites input paragraphs
        """

        if paragraphs is None:
            paragraphs = self.paragraphs

        if dom is None:
            dom = self.get_dom_clean()

        for paragraph in paragraphs:
            el = self._get_element_from_paragraph(paragraph,
                                                  dom=dom)

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
        # Initialise classifier model
        self._title_classifier_connector = BERTConnector(url="http://title_classifier:5000")
        labels = self._title_classifier_connector.get_labels()
        self._i_label_title = labels.names.index("title")

        super(TitleClassificationJustextWrapper, self).__init__(*args, **kwargs)

    def _make_paragraphs(self,
                         verbose=1) -> List[GeneralParagraph]:
        """
        Change heading already to include <strong/> and <b/> as headers

        Args:
            dom:

        Returns:

        TODO
         * Include <b/>

        """

        dom = self.get_dom_clean()
        paragraphs = super(TitleClassificationJustextWrapper, self)._make_paragraphs()

        # One at a time
        one_at_a_time = False
        if one_at_a_time:
            for i, paragraph in enumerate(paragraphs):
                if verbose:
                    print(f"Paragraph extraction {i + 1}/{len(paragraphs)}")

                el = self._get_element_from_paragraph(paragraph,
                                                      dom)

                # Pre-classify headings.
                if self._classify_title(paragraph, el):
                    paragraph.heading = True

        # ALl at once
        else:

            l_el = [self._get_element_from_paragraph(par, dom) for par in paragraphs]

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


def get_stoplist(language_or_language_code) -> FrozenSet[str]:
    """
    Same as justext.get_stoplist, but tries to convert to language
    Args:
        language_or_language_code: Full language name or ISO 639-1 language code

    Returns:
        stoplist
    """

    try:
        stoplist = justext.get_stoplist(language_or_language_code)
    except ValueError as e:  # Perhaps language code is given instead of language
        warnings.warn(
            f"Expected full language name: \"{language_or_language_code}\". Trying to cast from language code instead ",
            UserWarning)
        try:
            _language = _get_language_full_from_code(language_code=language_or_language_code)
        except:
            raise e
        else:
            return justext.get_stoplist(_language)
    else:
        return stoplist
