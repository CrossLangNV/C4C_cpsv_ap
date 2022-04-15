import json
import os
import warnings

from rdflib import RDF

from c4c_cpsv_ap.connector.hierarchy import CPSV_APGraph
from context_broker.script_upload import ItemContextBroker, OrionConnector

# Fix for stupid bug....
RDF._fail = False
RDF._warn = False

URL_ORION = os.environ.get("URL_ORION")
if URL_ORION is None:
    warnings.warn("Can't find environment variable 'URL_ORION'.")

AT_ID = "@id"
AT_GRAPH = "@graph"


def get_jsonld(filename) -> dict:
    """
    Get an RDF file as JSON-LD

    Args:
        filename: to the RDF

    Returns:
        JSON-LD as dictionary
    """
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
    n_already_in = 0

    for graph in jsonld:

        for item in graph[AT_GRAPH]:

            # if debug:
            #     print(json.dumps(item))

            item_clean = ItemContextBroker.from_RDF(item)

            r = conn.add_item(item_clean)

            if r.ok:
                n_ok += 1

            else:
                if r.status_code == 409:  # Already exists
                    n_already_in += 1

                else:  # Fail
                    n_not_ok += 1

                    if debug:
                        print(item_clean)

                        try:
                            s = r.json()
                        except:
                            s = r.text
                            warnings.warn(s, UserWarning)
                        else:
                            print(s)

    print(f'# alr in: {n_already_in}\n'
          f'    # ok: {n_ok}\n'
          f'# not ok: {n_not_ok}')

    return
