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
    parser.add_argument('Path',
                        metavar='path',
                        type=str,
                        help='input filename to read the HTML')
    parser.add_argument('RDF',
                        metavar='RDF',
                        type=str,
                        help='output filename to export the RDF')
    parser.add_argument("-c",
                        "--concepts",
                        action="store_true",
                        default=False,
                        help='flag to extract Concepts',
                        )

    return parser


def main(filename_html,
         filename_rdf,
         context="affligem.be",
         url: str = "https://www.affligem.be/Affligem/Nederlands/Leven/identiteitsbewijzen,-rijbewijzen-en-afschriften/afschriften-uittreksels-getuigschriften/wettiging-van-handtekening/page.aspx/169#",
         # TODO original webpage URL"
         country_code="BE",  # TODO
         extract_concepts: bool = False,
         general: bool = True,
         ):
    """
    Extract the administrative procedure ontology out of a html page,
    as defined by the CPSV-AP vocabulary.

    Input
        - HTML
        - general:
            flag whether to use the general classifier.
    Output
        - RDF (based on CPSV-AP)

    Returns:

    """

    if not os.path.exists(filename_html):
        warnings.warn(f"Could not find {filename_html}", UserWarning)

    # Get the HTML page
    try:
        html = get_html(filename_html)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Could not find HTML file: {filename_html}") from e

    if general:
        city_parser = GeneralCityParser()
    else:
        city_parser = get_municipality_parser(country_code=country_code,
                                              url=url)

    relation_extractor = RelationExtractor2(html,
                                            parser=city_parser,
                                            url=url,
                                            context=context,
                                            country_code=country_code,
                                            )

    relation_extractor.extract_all(extract_concepts=extract_concepts)

    # -- Save to RDF --
    # TODO check if already exists, else, ask for confirmation?
    relation_extractor.export(filename_rdf)

    return


# TODO use general parser or be able specify a parser by name instead of rule-based selection.
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

    main(filename_html=args.Path,
         filename_rdf=args.RDF,
         extract_concepts=args.Concepts)
