import os
import unittest

from rdflib import URIRef

from c4c_cpsv_ap.connector.hierarchy import Provider
from c4c_cpsv_ap.models import PublicService

FUSEKI_ENDPOINT = os.environ["FUSEKI_ENDPOINT"]


class TestConnector(unittest.TestCase):
    def test_init(self):
        connector = Provider(FUSEKI_ENDPOINT)

        self.assertEqual(0, 1)


class TestPublicServices(unittest.TestCase):

    def setUp(self) -> None:
        self.connector = Provider(FUSEKI_ENDPOINT)

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
