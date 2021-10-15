import abc
import warnings
from typing import List, Generator, Dict, Union

from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.namespace import DCAT, DCTERMS, RDF, SKOS
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.term import Identifier, Literal
from rdflib.term import URIRef
from rdflib.term import _serial_number_generator

from c4c_cpsv_ap.models import PublicService, Concept, CPSVAPModel, PublicOrganisation
from c4c_cpsv_ap.namespace import CPSV, VCARD, C4C, SCHEMA, CV

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
        self.public_organisations = PublicOrganisationsHarvester(self)
        self.locations = LocationsHarvester(self)

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
        self.public_organisations = PublicOrganisationsProvider(self)
        self.locations = LocationsProvider(self)


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
    def get(self, uri: URIRef) -> CPSVAPModel:
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
    def add(self,
            obj: CPSVAPModel,
            context: str,
            uri: URIRef = None) -> URIRef:
        """
        Add a new item to the RDF.

        Args:
            obj: An item object, see models.py
            context:
            uri:

        Returns:
            URI to the new item in the RDF.
        """
        pass

    def update(self,
               obj: CPSVAPModel,
               uri: URIRef,
               context: str
               ) -> URIRef:
        """
        Update an item from the RDF. When one or multiple of the links are updated

        Args:
            obj: An item object, see models.py
            uri (URIRef): URI to the item in the RDF.
            context (Optional): SubGraph

        Returns:
            original URI of item

        TODO:
         * This could be part of add, by just adding the URI as an option. If None, generate new, else use the
         URI and overwrite the previous one? But then we also would have to delete previous links, so an explicit
         update might be better.

        """

        uri = URIRef(uri)
        context = URIRef(context)

        self.delete(uri,
                    context=context)
        self.add(obj,
                 context=context,
                 uri=uri)

        return uri

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


class LocationsHarvester(SubHarvester):
    def get_all(self) -> List[URIRef]:
        raise NotImplementedError()

    def get(self, uri: URIRef) -> CPSVAPModel:
        raise NotImplementedError()


class LocationsProvider(SubProvider, LocationsHarvester):
    def add(self,
            uri_spat: URIRef,
            context=None) -> URIRef:
        """
        Like <dct:Location rdf:about="http://cpsv-ap.semic.eu/cpsv-ap_editor/content/mikkeli">
        """

        self.provider.graph.add((uri_spat, RDF.type, DCTERMS.Location, context))

        try:
            tmp_graph = Graph()
            tmp_graph.parse(str(uri_spat), format='xml')
            for label in list(tmp_graph.objects(URIRef(uri_spat), SKOS.prefLabel)):
                self.provider.graph.add((uri_spat, SKOS.prefLabel, label, context))
        except:
            warnings.warn('Did not succeed in extracting ATU info.')

        return uri_spat


class PublicOrganisationsHarvester(SubHarvester):
    def get_all(self) -> List[URIRef]:
        raise NotImplementedError()

    def get(self, uri: URIRef, context=None) -> PublicOrganisation:

        label = str(self.get_preferred_label(uri, context=context))
        spatial = list(map(str, self.get_spatial(uri, context=context)))

        return PublicOrganisation(pref_label=label,
                                  spatial=spatial)

    def search(self, obj: PublicOrganisation, context: str = None):

        def get_label_literal(obj: PublicOrganisation):
            label = obj.pref_label
            if isinstance(label, dict):
                # One is enough
                lang, label_val = list(label.items())[0]
                label_lit = Literal(label_val, lang=lang)
            else:
                label_lit = Literal(label)

            return label_lit

        def get_l_spatial_uri(obj: PublicOrganisation):
            return [URIRef(uri) for uri in obj.spatial]

        label_lit = get_label_literal(obj)
        l_spatial_uri = get_l_spatial_uri(obj)

        # Filter on label
        for s_label, _, _ in self.harvester.graph.triples((None, SKOS.prefLabel, label_lit, context)):

            ok = True
            # Filter on spatial
            for spatial_uri in l_spatial_uri:
                if not list(self.harvester.graph.triples((s_label, DCTERMS.spatial, spatial_uri), context=context)):
                    ok = False
                    break

            if ok:
                yield s_label

    def get_spatial(self, uri: URIRef, context=None) -> List[URIRef]:
        return [o for _, _, o in self.harvester.graph.triples((uri, DCTERMS.spatial, None), context=context)]

    def get_preferred_label(self, uri: URIRef, context=None) -> Literal:
        """ Only a single label is allowed """

        return get_single_el_from_list(
            [o for _, _, o in self.harvester.graph.triples((uri, SKOS.prefLabel, None), context=context)])


