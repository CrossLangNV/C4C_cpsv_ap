import argparse
import os.path
import warnings

from data.html import get_html
from relation_extraction.affligem import AffligemParser
from relation_extraction.pipeline import RelationExtractor2


def get_parser():
    parser = argparse.ArgumentParser(description='Extract the administrative procedure ontology out of a html page,'
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
         context="affligem.be",  # TODO
         country_code="BE",  # TODO
         extract_concepts: bool = False
         ):
    """
    Extract the administrative procedure ontology out of a html page,
    as defined by the CPSV-AP vocabulary.

    Input
        - HTML
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

    # TODO use general parser or be able specify a parser by name.
    parser = AffligemParser()

    relation_extractor = RelationExtractor2(html,
                                            context=context,
                                            country_code=country_code,
                                            parser=parser)

    relation_extractor.extract_all(extract_concepts=extract_concepts)

    # -- Save to RDF --
    # TODO check if already exists, else, ask for confirmation?
    relation_extractor.export(filename_rdf)

    return


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    main(filename_html=args.Path,
         filename_rdf=args.RDF,
         extract_concepts=args.Concepts)
