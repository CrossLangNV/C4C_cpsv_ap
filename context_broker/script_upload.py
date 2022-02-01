import json
import os
import urllib
import warnings

import requests
from pydantic import BaseModel

URL_ORION = os.environ["URL_ORION"]
URL_V1 = URL_ORION + "/ngsi-ld/v1/entities/"
URL_V2 = URL_ORION + "/v2/entities/"
EXAMPLE_ID = "Conceptbc83bfd3ad9b4690bbb1d3913420d320"
C4C = "c4c"
C4C_URL = "http://cefat4cities.crosslang.com/content/"
SKOS = "skos"
SKOS_URL = "http://www.w3.org/2004/02/skos/core#"

PROPERTY = "Property"
AT_VALUE = "@value"
AT_ID = "@id"
AT_LANG = "@language"


class OrionConnector:
    """
    Connector to FIWARE Orion
    """
    PATH_V2 = "/v2/entities/"

    def __init__(self, url):
        self.url = url

        response = requests.get(url + "/v2")
        if not response.ok:
            warnings.warn(f"Could not connect to {url}", UserWarning)

    def count_entities(self) -> int:
        """ Counts the number of entities in Orion.

        Returns:

        """

        class Params(BaseModel):
            options: str
            limit: str

        params = Params(options="count",
                        limit="1")

        r = requests.get(self.url + self.PATH_V2,
                         params=params.dict()
                         )
        n_count = int(r.headers['Fiware-Total-Count'])
        return n_count


NAMESPACES = {C4C: C4C_URL,
              SKOS: SKOS_URL,
              "sioc": "http://rdfs.org/sioc/ns#",
              "rdf": "http://www.w3.org/2000/01/rdf-schema#",
              "cpsv": "http://purl.org/vocab/cpsv#",
              "locn": "http://www.w3.org/ns/locn#",
              "dcat": "http://www.w3.org/ns/dcat#"}

ID = f"{C4C}:{EXAMPLE_ID}"

HEADERS = {"Content-Type": "application/ld+json"}


