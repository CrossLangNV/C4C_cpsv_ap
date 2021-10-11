import abc
from typing import List, Generator, Dict, Union

from rdflib.graph import ConjunctiveGraph
from rdflib.namespace import DCAT, DCTERMS, RDF, SKOS
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.term import Identifier, Literal
from rdflib.term import URIRef
from rdflib.term import _serial_number_generator

from c4c_cpsv_ap.models import PublicService, Concept
from c4c_cpsv_ap.namespace import CPSV, VCARD, C4C, SCHEMA

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

    def set(self, triple_or_quad):
        """Convenience method to update the value of object
        Allow to add quad

        Remove any existing triples for subject and predicate before adding
        (subject, predicate, object).
        """

        (subject, predicate, object_, context) = self._spoc(triple_or_quad, default=True)

        assert (
                subject is not None
        ), "s can't be None in .set([s,p,o]), as it would remove (*, p, *)"
        assert (
                predicate is not None
        ), "p can't be None in .set([s,p,o]), as it would remove (s, *, *)"
        self.remove((subject, predicate, None, context))
        self.add((subject, predicate, object_, context))
        return self


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
        Harvester of CPSV-data.

        1. Will use endpoint if available,
        2. else use store,
        3. if nothing is provided, it will start with an empty Graph.
        Args:
            endpoint:
            source:
            graph_uri: URI with the name of the graph. (only used when source is used)
        """

        if endpoint:
            store = SPARQLStore(endpoint)
            g = CPSV_APGraph(store)

        elif source:
            g = CPSV_APGraph()
            g.parse(source, publicID=graph_uri)

        else:
            g = CPSV_APGraph()  # Empty graph

        self.graph = g

        self.concepts = ConceptsHarvester(self)
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.concepts = ConceptsProvider(self)
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
    TODO how to add write rights for endpoint.
    """

    def __init__(self, provider: Provider):
        super().__init__(harvester=provider)
        self.provider = provider

    @abc.abstractmethod
    def add(self, *args, **kwargs) -> URIRef:
        """
        Add a new item to the RDF.

        Args:
            obj: An item object, see models.py

        Returns:
            URI to the new item in the RDF.
        """
        pass

    @abc.abstractmethod
    def update(self, *args) -> None:
        """
        Update an item from the RDF. When one or multiple of the links are updated

        Args:
            obj: An item object, see models.py
            uri (URIRef): URI to the item in the RDF.

        Returns:

        TODO:
         * This could be part of add, by just adding the URI as an option. If None, generate new, else use the
         URI and overwrite the previous one? But then we also would have to delete previous links, so an explicit
         update might be better.

        """
        pass

    def delete(self,
               uri: URIRef,
               context: str
               ) -> None:
        """
        Remove an item from the RDF.

        Args:
            uri: Main uri to the item in the RDF.
            context: subgraph uri

        Returns:

        """

        # this will remove all matching triples:
        self.provider.graph.remove((uri, None, None, context))
        self.provider.graph.remove((None, None, uri, context))


class ConceptsHarvester(SubHarvester):
    def get_all(self,
                graph_uri: URIRef = None,
                debug=False
                ) -> List[URIRef]:
        q_filter = f"""
                values ?{GRAPH} {{ {URIRef(graph_uri).n3()} }}
                """ if graph_uri is not None else ''

        q = f"""
        SELECT distinct ?{URI} ?{LABEL} ?{GRAPH}
            WHERE {{
                {q_filter}
                Graph ?{GRAPH} {{
                    ?{URI} a {SKOS.Concept.n3()} ;
                        {SKOS.prefLabel.n3()} ?{LABEL} .

                }}
            }}
            ORDER BY ?{URI}
        """

        if debug:
            print(q)

        l_c = self.query(q)
        l_c_uri = [ps_i.get(URI) for ps_i in l_c]

        return l_c_uri

    def get(self,
            uri: URIRef,
            ) -> Concept:

        if not isinstance(uri, URIRef):
            uri = URIRef(uri)

        # TODO use graph.objects() when we allow multiple labels.
        pref_label = xstr(self.harvester.graph.value(uri, SKOS.prefLabel, None, any=False))

        if pref_label is not None:
            return Concept(
                pref_label=pref_label,
            )


