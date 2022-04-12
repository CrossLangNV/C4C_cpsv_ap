import argparse
import os.path
import warnings

from data.html import get_html
from relation_extraction.aalter import AalterParser
from relation_extraction.affligem import AffligemParser
from relation_extraction.austrheim import AustrheimParser
from relation_extraction.cities import CityParser
from relation_extraction.general_classifier import GeneralCityParser
from relation_extraction.nova_gorica import NovaGoricaParser
from relation_extraction.pipeline import RelationExtractor2
from relation_extraction.san_paolo import SanPaoloParser
from relation_extraction.wien import WienParser
from relation_extraction.zagreb import ZagrebParser


def get_parser():
    parser = argparse.ArgumentParser(prog="extract_cpsv_ap",
                                     description='Extract the administrative procedure ontology out of a html page,'
                                                 ' as defined by the CPSV-AP vocabulary.')

    # Add the arguments
    parser.add_argument('path',
                        metavar='path',
                        type=str,
                        help='input filename to read the HTML')

    parser.add_argument('-o',
                        '--output',
                        metavar='filename',
                        type=str,
                        help='filename to export as RDF',
                        default=None,
                        required=True)

    parser.add_argument("-m",
                        "--municipality",
                        metavar='URL',
                        help="URL of home website",
                        required=True
                        )

    parser.add_argument("-u",
                        "--url",
                        help="URL of the specific page",
                        )

    parser.add_argument("-c",
                        "--country",
                        metavar='code',
                        help="Country code (e.g. FR, BE, DE, IT, BE...)",
                        required=True)

    parser.add_argument("-t",
                        "--terms",
                        action="store_true",
                        default=False,
                        help='flag to extract Concepts',
                        )

    parser.add_argument("-g",
                        "--general",
                        action="store_true",
                        default=False,
                        help="flag to use general relation-extractor",
                        )

    parser.add_argument("-l",
                        "--language",
                        metavar="code",
                        help="Language code (e.g. FR, NL, DE, IT, EN...)",
                        required=True)

    return parser


def extract_cpsv_ap_from_html(filename_html,
                              filename_rdf,
                              context,
                              country_code: str,
                              lang,  # Only needed when using general
                              url: str = None,
                              extract_concepts: bool = False,
                              general: bool = False,
                              filename_html_parsing: str = None
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

    if not os.path.exists(filename_html):
        warnings.warn(f"Could not find {filename_html}", UserWarning)

    # Get the HTML page
    try:
        html = get_html(filename_html)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Could not find HTML file: {filename_html}") from e

    if general:
        city_parser = GeneralCityParser(lang_code=lang)
    else:
        city_parser = get_municipality_parser(country_code=country_code,
                                              url=url)

    relation_extractor = RelationExtractor2(html,
                                            parser=city_parser,
                                            url=url,
                                            context=context,
                                            country_code=country_code,
                                            lang_code=lang
                                            )

    relation_extractor.extract_all(extract_concepts=extract_concepts,
                                   verbose=2)

    print("Success")

    # -- Save to RDF --
    # TODO check if already exists, else, ask for confirmation?
    if filename_rdf:
        print(f"Saving to: {filename_rdf}")
        relation_extractor.export(filename_rdf)

    return 0


def main(args: argparse.Namespace):
    """Run the script from args"""
    return extract_cpsv_ap_from_html(filename_html=args.path,
                                     filename_rdf=args.output,
                                     extract_concepts=args.terms,
                                     context=args.municipality,
                                     country_code=args.country,
                                     url=args.url,
                                     general=args.general,
                                     lang=args.language
                                     )


def get_municipality_parser(country_code: str = "",
                            url: str = ""
                            ) -> CityParser:
    if "AT" == country_code.upper():
        return WienParser()
    elif "BE" == country_code.upper():
        if "aalter" in url.lower():
            return AalterParser()
    elif "IT" == country_code.upper():
        return SanPaoloParser()
    elif "HR" == country_code.upper():
        return ZagrebParser()
    elif "NO" == country_code.upper():
        return AustrheimParser()
    elif country_code.upper() in ["SL", "SI"]:
        return NovaGoricaParser()

    # Backup: Affligem parser
    return AffligemParser()


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    main(args)
