import argparse
import enum
import os
import re
from typing import List, Optional, Union

import yaml
from pydantic import BaseModel

from c4c_cpsv_ap.models import PublicService
from data.html import get_html, url2html
from relation_extraction.cities import ClassifierCityParser, RegexCPSVAPRelationsClassifier
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser, GeneralSection
from relation_extraction.html_parsing.justext_wrapper import BoldJustextWrapper
from relation_extraction.html_parsing.utils import _tmp_filename
from relation_extraction.pipeline import RelationExtractor2
from scripts.extract_cpsv_ap import get_parser


class Label(enum.Enum):
    title = "title"
    description = "Description"
    rule = "rule"
    evidence = "evidence"
    cost = "cost"
    criterion_requirement = "criterion_requirement"
    contact_info = "contact_info"


class SectionV3(BaseModel):
    title: str
    # paragraphs: List[str] # Not yet used.

    heading_level: Optional[int] = None
    label: Optional[str] = None
    path: str  # Xpath path of the section


def Berlare_rule_based_summary(url: str,
                               lang_code="NL",
                               ) -> List[SectionV3]:
    # Check if the html is already in the cache. Else, download it.

    FILENAME_HTML_TMP = _tmp_filename(url, ext=".html")
    if not os.path.exists(FILENAME_HTML_TMP):
        url2html(url, FILENAME_HTML_TMP)

    html = get_html(FILENAME_HTML_TMP)

    # Section extraction
    justext_wrapper_class = BoldJustextWrapper
    html_parser = GeneralHTMLParser(html,
                                    language=lang_code,
                                    justext_wrapper_class=justext_wrapper_class
                                    )
    sections = html_parser.get_sections()

    # Rule-based extraction

    l = []

    for section in sections:

        # find the paragraph that matches the section:
        # 1. find the paragraph that matches the section

        def _get_paragraph_that_matches_section(section: GeneralSection,
                                                ):
            """
            Get the paragraph that matches the section title.
            Args:
                section:

            Returns:
            """
            for paragraph in html_parser.get_paragraphs():
                if section.title in paragraph.text:
                    return paragraph
            return None

        paragraph_that_matches_section = _get_paragraph_that_matches_section(section)
        if paragraph_that_matches_section is None:
            continue  # Else errors will occur.

        el_path = paragraph_that_matches_section.xpath

        # Determine the label
        if section.level == 1:
            label = "title"
        elif section.title == "Wat?":
            label = Label.description.name
        elif section.title == "Hoe aanvragen?":
            label = Label.rule.name
        elif section.title == "Wat breng je mee?":
            label = Label.evidence.name
        elif section.title == "Contact":
            label = Label.contact_info.name
        elif section.title == "Kostprijs":
            label = Label.cost.name
        else:
            # TODO: Determine the label
            label = None

        # TODO get DOM/xpath from the section.
        section_v3 = SectionV3(title=section.title,
                               heading_level=section.level,
                               label=label,
                               path=el_path)

        l.append(section_v3)

    return l


def Berlare_rule_based_extraction(url: str,
                                  lang_code="NL",
                                  clean=True,
                                  ):
    """

    Returns:

    TODO
     * Put into config
    """

    FILENAME_HTML_TMP = _tmp_filename(url, ext=".html")
    if not os.path.exists(FILENAME_HTML_TMP):
        url2html(url, FILENAME_HTML_TMP)

    html = get_html(FILENAME_HTML_TMP)

    # Rule based extraction
    """
    Example paths: -------------------------------------------------------|-------
    /html[1]/body[1]/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/h2[1]
    /html[1]/body[1]/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/h2[1]
    """
    xpath_sections = "/html[1]/body[1]/div[4]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div/h2[1]"

    # Get DOM and apply xpath

    justext_wrapper_class = BoldJustextWrapper
    html_parser = GeneralHTMLParser(html,
                                    language=lang_code,
                                    justext_wrapper_class=justext_wrapper_class
                                    )
    dom = html_parser.dom

    l_section_headings = dom.xpath(xpath_sections)

    roottree = dom.getroottree()

    # Get common parent of all headings
    common_parent_path = None

    for el in l_section_headings:
        path_i = roottree.getpath(el)

        if common_parent_path is None:
            common_parent_path = path_i

        else:
            l_sub = []
            for common_sub, path_i_sub in zip(common_parent_path.split('/'), path_i.split('/')):
                if common_sub != path_i_sub:
                    break
                else:
                    l_sub.append(common_sub)

            common_parent_path = '/'.join(l_sub)

    print(common_parent_path)

    common_parent = dom.xpath(common_parent_path)[0]

    l_desc = list(common_parent.iterdescendants())

    prev_section = None
    l_sections = []

    def get_paragraph_from_el(el_desc):
        path_el_desc = roottree.getpath(el_desc)

        # Iterate over paragraphs to find the matching one.
        for paragraph in html_parser.get_paragraphs():

            el_par = roottree.xpath(paragraph.xpath)[0]
            # necessary to get same standard.
            path_par = roottree.getpath(el_par)

            if path_par == path_el_desc:
                return paragraph

        return None

    for el_desc in l_desc:

        paragraph = get_paragraph_from_el(el_desc)

        # If paragraph is found, it means no matching text is found.
        if paragraph is None:
            continue

        text = paragraph.text

        # Cleaned text: strip empty spaces and join newlines
        if clean:
            text = ' '.join(filter(str, map(str.strip, text.splitlines())))

        # Heading if heading or normal paragraph
        if el_desc in l_section_headings:

            if prev_section is not None:
                l_sections.append(prev_section)

            # Try to get the level of the heading
            try:
                # Get the last part of the path
                el_x = el_desc.dom_path.rsplit(".", 1)[-1]
                level = int(re.findall(r"h(\d)", el_x)[0])
            except:
                level = None

            # Make a new section.
            prev_section = GeneralSection(title=text,
                                          paragraphs=[],
                                          level=level)

        else:
            # regular text

            # Check for section without a title (e.g. introduction)
            if prev_section is None:
                prev_section = GeneralSection(title="",
                                              paragraphs=[])

            prev_section.add_paragraph(text)

    if prev_section is not None:
        if (l_sections == []) or (prev_section != l_sections[-1]):
            l_sections.append(prev_section)

    return l_sections


