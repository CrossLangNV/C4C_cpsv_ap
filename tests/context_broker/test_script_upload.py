import json
import unittest

from context_broker.script_upload import ItemContextBroker, ItemRDF, OrionConnector, URL_ORION


class TestConversion(unittest.TestCase):
    maxDiff = 10000

    def setUp(self, debug=False) -> None:
        self.d_cpsv_ap = {
            '@id': 'http://cefat4cities.crosslang.com/content/BusinessEvent3a219a1b99cb4ad08465933752aed6f2',
            '@type': [
                'http://data.europa.eu/m8g/BusinessEvent',
                # 'http://data.europa.eu/m8g/Event'
            ],
            'http://purl.org/dc/terms/identifier': [
                {'@value': '81ae5cedbe664c0a864c90c65c329414'}],
            'http://purl.org/dc/terms/relation': [
                {'@id': 'http://cefat4cities.crosslang.com/content/PublicService891912a426cb48118dbdfe169cd38a62'}],
            'http://purl.org/dc/terms/title': [
                {'@value': 'Start a new project'}]
        }

        # TODO add DCTerms to context
        # TODO The context broker should accept multiple items.
        self.d_context_broker = {
            '@id': 'c4c:BusinessEvent3a219a1b99cb4ad08465933752aed6f2',
            '@type': 'http://data.europa.eu/m8g/BusinessEvent',
            'http://purl.org/dc/terms/identifier':
                {'value': '81ae5cedbe664c0a864c90c65c329414', 'type': 'Property'},
            'http://purl.org/dc/terms/relation':
                {'object': 'c4c:PublicService891912a426cb48118dbdfe169cd38a62',
                 'type': 'Relationship'},
            'http://purl.org/dc/terms/title':
                {'value': 'Start a new project',
                 'type': 'Property'},
            '@context':
                {'c4c': 'http://cefat4cities.crosslang.com/content/'}
        }
        if debug:
            print(json.dumps(self.d_context_broker))

    def test_from_rdf_to_cb(self):
        cb = ItemContextBroker.from_RDF(self.d_cpsv_ap)

        self.assert_equal_json(self.d_context_broker, cb, 'Context broker')

    def test_from_cb_to_rdf(self):
        rdf = ItemRDF.from_context_broker(self.d_context_broker)

        self.assert_equal_json(self.d_cpsv_ap, rdf, 'JSON-LD')

    def test_from_rdf_to_rdf(self):
        cb = ItemContextBroker.from_RDF(self.d_cpsv_ap)
        rdf = ItemRDF.from_context_broker(cb)

        self.assert_equal_json(self.d_cpsv_ap, rdf, 'JSON-LD')

    def test_from_cb_to_cb(self):
        rdf = ItemRDF.from_context_broker(self.d_context_broker)
        cb = ItemContextBroker.from_RDF(rdf)

        self.assert_equal_json(self.d_context_broker, cb, 'Context broker')

    def assert_equal_json(self, j_gt, j_pred, name=''):
        """
        Custom equal assertion for JSON's: consists of Dictionaries, Lists and Strings.
        Args:
            j_gt:
            j_pred:
            name:

        Returns:

        """

        # with self.subTest(name):
        #     self.assertEqual(j_gt, j_pred)

        if isinstance(j_gt, list):
            # List
            with self.subTest(name):
                self.assertIsInstance(j_pred, list)
                self.assertListEqual(j_gt, j_pred)

            if len(j_gt) == len(j_pred):
                for i, (v_gt, v_pred) in enumerate(zip(j_gt, j_pred)):
                    self.assert_equal_json(v_gt, v_pred, f'{name} - {i}')

        elif isinstance(j_gt, dict):
            # Dict
            with self.subTest(name):
                self.assertIsInstance(j_pred, dict)
                self.assertDictEqual(j_gt, j_pred)

            for key, value in j_gt.items():
                self.assert_equal_json(value, j_pred.get(key), f'{name} - {key}')

        else:
            # Other
            with self.subTest(name):
                self.assertEqual(type(j_gt), type(j_pred))
                self.assertEqual(j_gt, j_pred)


class TestConversion2(TestConversion):
    def setUp(self, debug=False) -> None:
        self.d_cpsv_ap = {
            "@id": "http://cefat4cities.crosslang.com/content/ContactPointbf428cc9d6ea47b1acc0b48fb2e1ae7d",
            "@type": ["https://schema.org/ContactPoint"],
            "https://schema.org/email": [{"@value": "E-Mail: foerderungen@ma05.wien.gv.at"}],
            "https://schema.org/hoursAvailable": [{
                "@id": "http://cefat4cities.crosslang.com/content/OpeningHoursSpecificationfeb13cbbbb244309907105951403af44"}],
            "https://schema.org/telephone": [{"@value": "Telefon: +43 1 4000-86528"},
                                             {"@value": "Fax: +43 1 4000-99-86510"}]
        }

        self.d_context_broker = {
            "@context": {
                "c4c": "http://cefat4cities.crosslang.com/content/"
            },
            "@id": "c4c:ContactPointbf428cc9d6ea47b1acc0b48fb2e1ae7d",
            "@type": "https://schema.org/ContactPoint",
            "https://schema.org/email":
                {
                    "value": "E-Mail: foerderungen@ma05.wien.gv.at",
                    "type": "Property"
                }
            ,
            "https://schema.org/hoursAvailable":
                {
                    "object": "c4c:OpeningHoursSpecificationfeb13cbbbb244309907105951403af44",
                    "type": "Relationship"
                }
            ,
            "https://schema.org/telephone":
                {
                    "value": ["Telefon: +43 1 4000-86528", "Fax: +43 1 4000-99-86510"],
                    "type": "Property"
                }

        }
        if debug:
            print(json.dumps(self.d_context_broker))

    def test_from_rdf_to_cb(self):
        super(TestConversion2, self).test_from_rdf_to_cb()


class TestOrionConnector(unittest.TestCase):
    def test_init(self):
        conn = OrionConnector(URL_ORION)