def post_example():
    json_post = {
        "@id": ID,
        "@type": f"{SKOS}:Concept",
        "skos:prefLabel": [
            {
                "type": PROPERTY,
                "value": "Finanzielles"
            }
        ],
        "@context": {
            f"{C4C}": C4C_URL,
            f"{SKOS}": SKOS_URL
        }
    }

    r = requests.post(URL_V1,
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
    """
    TODO:
     * Multiple types
    """
    context: dict = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context = self["@context"] = {}

    @classmethod
    def from_RDF(cls, d_rdf: dict,
                 ignore: bool = True):
        """

        Args:
            d_rdf:
            ignore: Flag to ignore properties unknown by NGSI. E.g. language.

        Returns:

        """

        cb = cls()

        context = {}

        def clean(a):

            if isinstance(a, str):
                pass

            elif isinstance(a, dict):

                d_ = {}

                for k, v in a.items():
                    if AT_VALUE == k:
                        if isinstance(v, int):  # If integer, try to add type Integer
                            v_type = PROPERTY  # "Integer" # does not seem to be working
                        else:
                            v_type = PROPERTY
                        d_["value"] = v
                        d_["type"] = v_type
                    elif AT_ID == k:

                        d_["object"] = list(map(cb._replace_namespace, v)) if isinstance(v, list) else \
                            cb._replace_namespace(v)
                        d_["type"] = "Relationship"
                    elif AT_LANG == k:
                        """
                        Suggestion from Fernando Lopez
                        
                        * ETSI CIM NGSI-LD LanguageProperty
                        'label': {
                            'type': 'LanguageProperty',
                            'LanguageMap': {
                                'en': 'a sentence',
                                'fr': 'une phrase'
                            }
                        }
                        * Workaround
                        'label': {
                            'type': 'Property',
                            'value': {
                                'en': 'a sentence',
                                'fr': 'une phrase'
                            }
                        }
                        
                        """
                        # TODO test

                        if 0:
                            # ETSI CIM NGSI-LD LanguageProperty
                            # TODO This specification is still not implemented in the Context Broker
                            d__ = {
                                "type": "LanguageProperty",
                                "LanguagMap": {
                                    a[AT_LANG]: a[AT_VALUE]
                                }
                            }
                            return d__

                        else:
                            d__ = {
                                "type": "Property",
                                "value": {
                                    a[AT_LANG]: a[AT_VALUE]
                                }
                            }
                            return d__

                    else:
                        if ignore:
                            pass  # TODO implement
                        else:
                            d_[k.replace('@', '')] = clean(v)

                return d_

            elif isinstance(a, list):

                if len(a) == 1:
                    return clean(a[0])
                else:
                    # Join
                    a0 = a[0]
                    if isinstance(a0, dict):
                        return clean({k0: [d_i[k0] for d_i in a] for k0 in a0})

            # All other cases: Do nothing
            return a

        for key, value in d_rdf.items():
            if key in ['@id', '@type']:
                if isinstance(value, list):
                    value = value[0]  # TODO allow multiple types
                value_clean = cb._replace_namespace(value)
            else:
                value_clean = clean(value)

            cb[cb._replace_namespace(key)] = value_clean

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

        json_ld = cls()

        def clean(a):

            if isinstance(a, str):
                return json_ld._replace_prefix(a)

            elif isinstance(a, dict):

                a_ = a.copy()

                if "type" in a_:
                    t = a_.pop("type")
                else:
                    t = None  # TODO

                # values
                if t.lower() == PROPERTY.lower():

                    v_ = a_["value"]
                    # Returns a list
                    if isinstance(v_, list):
                        return [{"@value": v_i} for v_i in v_]
                    else:
                        return [{"@value": v_}]

                elif t.lower() == "Relationship".lower():
                    v_ = a_["object"]
                    # Returns a list

                    if isinstance(v_, list):
                        return [{"@id": json_ld._replace_prefix(v_i)} for v_i in v_]
                    else:
                        return [{"@id": json_ld._replace_prefix(v_)}]
                else:  # None
                    return {k_: clean(v_) for k_, v_ in a_.items()}

                # Convert {value: [a, b]} -> [{value: a}, {value: b}]

                l_ = []

                d_ = {}
                for k_, v_ in a_.items():

                    # we double check, is this necessary?
                    if k_ == "value" and t.lower() == PROPERTY.lower():
                        k_ = "@value"
                    elif k_ == "object" and t.lower() == "Relationship".lower():
                        k_ = "@id"

                    if isinstance(v_, list):
                        print('')
                        ...
                        pass

                    d_[k_] = clean(v_)

                return [d_]

            elif isinstance(a, list):

                return [clean(b) for b in a]

            return a  # Do nothing

        for key, value in d_cb.items():
            if key == "@context":  # Skip
                continue

            if key == '@type':
                value_clean = [json_ld._replace_prefix(value)]
            else:
                value_clean = clean(value)

            json_ld[key] = value_clean

        return json_ld

    @staticmethod
    def _replace_prefix(value):
        if ":" in value:
            ns, end = value.split(':', 1)

            ns_full = NAMESPACES.get(ns)
            if ns_full is None:
                value_clean = value
            else:
                value_clean = ns_full + end
        else:
            value_clean = value
        return value_clean


def parse_json_ld(filename, debug=False):
    with open(filename) as f:
        j = json.load(f)

    n_ok = 0
    n_not_ok = 0

    for graph in j:
        graph["@id"]
        graph["@graph"]

        for item in graph["@graph"]:

            # if debug:
            #     print(json.dumps(item))

            item_clean = ItemContextBroker.from_RDF(item)

            r = requests.post(URL_V1,
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

    conn = OrionConnector(URL_ORION)

    n_count = conn.count_entities()
    print(f"# Before = {n_count}. Trying to get to 0.")

    n_ok = 0
    n_not_ok = 0

    limit = 10  # 100

    def get_json_all():

        json_all = []

        for offset in range(0, n_count, limit):
            r = requests.get(URL_V2,
                             params={
                                 "limit": str(limit),
                                 "offset": str(offset)
                             }
                             )

            json_all += r.json()

        return json_all

    json_all = get_json_all()

    # Delete every link
    for item in json_all:
        s_id = item["id"]
        s_type = item["type"]

        if 1:

            b = 0
            if b:

                r = requests.delete(URL_V1 + urllib.parse.quote_plus(s_id))
            else:
                r = requests.delete(URL_V1 + s_id)

        else:
            body = f"""
            {{
              "actionType":"delete",
              "entities":[
                {{
                  "id":"{s_id}", "type":"{s_type}"
                }}
              ]
            }}
            """
            r = requests.post("http://localhost:1026/v2/op/update",
                              headers={"Content-Type": "application/json"},  # HEADERS
                              json=body)

        if not r.ok:
            if debug:
                warnings.warn("Something went wrong.")
            n_not_ok += 1
        else:
            n_ok += 1

    print(f'#     ok = {n_ok}\n'
          f'# not ok = {n_not_ok}')

    n_count_after = conn.count_entities()
    print(f"#  After = {n_count_after}. (Should be *Before* - *#OK* = *#Not ok.*)")

    return


if __name__ == '__main__':
    filename = input("Enter filename of CPSV-AP in JSONLD format:\n")
    parse_json_ld(filename)
