import hashlib
import hashlib
import os.path
import re
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

import langcodes
import lxml
import yaml
from pydantic import BaseModel, validator

from data.html import get_html, url2html
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser2, \
    GeneralParagraph
from relation_extraction.html_parsing.utils import export_jsonl

FOLDER_TMP = os.path.join(os.path.dirname(__file__), "TMP")


class ParserModel(BaseModel):
    titles: Union[Enum, List[Enum]]  # cls.HeadingChoices

    @validator("titles", pre=True)
    def check_choices(cls, value: Union[str, List[str]], values) -> Union[Enum, List[Enum]]:
        if isinstance(value, cls.titlesChoices):
            return value

        if isinstance(value, list):
            return [cls.check_choices(v_i, values=values) for v_i in value]

        return cls.titlesChoices[value]

    class titlesChoices(Enum):
        html_headings = "html_headings"  # Look at <h2/>, <h3/> ... tags
        html_bold = "html_bold"  # Look at paragraphs/divs completely in <b/>


@dataclass
class MunicipalityModel:
    """
    TODO
     * Be able to access country
    """
    procedures: List[str]
    name: str

    language: Optional[str] = None

    # Optional information on how to parse the webpage
    parser: Optional[ParserModel] = None

    # _country: "CountryModel"

    @validator("parser", pre=True)
    def foo(cls, value, values):
        return value


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

        elif value is None:
            return []

        return value

    def municipalities_names(self) -> List[str]:
        return [muni.name for muni in self.municipalities]


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
    text: str
    html_el: str
    html_parents: str

    url: Optional[str] = None


class DataGeneric:
    """"""

    def extract_data(self,
                     url: str,
                     language_code: str,
                     filename_html: str = None,
                     filename_out: str = None
                     ) -> List[DataItem]:
        """

        Args:
            url: http...
            language_code: according to ISO 639-1
            filename_html:
                (Optional) Filename to save the HTML locally to.
                If nothing is provided, it will be saved in ./TMP dir.
            filename_out: To save output as json-line.
        Returns:

        """

        html = self._tmp_html(url, filename_html=filename_html)
        language = self._get_language_full_from_code(language_code)

        parser = GeneralHTMLParser2(html,
                                    language=language)

        l_data = []
        for paragraph in parser.get_paragraphs():
            if paragraph.is_boilerplate:
                # Skip boilerplate
                continue

            element_par = parser.get_lxml_element_from_paragraph(paragraph)

            label_names = self._get_label_names(paragraph)
            text = paragraph.text
            html_el = self._get_html_element(element_par)
            s_html_parents = self._make_html_including_parents(element_par)

            item = DataItem(label_names=label_names,
                            text=text,
                            html_el=html_el,
                            html_parents=s_html_parents,
                            url=url,
                            )

            l_data.append(item)

        if filename_out is None:
            filename_out = self._tmp_filename(url, ext=".jsonl", prefix="TITLE_")
            # filename_out = os.path.join(FOLDER_TMP, f"TITLE_{basename}.jsonl")

        export_jsonl(l_data, filename_out)

        return l_data

    def _get_language_full_from_code(self,
                                     language_code):

        language_full = langcodes.get(language_code).display_name()
        if language_full == "Norwegian":  # Default Norwegian (Spoken by ~90% of Norway)
            return "Norwegian_Bokmal"

        return language_full

    def _tmp_filename(self,
                      name,
                      ext="",
                      prefix="",
                      c_max=100) -> str:
        """

        Args:
            name:
            prefix:
            ext:
            c_max: To prevent too long filenames, the name will be hashed.

        Returns:

        """

        # Make valid by removing non-valid chars and replace with "_"
        re_pattern = re.compile(r"[^a-zA-Z0-9]+")
        basename = re_pattern.sub("_", name)

        if len(basename) > c_max:
            basename = f"{basename[:c_max]}_{hashlib.sha1(name.encode()).hexdigest()}"

        tmp_filename = os.path.join(FOLDER_TMP, f"{prefix}{basename}{ext}")

        return tmp_filename

    def _tmp_html(self, url, filename_html=None) -> str:

        if filename_html is None:
            filename_html = self._tmp_filename(url, ext=".html")

        try:
            html = get_html(filename_html)
        except FileNotFoundError:
            url2html(url, filename_html)
            html = get_html(filename_html)
        # except OSError as oserr:
        #     # Filename too long
        #     if oserr.errno == errno.ENAMETOOLONG:
        #
        #         basename = f"{basename[:50]}_{hashlib.sha1(basename.encode()).hexdigest()}"
        #         # Make a shorter filename
        #         FILENAME_INPUT_HTML = os.path.join(FOLDER_TMP, f"{basename}.html")
        #
        #         try:
        #             html = get_html(FILENAME_INPUT_HTML)
        #         except FileNotFoundError:
        #             url2html(url, FILENAME_INPUT_HTML)
        #             html = get_html(FILENAME_INPUT_HTML)
        #
        #     else:
        #         raise  # re-raise previously caught exception

        return html

    def _get_label_names(self,
                         paragraph: GeneralParagraph,
                         TITLE="title"):
        label_heading = paragraph.is_heading  # bool

        label_names = [TITLE] if label_heading else []

        return label_names

    def _get_html_element(self, element):
        html_el = lxml.html.tostring(element, encoding="UTF-8").decode("UTF-8")
        return html_el

    def _make_html_including_parents(self,
                                     node):
        """
        Add how much text context is given. e.g. 2 would mean 2 parent's text
        nodes are also displayed
        if questionContains is not None:
            newstr = doesThisElementContain(questionContains, lxml.html.tostring(node))
        else:
        """

        newstr = self._get_html_element(node)
        parent = node.getparent()
        while parent is not None:
            tag, items = parent.tag, parent.items()
            attrs = " ".join(['{}="{}"'.format(x[0], x[1]) for x in items if len(x) == 2])
            newstr = '<{} {}>{}</{}>'.format(tag, attrs, newstr, tag)
            parent = parent.getparent()
        return newstr


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

    pass


if __name__ == '__main__':
    data_extraction()