class PublicOrganisationsProvider(SubProvider, PublicOrganisationsHarvester):
    def add(self, obj: PublicOrganisation, context: str, uri: URIRef = None) -> URIRef:

        if uri is None:
            uri = uriref_generator('PublicOrganisation', C4C)

        uri_ref = URIRef(uri)

        if not isinstance(context, URIRef):
            context = URIRef(context)

        # self.provider.graph.add((uri_ref, RDF.type, RDF.Description)) # TODO find out if this is necessary/existing?
        self.provider.graph.add((uri_ref, RDF.type, CV.PublicOrganisation, context))

        # Mandatory
        pref_label = obj.pref_label
        if isinstance(pref_label, str):
            self.provider.graph.add((uri_ref, SKOS.prefLabel, Literal(obj.pref_label), context))

        elif isinstance(pref_label, dict):
            # ! only one allowed

            for i, (lang, label_val) in enumerate(pref_label.items()):

                if i > 0:
                    warnings.warn("Only one label allowed for Public services")
                    break

                _t = (uri_ref, SKOS.prefLabel, Literal(label_val, lang=lang), context)
                self.provider.graph.add(_t)

        else:
            raise ValueError(f'{pref_label} Should be str or dict')

        # Spatial
        for uri_spat in obj.spatial:
            uri_spat = URIRef(uri_spat)
            self.provider.graph.add((uri_ref, DCTERMS.spatial, uri_spat, context))

            self.provider.locations.add(uri_spat, context=context)

        return uri_ref


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

        title = self.harvester.graph.value(uri, DCTERMS.title, None, any=False)
        identifier = self.harvester.graph.value(uri, DCTERMS.identifier, None, any=False)
        description = self.harvester.graph.value(uri, DCTERMS.description, None, any=False)

        def get_public_org_from_public_service(uri):

            uri_public_org = self.harvester.graph.value(uri, CV.hasCompetentAuthority, None, any=False)

            public_org = self.harvester.public_organisations.get(uri_public_org)

            return public_org

        public_org = get_public_org_from_public_service(uri)

        keywords = list(map(str, self.harvester.graph.objects(uri, DCAT.keyword)))

        l_concepts: List[Concept] = []
        for uri_concept in self.harvester.graph.objects(uri, CV.isClassifiedBy):
            concept = self.harvester.concepts.get(uri_concept)
            if concept is not None:
                l_concepts.append(concept)

        return PublicService(
            name=xstr(title),
            description=xstr(description),
            identifier=xstr(identifier),
            has_competent_authority=public_org,
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

        uri_public_org = \
            list(self.provider.public_organisations.search(public_service.has_competent_authority, context=context))[0]
        self.provider.graph.add((uri_ref, CV.hasCompetentAuthority, uri_public_org, context))

        # keyword
        for keyword in public_service.keyword:
            self.provider.graph.add((uri_ref, DCAT.keyword, Literal(keyword), context))

        # IsClassified
        # requires Concepts. For this we have to have concepts first in the RDF and in models.py
        for concept in public_service.classified_by:
            # TODO find previously existing concept with this label and get uri.
            uri_concept = self.provider.concepts.add(concept, context=context)
            self.provider.graph.add((uri_ref, CV.isClassifiedBy, uri_concept, context))

        return uri_ref


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

    if isinstance(l, list):
        if len(l) != 1:
            warnings.warn('Expected a list with only one item, '
                          'will return first element.', UserWarning)
        return l[0]

    elif isinstance(l, str):
        # Expected a list, but this is fine.
        return l

    else:
        raise ValueError(f'Unknown input: {l}')


def xstr(s) -> Union[str, None]:
    """

    Args:
        s: to be casted to string

    Returns:
        string or
    """
    return str(s) if s is not None else None
