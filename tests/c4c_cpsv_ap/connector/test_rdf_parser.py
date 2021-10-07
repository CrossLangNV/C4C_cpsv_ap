import unittest

from SPARQLWrapper.Wrapper import POST
from rdflib.term import Literal, URIRef

from c4c_cpsv_ap.connector.rdf_parser import SPARQLConnector, SPARQLPublicServicesProvider, SPARQLContactPointProvider, \
    SUBJ, OBJ, URI, LABEL

SPARQL_ENDPOINT = 'http://gpu1.crosslang.com:3030/C4C_demo/query'
# SPARQL_ENDPOINT = 'https://django.cefat4cities.crosslang.com/cpsv/api/dataset'


class TestSPARQLConnector(unittest.TestCase):
    def setUp(self) -> None:
        """ Initialise a provider

        :return:
        """

        self.provider = SPARQLConnector(SPARQL_ENDPOINT)

    def test_get_triples(self):
        n = 25
        q = f"""
        SELECT ?subject ?predicate ?object
        WHERE {{
          ?subject ?predicate ?object
        }}
        LIMIT {n}
        """

        l = self.provider.query(q)

        self.assertEqual(len(l), n, "Number of returned triples is unexpected.")


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

        with self.subTest('WARNING NOT YET IMPLEMENTED List with dicts with LABEL that are string-likes'):
            # Check if elements can be string casted.
            # Probably not the most reliable test as a lot of types can be cast to string.

            cp_prov = SPARQLContactPointProvider(SPARQL_ENDPOINT)

            for d_i in l_cp:
                url = d_i[URI]
                info = cp_prov.get_contact_point_info(url)

                self.assertIsInstance(d_i.get(LABEL), str,
                                      'WARNING NOT YET IMPLEMENTED Would be nice if there is a string representation')

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

        with self.subTest('Equivalence len'):
            l_ps = self.provider.get_public_service_uris_filter()
            l_ps_baseline = self.provider.get_public_service_uris()

            self.assertEqual(len(l_ps), len(l_ps_baseline))

        with self.subTest('Equivalence'):
            l_ps = self.provider.get_public_service_uris_filter()
            l_ps_baseline = self.provider.get_public_service_uris()

            self.assertListEqual(l_ps, l_ps_baseline)

    def test_get_public_service_uris_filter_concept(self):
        l_c = self.provider.get_concepts()
        l_c_labels = list(map(str, [l_c_i.get(LABEL) for l_c_i in l_c]))

        # Wirtschaft is used by all?
        # Kindergruppenbetreuungspersonen seems fine
        l_c_label_i = l_c_labels[-1]

        l_ps = self.provider.get_public_service_uris_filter(filter_concepts=l_c_label_i)
        l_ps_list = self.provider.get_public_service_uris_filter(filter_concepts=[l_c_label_i])

        self.assertGreaterEqual(len(l_ps), 1, 'Should be non-empty.')
        self.assertEqual(l_ps, l_ps_list, 'Both single value and list should work.')

    def test_get_public_service_uris_filter_pub_organization(self):

        l_po = self.provider.get_competent_authorities()
        l_po_labels = list(map(str, [l_po_i.get(LABEL) for l_po_i in l_po]))

        l_po_label_i = l_po_labels[-1]

        l_ps = self.provider.get_public_service_uris_filter(filter_public_organization=l_po_label_i)
        l_ps_list = self.provider.get_public_service_uris_filter(filter_public_organization=[l_po_label_i])

        self.assertGreaterEqual(len(l_ps), 1, 'Should be non-empty.')
        self.assertEqual(l_ps, l_ps_list, 'Both single value and list should work.')

    def test_get_public_service_uris_filter_contact_points(self):
        l_cp = self.provider.get_contact_points()
        l_cp_uris = list(map(str, [l_cp_i.get(URI) for l_cp_i in l_cp]))

        l_cp_uri_i = l_cp_uris[-1]

        l_ps = self.provider.get_public_service_uris_filter(filter_contact_point=l_cp_uri_i)
        l_ps_list = self.provider.get_public_service_uris_filter(filter_contact_point=[l_cp_uri_i])

        self.assertGreaterEqual(len(l_ps), 1, 'Should be non-empty.')
        self.assertEqual(l_ps, l_ps_list, 'Both single value and list should work.')


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

    def test_get_contact_point_uris_filter(self):

        with self.subTest('Equivalence len'):
            l_cp = self.provider.get_contact_point_uris_filter()
            l_cp_baseline = self.provider.get_contact_point_uris()

            self.assertEqual(len(l_cp), len(l_cp_baseline))

        with self.subTest('Equivalence'):
            l_cp = self.provider.get_contact_point_uris_filter()
            l_cp_baseline = self.provider.get_contact_point_uris()

            self.assertEqual(l_cp, l_cp_baseline)

        with self.subTest('Filter public services'):
            l_ps = self.provider.get_public_services()
            l_ps_labels = list(map(str, [l_ps_i.get(LABEL) for l_ps_i in l_ps]))

            l_ps_label_i = l_ps_labels[-1]

            l_cp = self.provider.get_contact_point_uris_filter(filter_public_service=l_ps_label_i)
            l_cp_list = self.provider.get_contact_point_uris_filter(filter_public_service=[l_ps_label_i])

            self.assertGreaterEqual(len(l_cp), 1, 'Should be non-empty.')
            self.assertEqual(l_cp, l_cp_list, 'Both single value and list should work.')

        return


