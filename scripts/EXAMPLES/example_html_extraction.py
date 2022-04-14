import os.path
import tempfile
from urllib.request import urlopen

from connectors.elastic_search import ElasticSearchConnector
from data.html import FILENAME_HTML, get_html
from relation_extraction.methods import RelationExtractor


def main(filename: str,  # input filename html
         context: str,  # URL
         country_code: str,  # ISO 3166
         filename_rdf: str,
         extract_concepts=True):  # output filename
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

    relation_extractor.extract_all(extract_concepts=extract_concepts)

    # Save in RDF
    relation_extractor.export(filename_rdf)

    # Optional: Visualise results
    return


if __name__ == '__main__':
    # TODO convert to user-script

    case = 2
    if case == 1:
        es_conn = ElasticSearchConnector()
        html = es_conn.get_random_html(lang="en")

        # Get from elasticsearch, problem is that these are all identified as English.
        with tempfile.TemporaryDirectory() as d:
            FILENAME_TMP = os.path.join(d, "test.html")

            with open(FILENAME_TMP, "w") as f:
                f.write(html)

            main(filename=FILENAME_TMP,
                 context="https://1819.brussels",
                 country_code="BE",
                 filename_rdf=os.path.join(os.path.dirname(__file__), 'example_html_extraction_cpsv-ap.rdf'),
                 extract_concepts=False)

    elif case == 2:
        url = "https://diplomatie.belgium.be/en/about_the_organisation/contact/getting_there_opening_hours"
        html = urlopen(url).read().decode()

        with tempfile.TemporaryDirectory() as d:
            FILENAME_TMP = os.path.join(d, "test.html")

            with open(FILENAME_TMP, "w") as f:
                f.write(html)

            main(filename=FILENAME_TMP,
                 context="https://1819.brussels",
                 country_code="BE",
                 filename_rdf=os.path.join(os.path.dirname(__file__), 'example_html_extraction_cpsv-ap.rdf'),
                 extract_concepts=False)

    else:
        main(filename=FILENAME_HTML,
             context="https://1819.brussels",
             country_code="BE",
             filename_rdf=os.path.join(os.path.dirname(__file__), 'example_html_extraction_cpsv-ap.rdf'),
             extract_concepts=False)
