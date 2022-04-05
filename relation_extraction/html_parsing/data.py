import os.path
import re
import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import justext
import lxml
import yaml
from pydantic import BaseModel, validator

from data.html import get_html, url2html
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser2, \
    get_lxml_el_from_paragraph
from relation_extraction.html_parsing.utils import export_jsonl

FOLDER_TMP = os.path.join(os.path.dirname(__file__), "TMP")
D_LANG = {"NL": "Dutch"}


@dataclass
class MunicipalityModel:
    """
    TODO
     * Be able to access country
    """
    language: Optional[str]
    procedures: List[str]

    name: str

    # _country: "CountryModel"


class CountryModel(BaseModel):
    language: Optional[str]
    municipalities: List[MunicipalityModel]

    name: str

    @validator("municipalities", pre=True)
    def convert_dict_to_list(cls, value: Union[List, Dict], values) -> List[MunicipalityModel]:
        if isinstance(value, dict):

            l = []
            for name, value in value.items():

                # Get default language
                if "language" not in value:
                    value["language"] = values["language"]

                muni = MunicipalityModel(name=name, **value)
                l.append(muni)

            return l

        elif isinstance(value, list):

            l = [MunicipalityModel(**d) for d in value]
            return l

        return value


class DataCountries(BaseModel):
    countries: List[CountryModel]

    @validator("countries", pre=True)
    def convert_dict_to_list(cls, v: Union[List[CountryModel], Dict[str, dict]]) -> List[CountryModel]:
        if isinstance(v, dict):

            l = []
            for name, value in v.items():
                country = CountryModel(name=name, **value)
                l.append(country)

            return l

        return v

    @classmethod
    def load_yaml(cls,
                  filename,
                  remove_template=True,
                  key_template_country="Country"
                  ) -> "DataCountries":
        with open(filename) as file:
            dict_tmp = yaml.full_load(file)

        data = cls(**dict_tmp)

        if remove_template:
            # pop template data

            if key_template_country in data.country_names():

                i_template = next(i for i, v in enumerate(data.countries) if lambda v: v.name == key_template_country)
                data.countries.pop(i_template)

            else:
                warnings.warn(
                    f"Could not find template ({key_template_country}) in the file. Countries: {data.country_names()}",
                    UserWarning)

        return data

    def get(self, country_name, default=None) -> CountryModel:
        """
        Return the country based on name

        Args:
            country_name: Made it case-independent.

        Returns:
        """

        for country in self.countries:
            if country.name.lower() == country_name.lower():
                return country

        return default

    def country_names(self) -> List[str]:
        return [country.name for country in self.countries]


# class DataURLS(BaseModel):


# class


class DataItem(BaseModel):
    label_names: List[str] = []
    url: str
    text: str
    html_el: str
    html_parents: str


def data_turnhout(url="https://www.turnhout.be/inname-openbaar-domein",
                  language=None,
                  language_code="NL",
                  filename_out=None) -> List[dict]:
    """

    Args:
        url:
        language:
        language_code:
        filename_out: To save output as json-line.
    Returns:

    """

    re_pattern = re.compile(r"[^a-zA-Z0-9]+")
    basename = re_pattern.sub("_", url)

    if language is None:
        language = D_LANG.get(language_code.upper())

    FILENAME_INPUT_HTML = os.path.join(FOLDER_TMP, f"{basename}.html")

    if filename_out is None:
        filename_out = os.path.join(FOLDER_TMP, f"TITLE_{basename}.jsonl")

    try:
        html = get_html(FILENAME_INPUT_HTML)
    except FileNotFoundError:
        url2html(url, FILENAME_INPUT_HTML)
        html = get_html(FILENAME_INPUT_HTML)

    parser = GeneralHTMLParser2(html,
                                language=language)

    parser.get_paragraphs()

    l_data = []

    for paragraph in parser.get_paragraphs():
        if paragraph.is_boilerplate:
            continue

        label_heading = paragraph.is_heading  # bool

        text = paragraph.text

        html_root = lxml.html.fromstring(parser.html)

        # Same cleaning is needed to be able to go back from paragraphs to DOM (make use of the Xpath info).
        justext_preprocessor = justext.core.preprocessor
        html_root = justext_preprocessor(html_root)

        el = get_lxml_el_from_paragraph(html_root,
                                        paragraph)

        tree = el.getroottree()
        tree.getpath(el)

        s_html = lxml.html.tostring(el, encoding="UTF-8").decode("UTF-8")

        def makeParentLine(node, attach_head=False, questionContains=None):
            # Add how much text context is given. e.g. 2 would mean 2 parent's text
            # nodes are also displayed
            # if questionContains is not None:
            #     newstr = doesThisElementContain(questionContains, lxml.html.tostring(node))
            # else:
            newstr = lxml.html.tostring(node, encoding="UTF-8").decode('utf8')
            parent = node.getparent()
            while parent is not None:
                if attach_head and parent.tag == 'html':
                    newstr = lxml.html.tostring(parent.find(
                        './/head'), encoding='utf8').decode('utf8') + newstr
                tag, items = parent.tag, parent.items()
                attrs = " ".join(['{}="{}"'.format(x[0], x[1]) for x in items if len(x) == 2])
                newstr = '<{} {}>{}</{}>'.format(tag, attrs, newstr, tag)
                parent = parent.getparent()
            return newstr

        s_html_parents = makeParentLine(el)

        TITLE = "title"
        label_names = [TITLE] if label_heading else []

        item = DataItem(**{"label_names": label_names,
                           "text": text,
                           "url": url,
                           "html_el": s_html,
                           "html_parents": s_html_parents})

        l_data.append(item)

    if filename_out:
        export_jsonl(l_data, filename_out)

    return l_data

    # html = url2html(url)
    #
    # parser = HeaderHTMLParser(html)
    # sections = parser.get_sections()
    # for section in sections:
    #     section
    #
    # parser_gen = GeneralHTMLParser(html)


def data_extraction():
    """

    Workflow:
    - Loop over files with available headers
    - Remove boilerplate
    - Extract paragraphs
    - Extract clean text and HTML
    - Label header and non-header
    - Save clean text, HTML, label as JSON-LD
    - Split training and validation?

    Returns:

    """

    data_turnhout()

    pass


if __name__ == '__main__':
    data_extraction()