class TestReadOnly(unittest.TestCase):
    SUB = 'www.test.com'
    PRED = 'www.test.com/pred'
    OBJECT = 'a website'

    def setUp(self) -> None:
        """ Initialise a provider

        :return:
        """

        if 0:
            # TODO we might work with a separate page to protect Fuseki from outside.
            agent = {'Bearer': 'OERthRgu7kpJ6gCVXhPw3pDSpEeCCm'}
            endpoint = 'https://django.cefat4cities.crosslang.com/cpsv/api/dataset'
        elif 0:
            endpoint = 'http://gpu1.crosslang.com:3030/C4C_demo/query'

        else:
            endpoint = SPARQL_ENDPOINT

        self.provider = SPARQLConnector(endpoint)

    def test_read(self):
        """
        Is allowed

        :return:
        """

        q = """
        SELECT ?graph ?subject ?predicate ?object
        WHERE {
          GRAPH ?graph {
          ?subject ?predicate ?object
          }
        }
        LIMIT 25
        """

        r = self.provider.query(q)

        self.assertTrue(len(r), 'Should return some results')

        return

    def test_update(self):
        """
        Is not allowed

        :return:
        """

        q = f"""
            SELECT ?graph ?subject ?predicate ?object
            WHERE {{
                VALUES ?subject {{ {URIRef(self.SUB).n3()} }}
                VALUES ?predicate {{ {URIRef(self.PRED).n3()} }}
                VALUES ?object {{ {Literal(self.OBJECT).n3()} }}
                VALUES ?graph {{ {URIRef(self.PRED).n3()} }}
                GRAPH ?graph {{
                ?subject ?predicate ?object
                }}
            }}
            LIMIT 25
        """

        r = self.provider.query(q)

        with self.subTest('Sanity check'):
            self.assertFalse(len(r), 'Triple should not exist yet!')

        q_insert = f"""
        INSERT DATA {{ 
            GRAPH {URIRef(self.PRED).n3()} {{
                {URIRef(self.SUB).n3()} {URIRef(self.PRED).n3()} {Literal(self.OBJECT).n3()}
            }}
        }}
        """

        try:
            self.provider.sparql.setMethod(POST)
            self.provider.sparql.setQuery(q_insert)
            r = self.provider.sparql.query()
            results = r.convert().decode()

            with self.subTest('Fail to update'):
                self.assertNotIn('succ', results.lower(), 'Should not have succeeded!')

        except Exception as e:
            with self.subTest('Fail to update'):
                print(e)
        else:
            with self.subTest('Update response'):
                print(results)

        finally:
            r = self.provider.query(q)

            with self.subTest('Still empty after trying to add'):
                self.assertFalse(len(r), 'Triple should not exist yet!')

    def test_remove(self):
        """
        Is not allowed

        :return:
        """

        q_remove = f"""
        DELETE DATA {{ 
            GRAPH {URIRef(self.SUB).n3()} {{
                {URIRef(self.SUB).n3()} {URIRef(self.PRED).n3()} {Literal(self.OBJECT).n3()}
            }}
        }}
        """

        b = self._check_exists(self.SUB,
                               self.PRED,
                               self.OBJECT,
                               self.SUB)

        with self.subTest('Sanity check'):
            self.assertTrue(b, 'This test triple should exist already!')

        try:

            self.provider.sparql.setMethod(POST)
            self.provider.sparql.setQuery(q_remove)
            r = self.provider.sparql.query()
            results = r.convert().decode()

            with self.subTest('Fail to update'):
                self.assertNotIn('succ', results.lower(), 'Should not have succeeded!')

        except Exception as e:
            with self.subTest('Fail to update'):
                print(e)
        else:
            with self.subTest('Update response'):
                print(results)

        finally:

            b = self._check_exists(self.SUB,
                                   self.PRED,
                                   self.OBJECT,
                                   self.SUB)

            with self.subTest('Still exist after trying to remove.'):
                self.assertTrue(len(b), 'Triple should still exist.')

    def _check_exists(self, sub, pred, obj, graph):
        q = f"""
            SELECT ?graph ?subject ?predicate ?object
            WHERE {{
                VALUES ?subject {{ {URIRef(sub).n3()} }}
                VALUES ?predicate {{ {URIRef(pred).n3()} }}
                VALUES ?object {{ {Literal(obj).n3()} }}
                VALUES ?graph {{ {URIRef(graph).n3()} }}
                GRAPH ?graph {{
                    ?subject ?predicate ?object
                }}
            }}
            LIMIT 25
        """

        r = self.provider.query(q)

        return r
