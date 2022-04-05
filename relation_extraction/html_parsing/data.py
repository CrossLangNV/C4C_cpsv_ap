import errno
import hashlib
import os.path
import re
import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import justext
import langcodes
import lxml
import yaml
from pydantic import BaseModel, validator

from data.html import get_html, url2html
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser2, \
    get_lxml_el_from_paragraph
from relation_extraction.html_parsing.utils import export_jsonl, makeParentLine

FOLDER_TMP = os.path.join(os.path.dirname(__file__), "TMP")


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


class DataItem(BaseModel):
    label_names: List[str] = []
    url: str
    text: str
    html_el: str
    html_parents: str


def data_generic(url: str,
                 language_code: str,
                 filename_out: str = None
                 ) -> List[DataItem]:
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

    language_full = langcodes.get(language_code).display_name()

    FILENAME_INPUT_HTML = os.path.join(FOLDER_TMP, f"{basename}.html")

    try:
        html = get_html(FILENAME_INPUT_HTML)
    except FileNotFoundError:
        url2html(url, FILENAME_INPUT_HTML)
        html = get_html(FILENAME_INPUT_HTML)
    except OSError as oserr:
        # Filename too long
        if oserr.errno == errno.ENAMETOOLONG:

            basename = f"{basename[:50]}_{hashlib.sha1(basename.encode()).hexdigest()}"
            # Make a shorter filename
            FILENAME_INPUT_HTML = os.path.join(FOLDER_TMP, f"{basename}.html")

            try:
                html = get_html(FILENAME_INPUT_HTML)
            except FileNotFoundError:
                url2html(url, FILENAME_INPUT_HTML)
                html = get_html(FILENAME_INPUT_HTML)

        else:
            raise  # re-raise previously caught exception

    if filename_out is None:
        filename_out = os.path.join(FOLDER_TMP, f"TITLE_{basename}.jsonl")

    parser = GeneralHTMLParser2(html,
                                language=language_full)

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


def data_turnhout(url="https://www.turnhout.be/inname-openbaar-domein",
                  language=None,
                  language_code="NL",
                  filename_out=None) -> List[DataItem]:
    """

    Args:
        url:
        language:
        language_code:
        filename_out: To save output as json-line.
    Returns:

    TODO call data_generic
    """

    re_pattern = re.compile(r"[^a-zA-Z0-9]+")
    basename = re_pattern.sub("_", url)

    if language is None:
        language = langcodes.get(language_code).display_name()

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
