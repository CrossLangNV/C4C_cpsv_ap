import unittest

from rdflib import Literal, URIRef

from c4c_cpsv_ap.open_linked_data.queries import get_types, TYPE_CONTACT_POINT, TYPE_PUBLICSERVICE, \
    get_contact_points, get_public_services, get_contact_point_info, get_graphs, GRAPH

SPARQL_ENDPOINT = 'http://192.168.105.41:3030/C4C_demo'

GRAPH_URI_EX = 'https://www.wien.gv.at'


class TestTypes(unittest.TestCase):

    def test_find_something(self):
        l_types = get_types(SPARQL_ENDPOINT)

        with self.subTest('Non-empty'):
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

        for k, class_i in zip(('uri', GRAPH),
                              (URIRef, URIRef)):

            with self.subTest(k):
                for l_i in l_cp:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)

        return

    def test_with_graph_uri(self):

        l_cp0 = get_contact_points(SPARQL_ENDPOINT, graph_uri='')

        with self.subTest('Empty'):
            self.assertFalse(l_cp0, 'Should give no results')

        l_cp = get_contact_points(SPARQL_ENDPOINT, graph_uri=GRAPH_URI_EX)

        with self.subTest('Non-empty'):
            self.assertTrue(l_cp, 'Should be non-empty')

        for k, class_i in zip((GRAPH,),
                              (URIRef,)):

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

        l_cp_info_aggr = [d_i for cp_i in l_cp for d_i in get_contact_point_info(SPARQL_ENDPOINT, cp_i['uri'])]

        with self.subTest('Non-empty'):
            self.assertTrue(l_cp_info_aggr, 'Should be non-empty')

        for k, class_i in zip(('uri', 'pred', 'label', GRAPH),
                              (URIRef, URIRef, Literal, URIRef)):

            with self.subTest(k):
                for l_i in l_cp_info_aggr:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)

        set_pred = set(str(d_i.get('pred')) for d_i in l_cp_info_aggr)
        for s in ['email', 'tele', 'hour']:
            with self.subTest(f'Contact info predicate "{s}":'):
                self.assertTrue(any((s in pred_i.lower()) for pred_i in set_pred),
                                f'Pred "{s}" not found in {set_pred}')

    def test_with_graph_uri(self):

        l_cp = get_contact_points(SPARQL_ENDPOINT)

        l_cp_info_aggr0 = [d_i for cp_i in l_cp for d_i in
                           get_contact_point_info(SPARQL_ENDPOINT, cp_i['uri'], graph_uri='')]

        l_cp_info_aggr = [d_i for cp_i in l_cp for d_i in
                          get_contact_point_info(SPARQL_ENDPOINT, cp_i['uri'], graph_uri=GRAPH_URI_EX)]

        del (l_cp)

        with self.subTest('Empty'):
            self.assertFalse(l_cp_info_aggr0, 'Should give no results')

        # l_cp = get_contact_points(SPARQL_ENDPOINT, graph_uri=GRAPH_URI_EX)

        with self.subTest('Non-empty'):
            self.assertTrue(l_cp_info_aggr, 'Should be non-empty')

        for k, class_i in zip((GRAPH,),
                              (URIRef,)):

            with self.subTest(k):
                for l_i in l_cp_info_aggr:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)

        return


class TestGetPublicServices(unittest.TestCase):

    def test_find_something(self):
        l_ps = get_public_services(SPARQL_ENDPOINT)

        with self.subTest('Non-empty'):
            self.assertTrue(l_ps, 'Should be non-empty')

        for k, class_i in zip(('uri', 'title', 'description', GRAPH),
                              (URIRef, Literal, Literal, URIRef)):

            with self.subTest(k):
                for l_i in l_ps:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)

        return

    def test_with_graph_uri(self):

        l_ps0 = get_public_services(SPARQL_ENDPOINT, graph_uri='')

        with self.subTest('Empty'):
            self.assertFalse(l_ps0, 'Should give no results')

        l_ps = get_public_services(SPARQL_ENDPOINT, graph_uri=GRAPH_URI_EX)

        with self.subTest('Non-empty'):
            self.assertTrue(l_ps, 'Should be non-empty')

        for k, class_i in zip((GRAPH,),
                              (URIRef,)):

            with self.subTest(k):
                for l_i in l_ps:
                    self.assertIn(k, l_i.keys())
                    self.assertIsInstance(l_i.get(k), class_i)

        return


class TestGetGraphs(unittest.TestCase):

    def test_find_something(self):
        l_g = get_graphs(SPARQL_ENDPOINT)

        with self.subTest(f'key: {GRAPH}'):
            l_g_uri = [g_i[GRAPH] for g_i in l_g]

        with self.subTest('Non-empty'):
            self.assertTrue(l_g, 'Should be non-empty')

        with self.subTest('Wien'):
            self.assertTrue(any('wien' in g_i.lower() for g_i in l_g_uri), 'Wien is expected to be in the test example')
