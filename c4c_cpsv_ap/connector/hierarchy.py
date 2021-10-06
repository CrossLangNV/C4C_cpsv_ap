import abc
from typing import List, Generator, Dict

from rdflib.graph import ConjunctiveGraph
from rdflib.namespace import Namespace, DCAT, DCTERMS, RDF, SKOS
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.term import Identifier, Literal
from rdflib.term import URIRef
from rdflib.term import _serial_number_generator

from c4c_cpsv_ap.models import PublicService

CPSV = Namespace("http://purl.org/vocab/cpsv#")
CV = Namespace("http://data.europa.eu/m8g/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

C4C = Namespace("http://cefat4cities.crosslang.com/content/")
SCHEMA = Namespace("https://schema.org/")

TYPE_PUBLICSERVICE = CPSV.PublicService
TYPE_ISCLASSIFIEDBY = CPSV.isClassifiedBy

SUBJ = 'subj'
PRED = 'pred'
OBJ = 'obj'
URI = "uri"
LABEL = 'label'
GRAPH = 'graph'
TITLE = "title"
DESCRIPTION = 'description'


class CPSV_APGraph(ConjunctiveGraph):

    def __init__(self, *args, **kwargs):
        super(CPSV_APGraph, self).__init__(*args, **kwargs)

        self.bind("rdf", RDF)
        self.bind('cpsv', CPSV)
        self.bind('dct', DCTERMS)
        self.bind('dcat', DCAT)
        self.bind('vcard', VCARD)
        self.bind('schema', SCHEMA)
        self.bind('skos', SKOS)
        self.bind('c4c', C4C)


class Harvester:
    """
    A harvester of CSVP-AP data.
    Sends the relevant SPARQL queries to the Fuseki server.
    """

    def __init__(self,
                 endpoint: str = None,
                 source: str = None,
                 graph_uri: str = None
                 ):
        """
        Will use endpoint if available, else use store.
        Args:
            endpoint:
            source:
            graph_uri: URI with the name of the graph.
        """

        if not (endpoint or source):
            raise TypeError('Either endpoint or store should be provided.')

        if endpoint:
            store = SPARQLStore(endpoint)
            g = CPSV_APGraph(store)

        else:
            g = CPSV_APGraph()  # To work with named graphs
            g.parse(source, publicID=graph_uri)

        self.graph = g

        self.public_services = PublicServicesHarvester(self)

    def query(self, q) -> Generator[Dict[str, Identifier], None, None]:
        """
        Returns
        :param q: SparqlQuery
        :return:
        """

        qres = self.graph.query(q)

        for l_i in qres:
            yield {str(k): v for k, v in zip(qres.vars, l_i)}


class Provider(Harvester):
    """
    TODO implement generator
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.public_services = PublicServicesProvider(self)


class SubHarvester(abc.ABC):
    """
    Nested classes of harvesters
    """

    def __init__(self, harvester: Harvester):
        self.harvester = harvester

    def query(self, q):
        return self.harvester.query(q)

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


class SubProvider(SubHarvester, abc.ABC):
    """
    Nested classes of providers
    TODO how to add write rights.
    """

    def __init__(self, provider: Provider):
        super().__init__(harvester=provider)
        self.provider = provider

    @abc.abstractmethod
    def add(self, obj: object, *args, **kwargs) -> URIRef:
        """
        Add a new item to the RDF.

        Args:
            obj: One

        Returns:
            uri to the new item in the RDF.
        """
        pass


class PublicServicesHarvester(SubHarvester):

    def get_all(self,
                graph_uri: URIRef = None,
                debug=False
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

    def get(self,
            uri: URIRef,
            debug=False) -> PublicService:

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

        if debug:
            print(q)

        l_query = self.query(q)

        l_concepts: List[URIRef] = []
        title = None
        description = None
        identifier = None

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
                description = str(obj)

        return PublicService(
            name=title,
            description=description,
            identifier=identifier,
            classified_by=l_concepts,
        )


class PublicServicesProvider(SubProvider, PublicServicesHarvester):
    def add(self,
            public_service: PublicService,
            context: str,
            uri: str = None
            ) -> URIRef:
        """

        Args:
            public_service:
            context: subgraph uri
            uri:

        Returns:

        """

        if uri is None:
            uri = uriref_generator('PublicService', C4C)

        uri_ref = URIRef(uri)

        if not isinstance(context, URIRef):
            context = URIRef(context)

        # self.provider.graph.add((uri_ref, RDF.type, RDF.Description)) # TODO find out if this is necessary/existing?
        self.provider.graph.add((uri_ref, RDF.type, CPSV.PublicService, context))

        # Mandatory
        self.provider.graph.add((uri_ref, DCTERMS.identifier, Literal(public_service.identifier), context))
        self.provider.graph.add((uri_ref, DCTERMS.description, Literal(public_service.description), context))
        self.provider.graph.add((uri_ref, DCTERMS.title, Literal(public_service.name), context))

        return uri_ref


def id_generator():
    # def id_generator(size=12, chars=string.ascii_lowercase + string.digits):
    #     return ''.join(random.choice(chars) for _ in range(size))
    return _serial_number_generator()()


def uriref_generator(name: str, base=None):
    val = name + id_generator()
    return URIRef(val, base=base)