def get_config(config_file) -> dict:
    """
    Get the config for the extraction from YAML
    includes classification configs
    """

    with open(config_file, "r") as f:
        dict_tmp = yaml.full_load(f)

    return dict_tmp


class RelationExtractor3(RelationExtractor2):
    """
    Version 3 of the relation extractor.
    """

    def extract_all(self, *args, verbose=0, **kwargs, ) -> PublicService:
        # TODO update/improve

        return super(RelationExtractor3, self).extract_all()


def extract_cpsv_ap_from_html_v3(html: str,
                                 filename_rdf,
                                 context,
                                 country_code: str,
                                 lang: str,  # Only needed when using general
                                 url: str = None,
                                 extract_concepts: bool = False,
                                 filename_html_parsing: str = None,
                                 translation: Union[str, List[str]] = "EN"
                                 ):
    """
    Extract the administrative procedure ontology out of a html page,
    as defined by the CPSV-AP vocabulary.

    Input
        - filename_html: Filename of the HTML
        - context: URL of the homepage of the municipality
        - general (optional):
            flag whether to use the general classifier.
        - filename_html_parsing (optional):
            filename to save intermediate HTML parsing to. Marks detected headings and boilerplate text.

    Output
        - RDF (based on CPSV-AP) saved to *filename_rdf*

    Returns:
        0 if successful
    """

    # Cleaning input
    if lang is not None:
        lang = lang.upper()

    if translation is not None:
        if isinstance(translation, str):
            translation = translation.upper()
        else:
            translation = [l_i.upper() for l_i in translation]

    def get_parser(context: str):

        # Get config from YAML
        if "berlare" in context.lower():
            config_file = os.path.join(os.path.dirname(__file__),
                                       "config/config_berlare.yml")

            config = get_config(config_file)

            pattern_rule = config["classifiers"]["rule"]["rules"]["section.title"]
            pattern_evidence = config["classifiers"]["evidence"]["rules"]["section.title"]
            pattern_cost = config["classifiers"]["cost"]["rules"]["section.title"]

            classifier = RegexCPSVAPRelationsClassifier(pattern_criterion_requirement='',
                                                        # no pattern for criterion requirement
                                                        pattern_rule=pattern_rule,
                                                        pattern_evidence=pattern_evidence,  # with or without ?
                                                        pattern_cost=pattern_cost, )
            city_parser = ClassifierCityParser(classifier)

            return city_parser

        else:
            # TODO use general config
            return

    parser = get_parser(context)

    relation_extractor = RelationExtractor2(html,
                                            parser=parser,
                                            url=url,
                                            context=context,
                                            country_code=country_code,
                                            lang_code=lang
                                            )

    relation_extractor.extract_all(extract_concepts=extract_concepts,
                                   verbose=2)

    relation_extractor.translate(translation, source=lang)

    print("Success")

    # -- Save to RDF --
    # TODO check if already exists, else, ask for confirmation?
    if filename_rdf:
        print(f"Saving to: {filename_rdf}")
        relation_extractor.export(filename_rdf)

    return 0


def main(args: argparse.Namespace):
    """Run the script from args"""

    # Get the HTML page
    filename_html = args.filename_html
    try:
        html = get_html(filename_html)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Could not find HTML file: {filename_html}") from e

    return extract_cpsv_ap_from_html_v3(html=html,
                                        filename_rdf=args.output,
                                        extract_concepts=args.terms,
                                        context=args.municipality,
                                        country_code=args.country,
                                        url=args.url,
                                        lang=args.language,
                                        translation=args.translate,
                                        filename_html_parsing=args.html_parsing
                                        )


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    main(args)
