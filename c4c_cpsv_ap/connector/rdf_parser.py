from typing import List

from SPARQLWrapper.Wrapper import JSON, SPARQLWrapper
from rdflib.term import Literal, URIRef

from ..open_linked_data.queries import get_public_services

PRED = 'pred'
URI = "uri"
LABEL = 'label'


class Provider:
    pass


class SPARQLConnector(Provider):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        # RDF
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)  # JSON or XML only give valid response

    def query(self, q: str):
        self.sparql.setQuery(q)

        r = self.sparql.query()
        results = r.convert()

        l = []
        for result in results["results"]["bindings"]:
            l.append(
                {k: (URIRef(v['value']) if v.get('type') == 'uri' else Literal(v['value']))
                 for k, v in result.items()
                 })

        return l


class SPARQLPublicServicesProvider(SPARQLConnector):

    def get_public_service_uris(self) -> List[URIRef]:
        """

        :return: A list of URI's to the webpages, which are used as indices to the public services.
        """

        l_ps = get_public_services(self.endpoint)

        l_ps_uri = [ps_i.get(URI) for ps_i in l_ps]

        return l_ps_uri

    def get_relations(self):
        """ Find the different types of entities for the dropdown menus.
        
        :return: 
        """

        q = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>
    
            SELECT distinct ?{PRED}
            WHERE {{ 
                Graph ?graph {{
                    ?uri rdf:type <http://purl.org/vocab/cpsv#PublicService> ;
                        ?{PRED} ?object .
                    ?object a ?type	. # Filters Literals
                }}
            }}
        """

        l = self.query(q)

        l_pred = [l_i.get(PRED) for l_i in l]

        q_opposite_has = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>

            SELECT distinct ?{PRED}
            WHERE {{ 
                
                Graph ?graph {{
                    ?uri rdf:type <http://purl.org/vocab/cpsv#PublicService> .
                      ?object ?{PRED} ?uri .
                    ?object a ?type	. # Filters Literals
                }}
            }}
        """

        return l_pred

    def get_contact_points(self, has_uri=URIRef('http://www.w3.org/ns/dcat#hasContactPoint')):
        """ Can only return URI's to the contact points as they don't have a label (yet).

        :param has_uri: default should be fine
        :return: List of dictionary with URI.
        """

        if not isinstance(has_uri, URIRef):
            has_uri = URIRef(has_uri)

        q = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT distinct  ?{URI}
            WHERE {{
                Graph ?graph {{
                    ?ps rdf:type cpsv:PublicService ;
                       {has_uri.n3()} ?{URI} .
                }}
            }}
        """

        q_debug = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT distinct  ?label # ?pred ?uri
            WHERE {
                Graph ?graph {
                    ?ps rdf:type cpsv:PublicService ;
                       <http://www.w3.org/ns/dcat#hasContactPoint> ?uri .
                    ?uri ?pred ?label
                }
            }
        """

        # print(q)

        l = self.query(q)

        return l

    def get_competent_authorities(self, has_uri=URIRef('http://data.europa.eu/m8g/hasCompetentAuthority')):
        """

        :param has_uri: default should be fine
        :return: List with dictionaries with the keys URI (ID) and LABEL (string representation).
        """

        if not isinstance(has_uri, URIRef):
            has_uri = URIRef(has_uri)

        q = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT distinct ?{URI} ?{LABEL}
            WHERE {{
                Graph ?graph {{
                    ?ps rdf:type cpsv:PublicService ;
                        {has_uri.n3()} ?{URI} .
                    ?{URI} skos:prefLabel ?{LABEL}
                }}
            }}
        """

        l = self.query(q)

        return l

    def get_concepts(self, has_uri=URIRef('http://purl.org/vocab/cpsv#isClassifiedBy')):
        """ Returns the concepts the public service is classified by.

        :param has_uri: default should be fine
        :return: List with dictionaries with the keys URI (ID) and LABEL (string representation).
        """

        if not isinstance(has_uri, URIRef):
            has_uri = URIRef(has_uri)

        q = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT distinct ?{URI} ?{LABEL}
            WHERE {{
                Graph ?graph {{
                    ?ps rdf:type cpsv:PublicService ;
                        {has_uri.n3()} ?{URI} .
                    ?{URI} skos:prefLabel ?{LABEL}
                }}
            }}
        """

        l = self.query(q)

        return l

    def get_public_service_uris_filter(self,
                                       filter_concepts: List[str] = [],
                                       filter_public_organization: List[str] = [],
                                       filter_contact_point: List[URIRef] = []
                                       ) -> List[URIRef]:
        """

        :return: A list of URI's to the webpages, which are used as indices to the public services.
        """

        VALUE_C = 'value_c'
        VALUE_PO = 'value_po'

        URI_CP = 'uri_cp'

        def _get_q_filter(literal, l_f):
            f_s = 'UCASE(?{literal}) = UCASE({value})'

            if isinstance(l_f, str):
                q_filter = f"""
                        FILTER ({f_s.format(literal=literal, value=Literal(l_f).n3())})
                    """
            else:
                l_q_filter = map(lambda s: f_s.format(literal=literal, value=Literal(s).n3()), l_f)

                q_filter = f"""
                    FILTER ({"||".join(l_q_filter)})
                """

            return q_filter

        def _get_q_filter_uri(uri, l_f):
            f_s = '?{uri} = {value}'

            if isinstance(l_f, str):
                q_filter = f"""
                        FILTER ({f_s.format(uri=uri, value=URIRef(l_f).n3())})
                    """
            else:
                l_q_filter = map(lambda s: f_s.format(uri=uri, value=URIRef(s).n3()), l_f)

                q_filter = f"""
                    FILTER ({"||".join(l_q_filter)})
                """

            return q_filter

        q_filter_concept = _get_q_filter(VALUE_C, filter_concepts) if filter_concepts else ''

        q_filter_public_org = _get_q_filter(VALUE_PO, filter_public_organization) if filter_public_organization else ''

        # TODO
        q_filter_contact_point = _get_q_filter_uri(URI_CP, filter_contact_point) if filter_contact_point else ''

        q = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX cv: <http://data.europa.eu/m8g/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            
            SELECT distinct ?{URI} # ?uri ?value
            WHERE {{
                Graph ?graph {{
                    ?{URI} rdf:type cpsv:PublicService .
                                   
                    OPTIONAL{{
                        ?{URI} cpsv:isClassifiedBy ?uri_c .
                        ?uri_c skos:prefLabel ?{VALUE_C} .
                    }}
                    OPTIONAL{{
                        ?{URI} cv:hasCompetentAuthority ?uri_po .
                        ?uri_po ?pred ?{VALUE_PO} .
                    }}
                    OPTIONAL{{
                        ?{URI} dcat:hasContactPoint ?{URI_CP} .
                    }} 
                    {q_filter_concept}
                    {q_filter_public_org}
                    {q_filter_contact_point}
                }}
            }}
        """

        l = self.query(q)

        l_uri = list(map(lambda d: d.get(URI), l))

        return l_uri

    def _get_all_relationship_and_predicates(self):
        """ Good debugging query

        :return:
        """

        q_debug = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>
            PREFIX terms: <http://purl.org/dc/terms/>
    
            SELECT distinct ?pred ?pred_link
            WHERE { 
                Graph ?graph {
                    ?uri rdf:type <http://purl.org/vocab/cpsv#PublicService> ;
                        ?pred ?object .
                    ?object a ?type	. # Filters Literals
    				?object ?pred_link ?val
                }
            }
        """

        l = self.query(q_debug)
        return l