class ConceptsProvider(SubProvider, ConceptsHarvester):
    def add(self,
            concept: Concept,
            context: str,
            uri: str = None
            ) -> URIRef:

        if uri is None:
            uri = uriref_generator('Concept', C4C)

        uri_ref = URIRef(uri)

        if not isinstance(context, URIRef):
            context = URIRef(context)

        # self.provider.graph.add((uri_ref, RDF.type, RDF.Description)) # TODO find out if this is necessary/existing?
        self.provider.graph.add((uri_ref, RDF.type, SKOS.Concept, context))

        # Mandatory
        self.provider.graph.add((uri_ref, SKOS.prefLabel, Literal(concept.pref_label), context))

        return uri_ref

    def update(self,
               concept: Concept,
               uri_c: URIRef,
               context: str) -> URIRef:
        """

        Args:
            concept (Concept): Contains all the information of the concept.
            uri_ps: URI of the previous concept.
            # context: subgraph uri

        """

        # Mandatory
        self.provider.graph.set((uri_c, SKOS.prefLabel, Literal(concept.pref_label), context))

        return uri_c


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
                    ?{URI} a {CPSV.PublicService.n3()} ;
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

        l_concepts: List[Concept] = []
        for uri_concept in self.harvester.graph.objects(uri, CPSV.isClassifiedBy):
            concept = self.harvester.concepts.get(uri_concept)
            if concept is not None:
                l_concepts.append(concept)

        title = self.harvester.graph.value(uri, DCTERMS.title, None, any=False)
        identifier = self.harvester.graph.value(uri, DCTERMS.identifier, None, any=False)
        description = self.harvester.graph.value(uri, DCTERMS.description, None, any=False)

        keywords = list(map(str, self.harvester.graph.objects(uri, DCAT.keyword)))

        return PublicService(
            name=xstr(title),
            description=xstr(description),
            identifier=xstr(identifier),
            keyword=keywords,
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
            uri (str, Optional): Specify the URI of new public service. If None, a new one is generated.

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

        # keyword
        for keyword in public_service.keyword:
            self.provider.graph.add((uri_ref, DCAT.keyword, Literal(keyword), context))

        # IsClassified
        # requires Concepts. For this we have to have concepts first in the RDF and in models.py
        for concept in public_service.classified_by:
            # TODO find previously existing concept with this label and get uri.
            uri_concept = self.provider.concepts.add(concept, context=context)
            self.provider.graph.add((uri_ref, CPSV.isClassifiedBy, uri_concept, context))

        return uri_ref

    def update(self,
               public_service: PublicService,
               uri_ps: URIRef,
               context: str) -> URIRef:
        """

        Args:
            public_service (PublicService): Contains all the information of the public service.
            uri_ps: URI of the previous public service.
            context: subgraph uri

        """

        # Mandatory
        self.provider.graph.set((uri_ps, DCTERMS.identifier, Literal(public_service.identifier), context))
        self.provider.graph.set((uri_ps, DCTERMS.description, Literal(public_service.description), context))
        self.provider.graph.set((uri_ps, DCTERMS.title, Literal(public_service.name), context))

        return uri_ps


def id_generator() -> str:
    return _serial_number_generator()()


def uriref_generator(name: str, base=None) -> URIRef:
    val = name + id_generator()
    return URIRef(val, base=base)


def get_single_el_from_list(l: list):
    """
    Expects a list with only one element.
    Args:
        l:

    Returns:
        First and only item.
    """
    assert (len(l)) == 1, len(l)
    assert isinstance(l, list), type(l)
    return l[0]


def xstr(s) -> Union[str, None]:
    """

    Args:
        s: to be casted to string

    Returns:
        string or
    """
    return str(s) if s is not None else None
