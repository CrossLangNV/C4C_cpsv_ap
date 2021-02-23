import unittest

from c4c_cpsv_ap.connector.rdf_parser import *

SPARQL_ENDPOINT = 'http://gpu1.crosslang.com:3030/C4C_demo'


class TestPublicServicesProvider(unittest.TestCase):
    def setUp(self) -> None:
        """ Initialise a provider

        :return:
        """

        self.provider = SPARQLPublicServicesProvider(SPARQL_ENDPOINT)

    def test_get_public_services(self):
        l_uris = self.provider.get_public_service_uris()

        with self.subTest('Non-empty'):
            self.assertTrue(l_uris)

        with self.subTest('List of string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for uri_i in l_uris:
                self.assertIsInstance(uri_i, str, 'Should be string-like')

    def test_get_relations(self):

        l_relations = self.provider.get_relations()

        with self.subTest('Non-empty'):
            self.assertTrue(l_relations)

        with self.subTest('Known relationships'):
            self.assertEqual(len(l_relations), 3, 'Expected the 3 known relationships.')

        with self.subTest('List of string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for uri_i in l_relations:
                self.assertIsInstance(uri_i, str, 'Should be string-like')

        # Expected relationships
        with self.subTest('Contact points'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            l_filter = list(filter(lambda s: 'contactpoint' in s.lower(), l_relations))

            self.assertTrue(l_filter, 'Should be non-empty')
            self.assertEqual(len(l_filter), 1, 'Only one contact point ref expected')

        # Expected relationships
        with self.subTest('Concepts'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            l_filter = list(filter(lambda s: 'isClassifiedBy'.lower() in s.lower(), l_relations))

            self.assertTrue(l_filter, 'Should be non-empty')
            self.assertEqual(len(l_filter), 1, 'Only one Concepts ref expected')

        # Expected relationships
        with self.subTest('Public Organization'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            l_filter = list(filter(lambda s: 'hasCompetentAuthority'.lower() in s.lower(), l_relations))

            self.assertTrue(l_filter, 'Should be non-empty')
            self.assertEqual(len(l_filter), 1, 'Only one Public Organization ref expected')

        return

    def test_get_contact_points(self):

        l_cp = self.provider.get_contact_points()

        with self.subTest('Non-empty'):
            self.assertTrue(l_cp)

    def test_competent_authorities(self):

        l_ca = self.provider.get_competent_authorities()

        with self.subTest('Non-empty'):
            self.assertTrue(l_ca)
