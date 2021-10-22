import json
import unittest

from context_broker.script_upload import ItemContextBroker, ItemRDF


class TestConversion(unittest.TestCase):
    def setUp(self, debug=False) -> None:
        self.d_cpsv_ap = {
            '@id': 'http://cefat4cities.crosslang.com/content/BusinessEvent3a219a1b99cb4ad08465933752aed6f2',
            '@type': ['http://data.europa.eu/m8g/BusinessEvent', 'http://data.europa.eu/m8g/Event'],
            'http://purl.org/dc/terms/identifier': [{'@value': '81ae5cedbe664c0a864c90c65c329414'}],
            'http://purl.org/dc/terms/relation': [
                {'@id': 'http://cefat4cities.crosslang.com/content/PublicService891912a426cb48118dbdfe169cd38a62'}],
            'http://purl.org/dc/terms/title': [{'@value': 'Start a new project'}]}

        # TODO add DCTerms to context
        # TODO The context broker should accept multiple items.
        self.d_context_broker = {
            '@id': 'c4c:BusinessEvent3a219a1b99cb4ad08465933752aed6f2',
            '@type': 'http://data.europa.eu/m8g/BusinessEvent',
            'http://purl.org/dc/terms/identifier': [
                {'value': '81ae5cedbe664c0a864c90c65c329414', 'type': 'Property'}],
            'http://purl.org/dc/terms/relation': [
                {
                    'object': 'c4c:PublicService891912a426cb48118dbdfe169cd38a62',
                    'type': 'Relationship'}],
            'http://purl.org/dc/terms/title': [
                {'value': 'Start a new project',
                 'type': 'Property'}],
            '@context': {'c4c': 'http://cefat4cities.crosslang.com/content/'}
        }
        if debug:
            print(json.dumps(self.d_context_broker))

    def test_from_rdf_to_cb(self):
        cb = ItemContextBroker.from_RDF(self.d_cpsv_ap)

        self.assertEqual(self.d_context_broker, cb)

    def test_from_cb_to_rdf(self):
        rdf = ItemRDF.from_context_broker(self.d_context_broker)

        self.assertEqual(self.d_cpsv_ap, rdf)

    def test_from_rdf_to_rdf(self):
        cb = ItemContextBroker.from_RDF(self.d_cpsv_ap)
        rdf = ItemRDF.from_context_broker(cb)

        self.assertEqual(self.d_cpsv_ap, rdf)

    def test_from_cb_to_cb(self):
        rdf = ItemRDF.from_context_broker(self.d_context_broker)
        cb = ItemContextBroker.from_RDF(rdf)

        self.assertEqual(self.d_context_broker, cb)
