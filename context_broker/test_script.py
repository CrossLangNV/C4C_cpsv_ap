import json
import os

import requests

URL_POST_ITEM = "http://localhost:1026/ngsi-ld/v1/entities"

URL_V2 = "http://localhost:1026/v2/entities/"
EXAMPLE_ID = "Conceptbc83bfd3ad9b4690bbb1d3913420d320"
C4C = "c4c"
C4C_URL = "http://cefat4cities.crosslang.com/content/"
SKOS = "skos"
SKOS_URL = "http://www.w3.org/2004/02/skos/core#"

NAMESPACES = {C4C: C4C_URL,
              SKOS: SKOS_URL}

ID = f"{C4C}:{EXAMPLE_ID}"

HEADERS = {"Content-Type": "application/ld+json"}


def post_example():
    headers = {"Content-Type": "application/ld+json"}

    json_post = {
        "@id": ID,
        "@type": f"{SKOS}:Concept",
        "skos:prefLabel": [
            {
                "type": "Property",
                "value": "Finanzielles"
            }
        ],
        "@context": {
            f"{C4C}": C4C_URL,
            f"{SKOS}": SKOS_URL
        }
    }

    r = requests.post(URL_POST_ITEM,
                      headers=headers,
                      json=json_post)
    return r


def delete_example():
    r = requests.delete(os.path.join(URL_V2, ID))

    return r


def parse_json_ld(filename):
    with open(filename) as f:
        j = json.load(f)

    n_ok = 0
    n_not_ok = 0

    for graph in j:
        graph["@id"]
        graph["@graph"]

        for item in graph["@graph"]:

            context = {}

            def replace_namespace(s: str):

                s_replace = s
                for ns_short, ns_url in NAMESPACES.items():
                    if ns_url in s_replace:  # We can shorten it

                        context[ns_short] = ns_url

                        s_replace = s_replace.replace(ns_url, ns_short + ":")

                return s_replace

            # clean up dict
            item_clean = {}
            for key, value in item.items():

                if key == '@type':
                    # List with single item.
                    if isinstance(value, list) and len(value) == 1:
                        value = value[0]

                # Clean the value
                if isinstance(value, str):  # e.g. key == "@id"
                    value_clean = replace_namespace(value)

                elif isinstance(value, list):
                    value_clean = list(map(replace_namespace, value))

                    def add_type(d):

                        return

                    value_clean2 = []
                    for sub in value_clean:

                        if isinstance(sub, dict):
                            sub2 = {}
                            for k, v in sub.items():
                                sub2[k.replace('@', '')] = v

                            if "value" in sub2:
                                # Add type
                                sub2["type"] = "Property"
                            else:
                                sub2 = sub

                        value_clean2.append(sub2)

                    value_clean = value_clean2


                else:
                    value_clean = value

                # Clean the key
                key_clean = replace_namespace(key)

                # Update dict
                item_clean[key_clean] = value_clean

            item_clean["@context"] = context

            r = requests.post(URL_POST_ITEM,
                              headers=HEADERS,
                              json=item_clean)

            if not r.ok:
                print(r.content)

                n_not_ok += 1
            else:
                n_ok += 1

    print(f'    # ok: {n_ok}\n'
          f'# not ok: {n_not_ok}\n')

    return


def main():
    parse_json_ld(os.path.join(os.path.dirname(__file__), 'examples/demo_context_broker.jsonld'))

    r = post_example()
    r.status_code
    r.content
    r.json()

    r = delete_example()
    r.status_code
    r.content
    r.json()

    print('Script has finished.')


if __name__ == '__main__':
    main()
