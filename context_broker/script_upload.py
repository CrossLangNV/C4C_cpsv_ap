import json
import os
import warnings

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
                      headers=HEADERS,
                      json=json_post)
    return r


def delete_example():
    r = requests.delete(os.path.join(URL_V2, ID))

    return r


class Connector:
    def __init__(self):
        pass


class Item(dict):

    def __str__(self):
        return json.dumps(self)


class ItemContextBroker(Item):
    context: dict = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context = self["@context"] = {}

    @classmethod
    def from_RDF(cls, d_rdf: dict):

        cb = cls()

        context = {}

        # clean up dict
        for key, value in d_rdf.items():

            def clean_value(key, value):

                if key == '@type':
                    # TODO Context Broker should allow multiple types
                    if isinstance(value, list):  # and len(value) == 1:
                        value_clean = value[0]
                    else:
                        value_clean = value
                else:
                    # TODO
                    value_clean = value

                del value  # Makes sure we use the correct variable

                # Clean the value
                if isinstance(value_clean, str):  # e.g. key == "@id"
                    value_clean = cb._replace_namespace(value_clean)

                elif isinstance(value_clean, list):

                    def update_d_value(d: dict):

                        d_ = {}
                        for k, v in d.items():
                            if not v:
                                # TODO remove
                                d_rdf
                                value_clean
                                v
                            d_[k.replace('@', '')] = cb._replace_namespace(v) if isinstance(v, str) else v

                        VALUE = "value"
                        if VALUE in d_:
                            v_value = d_[VALUE]
                            # Add type
                            if isinstance(v_value, int):  # If integer, try to add type Integer
                                v_type = "Integer"
                            else:
                                v_type = "Property"

                            d_["type"] = v_type

                        elif "id" in d_:

                            d_["object"] = d_.pop("id")
                            d_["type"] = "Relationship"

                        else:
                            warnings.warn(f"Unexpected items: {d_}", UserWarning)

                        return d_

                    def process_l(l: list):
                        l_ = []

                        for a in l:

                            if isinstance(a, str):
                                a_ = cb._replace_namespace(a)
                            elif isinstance(a, dict):
                                a_ = update_d_value(a)
                            else:
                                warnings.warn(f"Unexpected type: {a}", UserWarning)
                                a_ = a

                            l_.append(a_)

                        return l_

                    value_clean = process_l(value_clean)

                return value_clean

            def clean_key(key, value=None):

                # Clean the key
                key_clean = cb._replace_namespace(key)

                return key_clean

            value_clean = clean_value(key, value)
            key_clean = clean_key(key, value)

            # Update dict
            cb[key_clean] = value_clean

        cb.context = context

        return cb

    def get_context(self):
        return self.context

    def _replace_namespace(self, s: str):

        assert isinstance(s, str), s

        s_replace = s
        for ns_short, ns_url in NAMESPACES.items():
            if ns_url in s_replace:  # We can shorten it

                self.context[ns_short] = ns_url

                s_replace = s_replace.replace(ns_url, ns_short + ":")

        return s_replace


class ItemRDF(Item):
    @classmethod
    def from_context_broker(cls, d_cb: dict):
        return cls()


def parse_json_ld(filename, debug=False):
    with open(filename) as f:
        j = json.load(f)

    n_ok = 0
    n_not_ok = 0

    for graph in j:
        graph["@id"]
        graph["@graph"]

        for item in graph["@graph"]:

            if debug:
                print(json.dumps(item))

            item_clean = ItemContextBroker.from_RDF(item)

            r = requests.post(URL_POST_ITEM,
                              headers=HEADERS,
                              json=item_clean)

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


def delete_all(debug=False):
    # Get all links
    r = requests.get(URL_V2,
                     params={
                         "options": "count",
                         "limit": "1"}
                     )
    n_count = int(r.headers['Fiware-Total-Count'])

    n_ok = 0
    n_not_ok = 0

    limit = 10  # 100
    for offset in range(0, n_count, limit):
        r = requests.get(URL_V2,
                         params={
                             "limit": str(limit),
                             "offset": str(offset)
                         }
                         )

        json_all = r.json()

        l_id = [d["id"] for d in json_all]

        # Delete every link
        for s_id in l_id:
            r = requests.delete(URL_V2 + s_id)

            if not r.ok:
                if debug:
                    warnings.warn("Something went wrong.")
                n_not_ok += 1
            else:
                n_ok += 1

    print(f'    # ok: {n_ok}\n'
          f'# not ok: {n_not_ok}\n')

    return


def main_example():
    delete_all()  # Clean slate.

    parse_json_ld(os.path.join(os.path.dirname(__file__), 'examples/demo_context_broker.jsonld'))

    r = post_example()
    try:
        print(r.status_code)
        print(r.content)
        print(r.json())
    except:
        pass

    r = delete_example()
    try:
        print(r.status_code)
        print(r.content)
        print(r.json())
    except:
        pass

    print('Script has finished.')


if __name__ == '__main__':
    main_example()
