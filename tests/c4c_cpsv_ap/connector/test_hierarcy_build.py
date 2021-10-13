import json
import os
import unittest

from c4c_cpsv_ap.connector.hierarchy import Provider, get_single_el_from_list
from c4c_cpsv_ap.models import PublicService, PublicOrganisation

FUSEKI_ENDPOINT = os.environ["FUSEKI_ENDPOINT"]
ROOT = os.path.join(os.path.dirname(__file__), '../../..')
FILENAME_DEMO_DATA = os.path.join(ROOT, 'data/examples/demo3.json')
FILENAME_OUT_BASENAME = os.path.join(ROOT, 'data/output/demo_export_v3')
FILENAME_OUT_CONTEXT_BROKER = os.path.join(ROOT, 'data/output/demo_context_broker.jsonld')

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

    def test_demo2_single(self, debug=True, save=True):
        """
        From a JSON build the RDF. Start of an example on how the RDF can be build.

        Args:
            debug (bool): flag to print intermediate steps.
        Returns:

        """

        public_service0 = self.data[0].copy()

        po = None
        with self.subTest('public_organisation'):

            d_pub_org = public_service0.pop('public_organisation')

            labels = d_pub_org['label']
            spatial_uri = d_pub_org['spatial']
            po = PublicOrganisation(pref_label=labels,
                                    spatial=spatial_uri
                                    )

            po_uri = self.provider.public_organisations.add(po, CONTEXT)

        with self.subTest('Public service'):
            identifier = get_single_el_from_list(public_service0.pop(URL))
            name = public_service0.pop(NAME)

            public_service = PublicService(description=f'A description of {name}',  # TODO
                                           identifier=identifier,
                                           name=name,
                                           has_competent_authority=po)
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

            s = self.provider.graph.serialize(format='pretty-xml')
            if debug:
                print(s)

            if save:
                self.provider.graph.serialize(FILENAME_OUT_BASENAME + '.rdf', format='pretty-xml')
                self.provider.graph.serialize(FILENAME_OUT_BASENAME + '.ttl', format='turtle')
                self.provider.graph.serialize(FILENAME_OUT_BASENAME + '.jsonld', format='json-ld')

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
        #     po = PublicOrganisation(preferred_label,
        #                             loc_uri)
        #     po_uri = g.add_public_organisation(po)
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

    def test_demo_context_broker(self):
        """
        For Fernando Lopez (FiWare) for the Context Broker meeting

        Returns:

        TODO
            * Wien is not added. Debug!
        """

        print("init", len(self.provider.graph))

        # Add Trento
        filename_trento = os.path.join(ROOT, 'data/examples/trento.jsonld')
        context_trento = 'https://www.provincia.tn.it/'
        assert os.path.exists(filename_trento)

        self.provider.graph.parse(filename_trento, publicID=context_trento)

        print("After Trento", len(self.provider.graph))

        # Add Mikkeli
        filename_mikkeli = os.path.join(ROOT, 'data/examples/export.rdf')
        context_mikkeli = 'https://www.mikkeli.fi/'
        assert os.path.exists(filename_mikkeli)
        self.provider.graph.parse(filename_mikkeli, publicID=context_mikkeli)

        print("After Mikkeli", len(self.provider.graph))

        # Add Own
        self.test_demo2_single(debug=False, save=False)

        print("After own", len(self.provider.graph))

        self.provider.graph.serialize(FILENAME_OUT_CONTEXT_BROKER, format='json-ld')
        self.provider.graph.serialize(FILENAME_OUT_CONTEXT_BROKER.rsplit('.', 1)[0] + '.rdf', format='pretty-xml')
