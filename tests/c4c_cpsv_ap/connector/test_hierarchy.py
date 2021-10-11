import abc
import os
import unittest

from rdflib import URIRef

from c4c_cpsv_ap.connector.hierarchy import Harvester, Provider, SubHarvester, SubProvider
from c4c_cpsv_ap.models import PublicService, Concept, CPSVAPModel

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


class AbstractTestModels(abc.ABC):

    def setUp(self) -> None:
        self.harvester = SubHarvester()

    @abc.abstractmethod
    def test_get_all(self):
        self.harvester.get_all()

    @abc.abstractmethod
    def test_get(self):
        self.harvester.get()


class AbstractTestModelsProvider(abc.ABC):

    def setUp(self) -> None:
        self.provider = SubProvider()

    @abc.abstractmethod
    def test_equivalent(self):
        harvest = SubHarvester()

        l_prov = self.provider.get_all()
        l_harv = harvest.get_all()

        self.assertListEqual(l_prov, l_harv, 'Should return same content.')

    @abc.abstractmethod
    def test_add(self):
        obj = CPSVAPModel()

        uri_before = self.provider.get_all()

        uri = self.provider.add(obj, CONTEXT)

        uri_after = self.provider.get_all()

        self.assertNotIn(uri, uri_before)
        self.assertIn(uri, uri_after)

        with self.subTest('Get'):
            # Expect identical keys

            obj_get = self.provider.get(uri)

            self.assertDictEqual(dict(obj), dict(obj_get), 'Should have saved all key values.')

    @abc.abstractmethod
    def test_delete(self):
        n_before = len(self.provider.provider.graph)

        obj = CPSVAPModel()

        uri = self.provider.add(obj, CONTEXT)
        with self.subTest('Add method (Sanity check)'):
            n_during = len(self.provider.provider.graph)
            self.assertGreater(n_during, n_before,
                               'Should have increased number of triples, make sure *add* method works.')

        with self.subTest('Delete method'):
            self.provider.delete(uri, CONTEXT)

        n_after = len(self.provider.provider.graph)

        with self.subTest("Restore to previous state"):
            self.assertEqual(n_before, n_after, 'Should restore to previous number of triples')


class AbstractTestModelsProviderUpdate(abc.ABC):
    obj_old = CPSVAPModel()
    obj_old2 = CPSVAPModel()
    obj_new = CPSVAPModel()
    obj_new2 = CPSVAPModel()

    def setUp(self) -> None:
        self.provider = SubProvider()

    @abc.abstractmethod
    def test_update(self):
        """
        Returns:

        """

        self.shared_test(self.obj_old, self.obj_new)

    @abc.abstractmethod
    def test_update_more_info(self):
        """
        Returns:

        """

        self.shared_test(self.obj_old, self.obj_new2)

    @abc.abstractmethod
    def test_update_less_info(self):
        """
        Test the update of a public service method
        Returns:

        """

        self.shared_test(self.obj_old2, self.obj_new)

    @abc.abstractmethod
    def test_update_add_remove(self):
        self.shared_test(self.obj_old2, self.obj_new2)

    @abc.abstractmethod
    def shared_test(self, obj_old: CPSVAPModel, obj_new: CPSVAPModel):
        uri = self.provider.add(obj_old, CONTEXT)

        with self.subTest('Sanity check'):
            r_old = self.provider.get(uri)
            self.assertDictEqual(dict(obj_old), dict(r_old))

        self.provider.update(obj_new, uri, CONTEXT)
        r = self.provider.get(uri)

        with self.subTest('Updated'):
            self.assertDictEqual(dict(obj_new), dict(r))


class TestConcepts(unittest.TestCase, AbstractTestModels):

    def setUp(self) -> None:
        """
        Set up
        """
        self.connector = Harvester(
            source=FILENAME_RDF_DEMO,
            graph_uri='https://www.wien.gv.at'
        )

    def test_get_all(self):
        l = self.connector.concepts.get_all()

        with self.subTest('Non-empty'):
            self.assertTrue(l, 'Should return Non-empty')

        with self.subTest('Type'):
            for a in l:
                self.assertIsInstance(a, URIRef, 'Elements in list have unexpected type.')

    def test_get(self):
        uri_0 = self.connector.concepts.get_all()[0]

        with self.subTest('Sanity check'):
            self.assertTrue(uri_0, 'Should return Non-empty')

        concept = self.connector.concepts.get(uri_0)

        with self.subTest('Type'):
            self.assertIsInstance(concept, Concept, 'Elements in list have unexpected type.')


class TestConceptsProvider(unittest.TestCase, AbstractTestModelsProvider):
    def test_equivalent(self):
        self.assertEqual(0, 1)

    def test_add(self):
        self.assertEqual(0, 1)

    def test_delete(self):
        self.assertEqual(0, 1)


