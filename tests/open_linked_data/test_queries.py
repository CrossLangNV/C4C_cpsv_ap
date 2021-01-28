import unittest
from rdflib import Literal, URIRef
from c4c_cpsv_ap.open_linked_data.queries import get_types, TYPE_CONTACT_POINT, TYPE_PUBLICSERVICE,\
    get_contact_points, get_public_services, get_contact_point_info

SPARQL_ENDPOINT = 'http://192.168.105.41:3030/C4C_demo'


class TestTypes(unittest.TestCase):

    def test_find_something(self):
        l_types = get_types(SPARQL_ENDPOINT)

        with self.subTest('Non-emptsy'):
            self.assertTrue(l_types, 'Should be non-empty')

        with self.subTest('Event'):
            self.assertTrue(any([('event' in type_i.lower()) for type_i in l_types]),
                            "Couldn't find a type related to events")

        with self.subTest('Contact point'):
            self.assertIn(str(TYPE_CONTACT_POINT), list(map(str, l_types)), "Couldn't find the 'contact point' type")

        with self.subTest('Public service'):
            self.assertIn(str(TYPE_PUBLICSERVICE), map(str, l_types), "Couldn't find the 'public service' type")




class TestGetContactPoints(unittest.TestCase):

    def test_find_something(self):
        l_cp = get_contact_points(SPARQL_ENDPOINT)

        with self.subTest('Non-empty'):
            self.assertTrue(l_cp, 'Should be non-empty')

        for k, class_i  in zip(('uri', ),
                       (URIRef, )):

            with self.subTest(k):
                for l_i in l_cp:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)

        return


class TestGetContactPointInfo(unittest.TestCase):
    def test_find_something(self):
        """

        :return:
        """
        l_cp = get_contact_points(SPARQL_ENDPOINT)

        # First element of all contact points and first element to get URI to CP.
        cp_0 = l_cp[0]['uri']

        l_cp_info = get_contact_point_info(SPARQL_ENDPOINT, cp_0)

        with self.subTest('Non-empty'):
            self.assertTrue(l_cp_info, 'Should be non-empty')

        for k, class_i  in zip(('uri', 'pred', 'label'),
                       (URIRef, URIRef, Literal)):

            with self.subTest(k):
                for l_i in l_cp_info:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)



class TestGetPublicServices(unittest.TestCase):

    def test_find_something(self):
        l_ps = get_public_services(SPARQL_ENDPOINT)

        with self.subTest('Non-empty'):
            self.assertTrue(l_ps, 'Should be non-empty')

        # with self.subTest('uri, title, description type'):
        #
        #     for (uri, title, description) in l_ps:
        #         self.assertIsInstance(str(uri), str, 'Should be equivalent to strings')
        #         self.assertIsInstance(str(title), str, 'Should be equivalent to strings')
        #         self.assertIsInstance(str(description), str, 'Should be equivalent to strings')

        for k, class_i  in zip(('uri', 'title', 'description'),
                       (URIRef, Literal, Literal )):

            with self.subTest(k):
                for l_i in l_ps:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)

        return
#         with self.subTest('Event'):
#             self.assertTrue(any([('event' in type_i.lower()) for type_i in l_types]),
#                             "Couldn't find a type related to events")
#
#         with self.subTest('Contact point'):
#             self.assertIn(str(TYPE_CONTACT_POINT), list(map(str, l_types)), "Couldn't find the 'contact point' type")
#
#         with self.subTest('Public service'):
#             self.assertIn(str(TYPE_PUBLICSERVICE), map(str, l_types), "Couldn't find the 'public service' type")
