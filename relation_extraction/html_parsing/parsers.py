import abc
import re
import warnings
from typing import List, Union

from bs4 import BeautifulSoup, Tag

from relation_extraction.utils import clean_text


class Section(list):
    """
    Contains section info of a (web)page
    """

    def __init__(self,
                 title: str,
                 paragraphs: List[str],
                 level: int = None):
        _l = [title] + paragraphs
        super(Section, self).__init__(_l)

        if level is not None:
            self._level = level

    @property
    def title(self):
        """
        Title of the (sub)section
        Returns:

        """

        return self[0]

    @property
    def paragraphs(self) -> List[str]:
        """
        Text/paragraphs contained within the section, excluding the title.
        Returns:

        """

        return self[1:]

    def paragraphs_text(self, delimiter="\n") -> str:
        """Joins all the paragraphs in single string."""
        return delimiter.join(self.paragraphs)

    @property
    def level(self) -> int:
        """
        The level of the (sub)section: h1, h2, h3...
        """
        return self._level

    def get_all_text_blocks(self) -> List[str]:
        """
        All text, including the section title within this section.

        Returns:
            List of strings: [title, paragraph1, paragraph2...].
        """

        return self  # [self.title] + self.paragraphs

        # raise NotImplementedError()

    def get_all_text(self, delimiter="\n"):
        return delimiter.join(self.get_all_text_blocks())

    def add_paragraph(self, paragraph: str):
        """To iteratively add the paragraphs"""
        self.append(paragraph)


class HTMLParser(abc.ABC):
    def __init__(self, html: str):
        self.html = html

    @abc.abstractmethod
    def get_sections(self) -> List[Section]:
        """"""


def deprecated_metaclass(message):
    class DeprecatedMetaclass(type):
        def __init__(cls, name, bases, dct):
            if not hasattr(cls, '__metaclass__'):
                cls.__metaclass__ = DeprecatedMetaclass
            if any(getattr(base, '__metaclass__', None) == DeprecatedMetaclass
                   for base in bases):
                warnings.warn(message, DeprecationWarning, stacklevel=2)
            super(DeprecatedMetaclass, cls).__init__(name, bases, dct)


class HeaderHTMLParser(HTMLParser):

    def __init__(self, *args, **kwargs):
        warnings.warn("Use GeneralParser2 instead", DeprecationWarning)
        super(HeaderHTMLParser, self).__init__(*args, **kwargs)

    def get_sections(self,
                     include_sub=False) -> List[Section]:
        """"""

        soup = BeautifulSoup(self.html, 'html.parser')

        # Find the Title
        h_title = soup.find_all('h1')[-1]
        page_procedure = self._get_page_procedure(h_title)

        l_sections = []

        l_headers = self._get_all_headers(page_procedure)
        for header in l_headers:

            # Header text
            text_header = header.get_text(separator=" ", strip=True)
            text_header = clean_text(text_header, remove_newlines=True)

            l_par = []

            # All following text.
            for sib in header.find_next_siblings():
                text = clean_text(sib.get_text(separator=" ", strip=True), remove_newlines=True)
                if sib.name in ["div", "p", "a"]:
                    l_par.append(text)
                elif sib.name == "li":
                    l_par.append(f"* {text}")
                elif sib.name == "ul":
                    for li in sib.findChildren("li"):
                        text_li = clean_text(li.get_text(separator=" ", strip=True), remove_newlines=True)

                        l_par.append(f"* {text_li}")

                if sib in l_headers:
                    # Only return if sib header is of same depth or higher
                    if not include_sub:
                        # No need to check.
                        break

                    # Depth
                    def get_depth(tag: Tag) -> Union[int, None]:
                        name = tag.name
                        match = re.match(r"h([0-9]+)", name, re.IGNORECASE)
                        if match:
                            depth = int(match.groups()[0])
                            return depth

                    depth_header = get_depth(header)
                    depth_sib = get_depth(sib)
                    if (depth_header is None) or (depth_sib is None):
                        # No depth information, just break.
                        break
                    elif depth_sib <= depth_header:
                        # Equal or higher level header. Thus break
                        break

                    # Else
                    l_par.append(text)

            # Filter empty sentences
            l_par = [s for s in l_par if s]

            if text_header or len(l_par):
                section = Section(title=text_header,
                                  paragraphs=l_par)

                l_sections.append(section)

        return l_sections

    def _get_page_procedure(self, page_procedure_child, n_headers_min=2, n_headers_max=None):
        """
         Start from single element and go up untill multiple headers are returned.

        Args:
            page_procedure_child:
            n_headers_min: Minimum number of headers to retrieve before returning
            n_headers_max: Maximum number of headers to retrieve before returning

         """

        if n_headers_max is None:
            soup = page_procedure_child.find_parents()[-1]
            n_headers_max = len(self._get_all_headers(soup))

        page_procedure = page_procedure_child.parent

        # Check that we can find other headers.
        headers = self._get_all_headers(page_procedure)

        n_headers = len(headers)
        if n_headers >= n_headers_min:
            return page_procedure

        elif n_headers >= n_headers_max:
            # Max number found
            return page_procedure

        # recursively go up
        return self._get_page_procedure(page_procedure,
                                        n_headers_min=n_headers_min,
                                        n_headers_max=n_headers_max)

    def _get_all_headers(self, soup: Union[BeautifulSoup, Tag]) -> List[Tag]:
        return soup.find_all(self._filter_header)

    def _filter_header(self, tag: Tag) -> bool:
        if re.match(r'^h[1-6]$', tag.name):
            return True

        return False
