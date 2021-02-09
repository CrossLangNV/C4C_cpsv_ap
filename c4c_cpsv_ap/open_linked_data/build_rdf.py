from rdflib.graph import Graph
from rdflib.term import Literal, URIRef
from rdflib.namespace import RDF, Namespace, DCAT, DCTERMS, SKOS

from rdflib.term import _serial_number_generator

CPSV = Namespace("http://purl.org/vocab/cpsv#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

C4C = Namespace("http://cefat4cities.crosslang.com/content/")
SCHEMA = Namespace("https://schema.org/")

URL = 'url'
TITLE = 'title'
PHONE = 'phone'
EMAILS = 'emails'
OPENING_HOURS = 'opening_hours'


def get_list(v):
    assert isinstance(v, list)
    return v


def get_url(v):
    assert isinstance(v, list)
    assert len(v) == 1
    return v[0]


def get_title(v):
    assert isinstance(v, str)
    return v


class PublicService:
    uri: str = None
    title: str = None

    def __init__(self,
                 uri: str,
                 title: str):
        """

        :param url: will be used as the unique id for the PS as URI.
        """

        self.uri = uri
        self.title = title

        pass

    @classmethod
    def from_dict(cls, page: dict):

        url = get_url(page.pop(URL))
        title = get_title(page.pop(TITLE))

        try:
            return cls(uri=url,
                       title=title
                       )
        except Exception as e:
            print(e,
                  "If certain variables are not yet defined. It's because they were not found, while they should have!")


class ContactPoint:
    l_phone: list = None
    l_emails: list = None
    l_opening_hours: list = None

    def __init__(self,
                 l_phone=[],
                 l_emails=[],
                 l_opening_hours=[]):
        """

        :param l_phone: List with phone numbers
        :param l_emails: List with email contacts
        :param l_opening_hours: List with information about opening hours
        """

        self.l_phone = l_phone
        self.l_emails = l_emails
        self.l_opening_hours = l_opening_hours

    @classmethod
    def from_dict(cls, page: dict):

        l_phone = get_list(page.pop(PHONE))
        l_emails = get_list(page.pop(EMAILS))
        l_opening_hours = get_list(page.pop(OPENING_HOURS))

        try:
            return cls(l_phone=l_phone,
                       l_emails=l_emails,
                       l_opening_hours=l_opening_hours
                       )
        except Exception as e:
            print(e,
                  "If certain variables are not yet defined. It's because they were not found, while they should have!")


# TODO move to other file
class CPSV_APGraph(Graph):

    def __init__(self, *args, **kwargs):
        super(CPSV_APGraph, self).__init__(*args, **kwargs)

        self.bind('cpsv', CPSV)
        self.bind('dct', DCTERMS)
        self.bind('dcat', DCAT)
        self.bind('vcard', VCARD)
        self.bind('schema', SCHEMA)
        self.bind('skos', SKOS)

    def add_public_service(self, public_service: PublicService):
        uri = public_service.uri
        uri_ref = URIRef(uri)

        title = public_service.title

        self.add((uri_ref, RDF.type, RDF.Description))
        self.add((uri_ref, RDF.type, CPSV.PublicService))

        # Mandatory
        self.add((uri_ref, DCTERMS.identifier, Literal(title_to_identifier(title))))
        self.add((uri_ref, DCTERMS.description, Literal('TODO')))  # TODO
        self.add((uri_ref, DCTERMS.title, Literal(title)))

        return uri_ref

    def add_contact_point(self, contact_point: ContactPoint):
        """

        :param contact_point:
        :return:
            If contact info was found, it returns URI to contact_info
        """

        l_emails = contact_point.l_emails
        l_opening_hours = contact_point.l_opening_hours
        l_phone = contact_point.l_phone

        if not (len(l_emails) or len(l_opening_hours) or len(l_phone)):
            # No contact info found
            return

        id = 'contactPoint' + _serial_number_generator()()
        uri_ref = URIRef(id, base=C4C)

        self.add((uri_ref, RDF.type, RDF.Description))
        self.add((uri_ref, RDF.type, DCAT.ContactPoint))  # ['ContactPoPublicService']))

        for email in l_emails:
            self.add((uri_ref,
                      VCARD.hasEmail,
                      Literal(email)))

        for opening_hour in l_opening_hours:
            # TODO finetune
            self.add((uri_ref,
                      SCHEMA.openingHours,
                      Literal(opening_hour)))

        for phone in l_phone:
            self.add((uri_ref,
                      VCARD.hasTelephone,
                      Literal(phone)))

        return uri_ref

    def link_ps_cp(self, ps_uri, cp_uri):

        if not isinstance(ps_uri, URIRef):
            # EAFP
            ps_uri = URIRef(ps_uri)

        if not isinstance(cp_uri, URIRef):
            # EAFP
            cp_uri = URIRef(cp_uri)

        self.add((URIRef(ps_uri), DCAT.hasContactPoint, URIRef(cp_uri)))

    def add_concepts(self, l_terms, public_service_uri: URIRef):

        if not isinstance(public_service_uri, URIRef):
            # EAFP
            public_service_uri = URIRef(public_service_uri)

        q = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?subject
        WHERE {{
            ?subject rdf:type skos:Concept ;
                skos:prefLabel "{term}" .  
        }}
        """

        l_uri = []

        for term in l_terms:

            r = [s for s, *_ in self.query(q.format(term=term))]

            if len(r):
                l_uri.extend(r)

            # Add to graph if it doesn't exist yet
            else:
                id = 'concept' + _serial_number_generator()()
                uri_ref = URIRef(id, base=C4C)

                self.add((uri_ref, RDF.type, RDF.Description))
                self.add((uri_ref, RDF.type, SKOS.Concept))  # ['ContactPoPublicService']))
                self.add((uri_ref, SKOS.prefLabel, Literal(term)))

                l_uri.append(uri_ref)

        # Link to public service
        for uri in l_uri:
            self.add((public_service_uri, CPSV.isClassifiedBy, uri))

        return

    def add_life_events(self, l_life_events, public_service_uri: URIRef):
        """ Add life events to the graph

        :param l_life_events:
        :param public_service_uri:
        :return:
        """

        if not isinstance(public_service_uri, URIRef):
            # EAFP
            public_service_uri = URIRef(public_service_uri)

        l_uri = []

        for title in l_life_events:

            # Cast to _literal_n3 to make sure special characters are handled correctly.
            q = f"""

            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX cpsv: <{CPSV}>

            SELECT ?subject
            WHERE {{
                ?subject rdf:type cpsv:LifeEvent ;
                    dct:title {Literal(title)._literal_n3()} .
            }}
            """

            r = [s for s, *_ in self.query(q)]

            if len(r):
                l_uri.extend(r)

            # Add to graph if it doesn't exist yet
            else:
                id = 'lifeEvent' + _serial_number_generator()()
                uri_ref = URIRef(id, base=C4C)

                self.add((uri_ref, RDF.type, RDF.Description))
                self.add((uri_ref, RDF.type, CPSV.LifeEvent))

                # Mandatory
                self.add((uri_ref, DCTERMS.identifier, Literal(title_to_identifier(title))))  # TODO
                self.add((uri_ref, DCTERMS.title, Literal(title)))

                l_uri.append(uri_ref)

        # # Link to public service
        for uri in l_uri:
            self.add((public_service_uri, CPSV.isClassifiedBy, uri))
            self.add((uri, CPSV.isGroupedBy, public_service_uri))

        return


def title_to_identifier(s: str):
    return s.title().replace(' ', '')
