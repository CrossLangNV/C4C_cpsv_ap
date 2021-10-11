from rdflib import URIRef
from rdflib.namespace import DefinedNamespace, Namespace

CV = Namespace("http://data.europa.eu/m8g/")
SCHEMA = Namespace("https://schema.org/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

C4C = Namespace("http://cefat4cities.crosslang.com/content/")


class CPSV(DefinedNamespace):
    """
    Core Public Service Vocabulary Application Profile (CPSV-AP)

    A data model for describing public services and the associated life and business events

    Generated from: https://raw.githubusercontent.com/catalogue-of-services-isa/CPSV-AP/master/releases/2.2.1/SC2015DI07446_D02.02_CPSV-AP_v2.2.1_RDF_Schema_v1.00.ttl
    Date: 2021-10-11 15:28:00.0000
    """

    # http://purl.org/vocab/cpsv#
    PublicService: URIRef
    isClassifiedBy: URIRef

    _NS = Namespace("http://purl.org/vocab/cpsv#")
