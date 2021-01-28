import random
import string
import warnings

from rdflib import Graph, Literal, RDF, Namespace

BASE_NAME = 'c4c'
BASE_NAMESPACE = Namespace("http://cpsv-ap.c4c.com/content/")

SCHEMA = Namespace("https://schema.org/")


class ContactPoint:
    """
    Represent the CPSV-AP contact point.
    """

    l_email = None
    l_telephone = None
    l_url = None

    def __init__(self,
                 telephone_number: str = None,
                 email: str = None,
                 url: str = None,
                 ):

        self.l_email = []
        self.l_telephone = []
        self.l_url = []

        """
        TODO allow multiple entries at construction

        :param telephone_number:  Optional contact telephone number
        :param email: Optional contact email address
        :param url:  Optional web address.
        """

        if email is not None:
            self.add_email(email)
        if telephone_number is not None:
            self.add_telephone(telephone_number)
        if url is not None:
            self.add_url(url)

    def get_l_email(self):
        return self.l_email

    def get_l_telephone(self):
        return self.l_telephone

    def get_l_url(self):
        return self.l_url

    def add_email(self, email: str = None):
        self.l_email.append(email)

    def add_telephone(self, telephone_number: str = None):
        self.l_telephone.append(telephone_number)

    def add_url(self, url: str = None):
        self.l_url.append(url)


class ContactPointGraph(Graph):
    """
    ContactPoint RDF Graph
    """

    def __init__(self, *args, **kwargs):
        super(ContactPointGraph, self).__init__(
            *args, **kwargs)

        self.bind("rdf", RDF)
        self.bind(BASE_NAME, BASE_NAMESPACE)

    def add_contact_point(self, contact_point: ContactPoint):
        """ Add new contact points to the RDF as CPSV-AP Contact Points.

        Args:
            contact_point: a contact point object

        Returns:
            URI to the contact point.
        """

        uri_cp = BASE_NAMESPACE[id_generator()]

        self.add((uri_cp, RDF.type, SCHEMA["ContactPoint"]))

        for email in contact_point.get_l_email():
            self.add((uri_cp, SCHEMA['email'], Literal(email)))

        for telephone in contact_point.get_l_telephone():
            self.add((uri_cp, SCHEMA['telephone'], Literal(telephone)))

        for url in contact_point.get_l_url():
            # TODO, not by default in CPSV-AP
            warnings.warn("URL's are not part of CPSV-AP.", UserWarning)
            break

        return uri_cp

    # def add_terms(self, l_terms: List[str], lang=EN):
    #     """ Add new terms to the RDF as SKOS concepts.
    #
    #     Args:
    #         l_terms: List of the terms in string format
    #         lang: optional language parameter of the terms.
    #
    #     Returns:
    #         list of RDF URI's of the new SKOS concepts.
    #     """
    #
    #     l_terms = list(map(str, l_terms)) #
    #     l_uri = [None for _ in l_terms]    # Initialisation
    #     for i, term_i in enumerate(l_terms):
    #         node_term_i = self.uid_iterator.get_next()
    #
    #         l_uri[i] = node_term_i
    #
    #         self.add((node_term_i,
    #                   RDF.type,
    #                   SKOS.Concept
    #                   ))
    #
    #         self.add((node_term_i,
    #                   SKOS.prefLabel,
    #                   Literal(term_i, lang=lang)
    #                   ))
    #
    #     return l_uri


def id_generator(size=12, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
