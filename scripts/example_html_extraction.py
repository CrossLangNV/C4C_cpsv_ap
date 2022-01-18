import os.path

from data.html import FILENAME_HTML, get_html
from relation_extraction.methods import RelationExtractor


def main(filename: str,  # input filename html
         context: str,  # URL
         country_code: str,  # ISO 3166
         filename_rdf: str):  # output filename
    """
    (for DEMO)
    We want to extract relations from a webpage as found in the CPSV Application Profile.
    Starting from a html page, we chunk the different sections, such that we can classify relevant sections.
    We expect that the input HTML is a Public Service.

    The HTML page is first filtered to remove irrelevant content.
    In the next stage, different relation extraction methods (these can be either rule-based or ML/NLP based) are applied.
    To save the relations, they are put into an RDF.

    TODO
     * Start simple: Save the Public Service in CPSV-AP
     * Work in multiple languages
    """

    # Get the HTML page
    html = get_html(filename)

    # Apply relation extraction
    relation_extractor = RelationExtractor(html,
                                           context=context,
                                           country_code=country_code)

    relation_extractor.extract_all()

    # Save in RDF
    relation_extractor.export(filename_rdf)

    # Optional: Visualise results
    return


if __name__ == '__main__':
    # TODO convert to user-script
    main(filename=FILENAME_HTML,
         context="https://1819.brussels",
         country_code="BE",
         filename_rdf=os.path.join(os.path.dirname(__file__), 'example_html_extraction_cpsv-ap.rdf'))
