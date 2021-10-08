import json
import os
import unittest

from c4c_cpsv_ap.connector.hierarchy import Provider
from c4c_cpsv_ap.models import PublicService

FUSEKI_ENDPOINT = os.environ["FUSEKI_ENDPOINT"]
ROOT = os.path.join(os.path.dirname(__file__), '../../..')
FILENAME_DEMO_DATA = os.path.join(ROOT, 'data/examples/demo3.json')
FILENAME_OUT_BASENAME = os.path.join(ROOT, 'data/output/demo_export_v3')

assert os.path.exists(FILENAME_DEMO_DATA)

CONTEXT = 'https://www.wien.gv.at'

URL = 'url'
NAME = 'title'


class TestProviderBuild(unittest.TestCase):

    def setUp(self) -> None:
        self.provider = Provider()

        with open(FILENAME_DEMO_DATA) as json_file:
            self.data = json.load(json_file)

    def test_demo2_data(self):

        keys = self.data[0].keys()

        for key in keys:
            with self.subTest(key):
                # Each/most el is a list (of length 1 or more)
                l = [val for el in self.data for val in el[key]]
                print(l)

    def test_demo2_single(self, debug=True):
        """
        From a JSON build the RDF. Start of an example on how the RDF can be build.

        Args:
            debug (bool): flag to print intermediate steps.
        Returns:

        """

        public_service0 = self.data[0].copy()

        def get_single_el_from_list(l):
            """
            Expects a list with only one element.
            Args:
                l:

            Returns:

            """
            self.assertIsInstance(l, list)
            return l[0]

        with self.subTest('Public service'):
            identifier = get_single_el_from_list(public_service0.pop(URL))
            name = public_service0.pop(NAME)

            public_service = PublicService(description=f'A description of {name}',  # TODO
                                           identifier=identifier,
                                           name=name)
            self.provider.public_services.add(public_service, CONTEXT)

        while public_service0:
            key = list(public_service0)[0]
            value = public_service0.pop(key)

            if debug:
                print(key)

            with self.subTest(key):
                if 0:  # TODO
                    pass
                else:
                    self.fail('Every key element should be implemented.')

        with self.subTest('Export'):

            print(self.provider.graph.serialize(format='pretty-xml'))

            self.provider.graph.serialize(FILENAME_OUT_BASENAME + '.rdf', format='pretty-xml')
            self.provider.graph.serialize(FILENAME_OUT_BASENAME + '.ttl', format='turtle')

        # DEFAULT_PUB_ORG_WIEN = ('Stadt Wien', 'http://publications.europa.eu/resource/authority/atu/AUT_STTS_VIE')
        #
        # known_keys = map_do.keys()
        #
        # with self.subTest('Known keys'):
        #     keys = {key for page in data for key in page.keys()}
        #
        #     self.assertEqual(known_keys, keys, 'Only for the stated keys is known how it has to be processed')
        #
        # url_id = get_homepage(data[0]['url'][0])
        #
        # # Identifier doesn't do much until we connect directly to Fuseki from python
        # g = CPSV_APGraph(identifier=url_id)  # Might be problem in the future if we parse multiple websites at once.
        #
        # for page in data:
        #     url_page = page.get('url')[0]
        #
        #     cp = ContactPoint.from_dict(page)
        #
        #     cp_uri = g.add_contact_point(cp)
        #
        #     if cp_uri:  # Only make sense if it's not none.
        #         g.link_ps_cp(ps_uri=ps.uri,
        #                      cp_uri=cp_uri)
        #
        #     l_terms = page.pop('terms')
        #     g.add_concepts(l_terms, public_service_uri=ps_uri)
        #
        #     l_life_events = page.pop('life_events')
        #     g.add_life_events(l_life_events, public_service_uri=ps_uri)
        #
        #     # Public organisation
        #     preferred_label, loc_uri = d_pub_org_PoC.get(url_page)
        #     if preferred_label is None or loc_uri is None:  # TODO
        #         preferred_label, loc_uri = DEFAULT_PUB_ORG_WIEN
        #
        #     po = PublicOrganization(preferred_label,
        #                             loc_uri)
        #     po_uri = g.add_public_organization(po)
        #     g.link_ps_po(ps_uri, po_uri)
        #
        #     # Unused keys
        #     for k, v in page.items():
        #         print(k, '# TODO')
        #
        #         f = map_do.get(k)
        #         assert f, 'Unknown key'
        #
        #         f(v)
