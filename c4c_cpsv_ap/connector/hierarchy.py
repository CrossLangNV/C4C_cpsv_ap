import abc
from typing import List, Generator, Dict

import rdflib
import rdflib.graph
from rdflib import URIRef, Namespace
from rdflib.namespace import DCTERMS
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.term import Identifier

from c4c_cpsv_ap.models import PublicService

NS_CSPV = Namespace('http://purl.org/vocab/cpsv#')
TYPE_PUBLICSERVICE = NS_CSPV.PublicService
TYPE_ISCLASSIFIEDBY = NS_CSPV.isClassifiedBy

SUBJ = 'subj'
PRED = 'pred'
OBJ = 'obj'
URI = "uri"
LABEL = 'label'
GRAPH = 'graph'
TITLE = "title"
DESCRIPTION = 'description'


class Provider:
    """
    A provider of CSVP-AP data.
    Sends the relevant SPARQL queries to the Fuseki server.
    """

    def __init__(self, endpoint: str):
        store = SPARQLStore(endpoint)
        self.graph = rdflib.Graph(store)

        # TODO remove
        # berlin = rdflib.URIRef("http://dbpedia.org/resource/Berlin")
        # for label in graph.objects(berlin, rdflib.RDFS.label):
        #     print
        #     label

        self.public_services = PublicServicesProvider(self)

    def query(self, q) -> Generator[Dict[str, Identifier], None, None]:
        """
        Returns
        :param q: SparqlQuery
        :return:
        """

        qres = self.graph.query(q)

        for l_i in qres:
            yield {str(k): v for k, v in zip(qres.vars, l_i)}


class SubProvider(abc.ABC):
    """
    Nested classes of provider
    """

    def __init__(self, provider: Provider):
        self.provider = provider

    def query(self, q):
        return self.provider.query(q)

    @abc.abstractmethod
    def get_all(self) -> List[URIRef]:
        """
        Get all the items
        :return:
        """
        pass

    @abc.abstractmethod
    def get(self, uri: URIRef) -> object:
        """
        Get specific item based on uri
        :return:
        """
        pass


class PublicServicesProvider(SubProvider):

    def get_all(self,
                graph_uri: URIRef = None,
                debug=True
                ) -> List[URIRef]:
        q_filter = f"""
                values ?{GRAPH} {{ {URIRef(graph_uri).n3()} }} 
                """ if graph_uri is not None else ''

        q = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX cpsv: <http://purl.org/vocab/cpsv#>
        PREFIX terms: <http://purl.org/dc/terms/>

        SELECT distinct ?{URI} ?{TITLE} ?{DESCRIPTION} ?{GRAPH}
            WHERE {{
                {q_filter}
                Graph ?{GRAPH} {{
                    ?{URI} a {TYPE_PUBLICSERVICE.n3()} ;
                        terms:title ?{TITLE} ;
                        terms:description ?{DESCRIPTION} .
                }}
            }}
            ORDER BY ?{URI}
        """

        if debug:
            print(q)

        l_ps = self.query(q)
        l_ps_uri = [ps_i.get(URI) for ps_i in l_ps]
        return l_ps_uri

    def get(self, uri: URIRef) -> PublicService:

        if not isinstance(uri, URIRef):
            uri = URIRef(uri)

        q = f"""
        SELECT ?{PRED} ?{OBJ}
        WHERE {{
            Graph ?g {{
                {uri.n3()} ?{PRED} ?{OBJ} .
            }}
        }}
        """

        l_query = self.query(q)

        l_concepts: List[URIRef] = []

        for d_i in l_query:

            pred = d_i[PRED]
            obj = d_i[OBJ]
            if pred == TYPE_ISCLASSIFIEDBY:
                l_concepts.append(obj)
            elif pred == DCTERMS.title:
                title = str(obj)
            elif pred == DCTERMS.identifier:
                identifier = str(obj)
            elif pred == DCTERMS.description:
                description =str(obj)

        return PublicService(
            name = title,
            description = description,
            identifier = identifier,
            classified_by=l_concepts,
        )
