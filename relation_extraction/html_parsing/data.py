import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

import lxml
import yaml
from pydantic import BaseModel, validator

from relation_extraction.html_parsing.general_parser import GeneralHTMLParser
from relation_extraction.html_parsing.justext_wrapper import BoldJustextWrapper, GeneralParagraph, JustextWrapper
from relation_extraction.html_parsing.utils import _get_language_full_from_code, _tmp_filename, _tmp_html, export_jsonl


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

    def get_justext_wrapper(self):

        if isinstance(self.titles, list):
            # Let html_bold take priority
            if self.titlesChoices.html_bold in self.titles:
                return BoldJustextWrapper()

        if self.titles == self.titlesChoices.html_bold:
            return BoldJustextWrapper()

        # Default behaviour
        return JustextWrapper()


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

    def __init__(self, parser_config: ParserModel = None):

        if parser_config is None:
            # Default .
            parser_config = ParserModel(titles=ParserModel.titlesChoices.html_headings)

        self._justext_wrapper = parser_config.get_justext_wrapper()

    @property
    def justext_wrapper(self) -> JustextWrapper:
        return self._justext_wrapper

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

        html = _tmp_html(url, filename_html=filename_html)
        language = _get_language_full_from_code(language_code)

        parser = GeneralHTMLParser(html,
                                   language,
                                   self.justext_wrapper,
                                   )

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
            filename_out = _tmp_filename(url, ext=".jsonl", prefix="TITLE_")
            # filename_out = os.path.join(FOLDER_TMP, f"TITLE_{basename}.jsonl")

        export_jsonl(l_data, filename_out)

        return l_data

    def _get_label_names(self,
                         paragraph: GeneralParagraph,
                         TITLE="title"):

        label_names = [TITLE] if paragraph.is_heading else []

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