class TestConceptsProviderUpdate(unittest.TestCase, AbstractTestModelsProviderUpdate):
    def test_update(self):
        self.assertEqual(0, 1)

    def test_update_more_info(self):
        self.assertEqual(0, 1)

    def test_update_less_info(self):
        self.assertEqual(0, 1)

    def test_update_add_remove(self):
        self.assertEqual(0, 1)

    def shared_test(self, obj_old: CPSVAPModel, obj_new: CPSVAPModel):
        self.assertEqual(0, 1)


class TestPublicServices(unittest.TestCase, AbstractTestModels):

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


class TestPublicServicesProvider(unittest.TestCase, AbstractTestModelsProvider):

    def setUp(self) -> None:
        self.provider = Provider(
            source=FILENAME_RDF_DEMO,
            graph_uri=CONTEXT
        )

    def test_equivalent(self):
        harvest = Harvester(FUSEKI_ENDPOINT)

        l_prov = self.provider.public_services.get_all()
        l_harv = harvest.public_services.get_all()

        self.assertListEqual(l_prov, l_harv, 'Should return same content.')

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

            self.assertDictEqual(dict(public_service), dict(public_service_get), 'Should have saved all key values.')

    def test_add2(self):
        concept0 = Concept(pref_label='Test concept 0')
        concept1 = Concept(pref_label='Test concept 1')

        public_service = PublicService(description='Test description.',
                                       identifier='Test identifier.',
                                       name='Test name.',
                                       keyword=['Test keyword'],
                                       classified_by=[concept0, concept1],
                                       )

        uri_ps_before = self.provider.public_services.get_all()

        uri_ps = self.provider.public_services.add(public_service, CONTEXT)

        uri_ps_after = self.provider.public_services.get_all()

        self.assertNotIn(uri_ps, uri_ps_before)
        self.assertIn(uri_ps, uri_ps_after)

        with self.subTest('Get'):
            # Expect identical keys

            public_service_get = self.provider.public_services.get(uri_ps)

            self.assertDictEqual(dict(public_service), dict(public_service_get), 'Should have saved all key values.')

        with self.subTest('Export single'):
            FILENAME_SINGLE = os.path.join(os.path.dirname(__file__), '../../../data/output/single_test.ttl')

            self.provider.graph.serialize(FILENAME_SINGLE, format='turtle')

    def test_delete(self):
        n_before = len(self.provider.graph)

        public_service = PublicService(description='Delete this description.',
                                       identifier='Delete this identifier.',
                                       name='Delete this name.')

        uri_ps = self.provider.public_services.add(public_service, CONTEXT)
        with self.subTest('Add method (Sanity check)'):
            n_during = len(self.provider.graph)
            self.assertGreater(n_during, n_before,
                               'Should have increased number of triples, make sure *add* method works.')

        with self.subTest('Delete method'):
            self.provider.public_services.delete(uri_ps, CONTEXT)

        n_after = len(self.provider.graph)

        with self.subTest("Restore to previous state"):
            self.assertEqual(n_before, n_after, 'Should restore to previous number of triples')


class TestPublicServicesProviderUpdate(unittest.TestCase, AbstractTestModelsProviderUpdate):
    public_service_old = PublicService(description='Old test description.',
                                       identifier='Old test identifier.',
                                       name='Old test name.')

    public_service_old_2 = PublicService(description='Old test description.',
                                         identifier='Old test identifier.',
                                         name='Old test name.',
                                         classified_by=[Concept(pref_label='Old test term')])

    public_service_new = PublicService(description='New test description.',
                                       identifier='New test identifier.',
                                       name='New test name.')

    public_service_new_2 = PublicService(description='New test description.',
                                         identifier='New test identifier.',
                                         name='New test name.',
                                         keyword=['This is new']
                                         )

    def setUp(self) -> None:
        self.provider = Provider(
            source=FILENAME_RDF_DEMO,
            graph_uri=CONTEXT
        )

    def test_update(self):
        """
        Test the update of a public service method
        Returns:

        """

        self.shared_test(self.public_service_old, self.public_service_new)

    def test_update_more_info(self):
        """
        Test the update of a public service method
        Returns:

        """

        self.shared_test(self.public_service_old, self.public_service_new_2)

    def test_update_less_info(self):
        """
        Test the update of a public service method
        Returns:

        """

        self.shared_test(self.public_service_old_2, self.public_service_new)

    def test_update_add_remove(self):
        self.shared_test(self.public_service_old_2, self.public_service_new_2)

    def shared_test(self, ps_old: PublicService, ps_new: PublicService):
        uri = self.provider.public_services.add(ps_old, CONTEXT)

        with self.subTest('Sanity check'):
            r_old = self.provider.public_services.get(uri)
            self.assertDictEqual(dict(ps_old), dict(r_old))

        self.provider.public_services.update(ps_new, uri, CONTEXT)
        r = self.provider.public_services.get(uri)

        with self.subTest('Updated'):
            self.assertDictEqual(dict(ps_new), dict(r))
