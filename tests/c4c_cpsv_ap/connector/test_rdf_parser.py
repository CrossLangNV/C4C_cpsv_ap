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

        with self.subTest('List with dicts with URI'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_cp:
                self.assertIsInstance(d_i.get(URI), str, 'Should be string-like')

        with self.subTest('List with dicts with LABEL that are string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_cp:
                self.assertIsInstance(d_i.get(LABEL), str, 'Would be nice if there is a string representation')

    def test_competent_authorities(self):

        l_ca = self.provider.get_competent_authorities()

        with self.subTest('Non-empty'):
            self.assertTrue(l_ca)

        with self.subTest('List with dicts with URI'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_ca:
                self.assertIsInstance(d_i.get(URI), str, 'Should be string-like')

        with self.subTest('List with dicts with LABEL that are string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_ca:
                self.assertIsInstance(d_i.get(LABEL), str, 'Should be string-like')

    def test_get_concepts(self):

        l_c = self.provider.get_concepts()

        with self.subTest('Non-empty'):
            self.assertTrue(l_c)

        with self.subTest('List with dicts with URI'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_c:
                self.assertIsInstance(d_i.get(URI), str, 'Should be string-like')

        with self.subTest('List with dicts with LABEL that are string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_c:
                self.assertIsInstance(d_i.get(LABEL), str, 'Should be string-like')

    def test_get_public_service_uris_filter(self):

        with self.subTest('Equivalence'):
            l_ps = self.provider.get_public_service_uris_filter()

            l_ps_baseline = self.provider.get_public_service_uris()

            self.assertEqual(l_ps, l_ps_baseline)

        with self.subTest('Filter concepts'):
            l_c = self.provider.get_concepts()
            l_c_labels = list(map(str, [l_c_i.get(LABEL) for l_c_i in l_c]))

            # Wirtschaft is used by all?
            # Kindergruppenbetreuungspersonen seems fine
            l_c_label_i = l_c_labels[-1]

            l_ps = self.provider.get_public_service_uris_filter(filter_concepts=l_c_label_i)
            l_ps_list = self.provider.get_public_service_uris_filter(filter_concepts=[l_c_label_i])

            self.assertGreaterEqual(len(l_ps), 1, 'Should be non-empty.')
            self.assertEqual(l_ps, l_ps_list, 'Both single value and list should work.')

        with self.subTest('Filter public organizations'):
            l_po = self.provider.get_competent_authorities()
            l_po_labels = list(map(str, [l_po_i.get(LABEL) for l_po_i in l_po]))

            l_po_label_i = l_po_labels[-1]

            l_ps = self.provider.get_public_service_uris_filter(filter_public_organization=l_po_label_i)
            l_ps_list = self.provider.get_public_service_uris_filter(filter_public_organization=[l_po_label_i])

            self.assertGreaterEqual(len(l_ps), 1, 'Should be non-empty.')
            self.assertEqual(l_ps, l_ps_list, 'Both single value and list should work.')

        with self.subTest('Filter contact points'):
            l_cp = self.provider.get_contact_points()
            l_cp_uris = list(map(str, [l_cp_i.get(URI) for l_cp_i in l_cp]))

            l_cp_uri_i = l_cp_uris[-1]

            l_ps = self.provider.get_public_service_uris_filter(filter_contact_point=l_cp_uri_i)
            l_ps_list = self.provider.get_public_service_uris_filter(filter_contact_point=[l_cp_uri_i])

            self.assertGreaterEqual(len(l_ps), 1, 'Should be non-empty.')
            self.assertEqual(l_ps, l_ps_list, 'Both single value and list should work.')

        return


class TestContactPointProvider(unittest.TestCase):
    def setUp(self) -> None:
        """ Initialise a provider

        :return:
        """

        self.provider = SPARQLContactPointProvider(SPARQL_ENDPOINT)

    def test_get_contact_point(self):
        l_uris = self.provider.get_contact_point_uris()

        with self.subTest('Non-empty'):
            self.assertTrue(l_uris)

        with self.subTest('List of string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for uri_i in l_uris:
                self.assertIsInstance(uri_i, str, 'Should be string-like')

    def test_get_contact_point_info(self):

        l_uris = self.provider.get_contact_point_uris()
        uri_i = l_uris[0]

        for uri_i in [l_uris[0],
                      l_uris[1]]:

            l = self.provider.get_contact_point_info(uri_i)

            with self.subTest('Retrieve URI in each element'):

                for d_i in l:
                    self.assertEqual(str(d_i.get(URI)), str(uri_i))

            with self.subTest('subjects'):
                self.assertTrue(any(map(lambda d: d.get(SUBJ), l)))

            with self.subTest('objects'):
                self.assertTrue(any(map(lambda d: d.get(OBJ), l)))

        return

    def test_get_public_services(self):
        l_ps = self.provider.get_public_services()

        with self.subTest('Non-empty'):
            self.assertTrue(l_ps)

        with self.subTest('List with dicts with URI'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_ps:
                self.assertIsInstance(d_i.get(URI), str, 'Should be string-like')

        with self.subTest('List with dicts with LABEL that are string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            for d_i in l_ps:
                self.assertIsInstance(d_i.get(LABEL), str, 'Should be string-like')
