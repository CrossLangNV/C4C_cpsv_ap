from relation_extraction.methods import RelationExtractor
from tests.relation_extraction.test_methods import FILENAME_HTML, get_html


def main(filename=FILENAME_HTML,
         context="https://1819.brussels"):
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
    relation_extractor = RelationExtractor(html, context=context)

    relation_extractor.extract_public_service()

    # Save in RDF
    relation_extractor.export()

    # Optional: Visualise results
    return

if __name__ == '__main__':
    main()
