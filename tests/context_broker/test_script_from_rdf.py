import json
import os.path
import unittest
import warnings

from rdflib import RDF

from c4c_cpsv_ap.connector.hierarchy import CPSV_APGraph
# Fix for stupid bug....
from context_broker.script_upload import ItemContextBroker, OrionConnector

RDF._fail = False
RDF._warn = False

DIR_SRC = os.path.join(os.path.dirname(__file__), "../..")
FILENAME_JSONLD = os.path.join(DIR_SRC, "context_broker/examples/demo_context_broker.jsonld")

FILENAME_RDF = os.path.join(DIR_SRC, "scripts/EXAMPLES/DEMO_GEN_CHUNKER.rdf")
if not os.path.exists(FILENAME_RDF):
    warnings.warn(f"Could not find {FILENAME_RDF}. Make sure path is correct.")

URL_ORION = os.environ["URL_ORION"]


def get_jsonld(filename) -> dict:
    g = CPSV_APGraph()
    g.parse(filename)

    foobar = g.serialize(format="json-ld", indent=2)

    j = json.loads(foobar)

    return j


def upload_jsonld_to_orion(jsonld: dict,
                           debug=False
                           ):
    conn = OrionConnector(URL_ORION)

    n_ok = 0
    n_not_ok = 0

    for graph in jsonld:
        graph["@id"]
        graph["@graph"]

        for item in graph["@graph"]:

            # if debug:
            #     print(json.dumps(item))

            item_clean = ItemContextBroker.from_RDF(item)

            r = conn.add_item(item_clean)

            if not r.ok:
                # print(r.content)
                if debug:
                    print(item_clean)

                    try:
                        s = r.json()
                    except:
                        pass
                    else:
                        s = r.content

                    warnings.warn(s)

                n_not_ok += 1
            else:
                n_ok += 1

    print(f'    # ok: {n_ok}\n'
          f'# not ok: {n_not_ok}\n')

    return


class TestFoo(unittest.TestCase):
    def test_bar(self):
        # Open RDF
        jsonld = get_jsonld(filename=FILENAME_RDF)

        # Go over triples
        # push to Context Broker
        upload_jsonld_to_orion(jsonld)

        return
