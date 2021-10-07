import os
import unittest

from rdflib import URIRef

from c4c_cpsv_ap.connector.hierarchy import Harvester, Provider
from c4c_cpsv_ap.models import PublicService

FUSEKI_ENDPOINT = os.environ["FUSEKI_ENDPOINT"]
FILENAME_RDF_DEMO = os.path.join(os.path.dirname(__file__), '../../../data/output/demo2_export.rdf')
assert os.path.exists(FILENAME_RDF_DEMO)

CONTEXT = 'https://www.wien.gv.at'


class TestConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.n = 25
        self.q = f"""
        SELECT ?subject ?predicate ?object
        WHERE {{
            GRAPH ?g {{
                ?subject ?predicate ?object
            }}
        }}
        LIMIT {self.n}
        """

    def test_init_endpoint(self):
        connector = Harvester(
            FUSEKI_ENDPOINT,
        )

        self.assertTrue(connector)

        l = list(connector.query(self.q))

        self.assertTrue(l)
        self.assertEqual(len(l), self.n)

    def test_init_source(self):
        connector = Harvester(
            source=FILENAME_RDF_DEMO,
            graph_uri='https://www.wien.gv.at'
        )

        self.assertTrue(connector)

        l = list(connector.query(self.q))

        self.assertTrue(l)
        self.assertEqual(len(l), self.n)

    def test_init_empty(self):
        connector = Harvester()

        self.assertTrue(connector)

        l = list(connector.query(self.q))

        self.assertEqual(len(l), 0, 'Should be empty')


class TestPublicServices(unittest.TestCase):

    def setUp(self) -> None:
        self.connector = Harvester(
            source=FILENAME_RDF_DEMO,
            graph_uri='https://www.wien.gv.at'
        )

    def test_get_all(self):
        l = self.connector.public_services.get_all()

        self.assertTrue(l, 'Should return Non-empty')

        for a in l:
            self.assertIsInstance(a, URIRef, 'Elements in list have unexpected type.')

    def test_get(self):
        uri_0 = self.connector.public_services.get_all()[0]

        self.assertTrue(uri_0, 'Should return Non-empty')

        public_service = self.connector.public_services.get(uri_0)

        self.assertIsInstance(public_service, PublicService, 'Elements in list have unexpected type.')


class TestPublicServicesProvider(unittest.TestCase):

    def setUp(self) -> None:
        self.provider = Provider(
            source=FILENAME_RDF_DEMO,
            graph_uri=CONTEXT
        )

    def test_add(self):
        public_service = PublicService(description='Test description.',
                                       identifier='Test identifier.',
                                       name='Test name.')

        uri_ps_before = self.provider.public_services.get_all()

        uri_ps = self.provider.public_services.add(public_service, CONTEXT)

        uri_ps_after = self.provider.public_services.get_all()

        self.assertNotIn(uri_ps, uri_ps_before)
        self.assertIn(uri_ps, uri_ps_after)

        with self.subTest('Get'):
            # Expect identical keys

            public_service_get = self.provider.public_services.get(uri_ps)

            self.assertEqual(dict(public_service), dict(public_service_get), 'Should have saved all key values.')

    def test_equivalent(self):
        harvest = Harvester(FUSEKI_ENDPOINT)

        l_prov = self.provider.public_services.get_all()
        l_harv = harvest.public_services.get_all()

        self.assertListEqual(l_prov, l_harv, 'Should return same content.')
