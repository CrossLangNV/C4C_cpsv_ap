import os.path
import unittest
import warnings

from rdflib import RDF

from context_broker.context_broker_connector import get_jsonld, upload_jsonld_to_orion
from scripts.upload_context_broker import upload_rdf_to_context_broker

RDF._fail = False
RDF._warn = False

DIR_SRC = os.path.join(os.path.dirname(__file__), "../..")
FILENAME_JSONLD = os.path.join(DIR_SRC, "context_broker/examples/demo_context_broker.jsonld")

FILENAME_RDF = os.path.join(DIR_SRC, "scripts/EXAMPLES/DEMO_GEN_CHUNKER.rdf")
if not os.path.exists(FILENAME_RDF):
    warnings.warn(f"Could not find {FILENAME_RDF}. Make sure path is correct.")

URL_ORION = os.environ["URL_ORION"]



class TestFoo(unittest.TestCase):
    def test_bar(self):
        # Open RDF
        jsonld = get_jsonld(filename=FILENAME_RDF)

        # Go over triples
        # push to Context Broker
        upload_jsonld_to_orion(jsonld)

        return

    def test_cli(self):
        upload_rdf_to_context_broker(FILENAME_RDF)
