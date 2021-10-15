import json
import os
import unittest
from typing import List

from c4c_cpsv_ap.connector.hierarchy import Provider, get_single_el_from_list
from c4c_cpsv_ap.models import PublicService, PublicOrganisation, BusinessEvent, _id_generator, Concept, ContactPoint, \
    LifeEvent

FUSEKI_ENDPOINT = os.environ["FUSEKI_ENDPOINT"]
ROOT = os.path.join(os.path.dirname(__file__), '../../..')
FILENAME_DEMO_DATA_V2 = os.path.join(ROOT, 'data/examples/demo2.json')
FILENAME_DEMO_DATA = os.path.join(ROOT, 'data/examples/demo3.json')
FILENAME_OUT_BASENAME = os.path.join(ROOT, 'data/output/demo_export_v3')
FILENAME_OUT_CONTEXT_BROKER = os.path.join(ROOT, 'data/output/demo_context_broker.jsonld')

for filename in [FILENAME_DEMO_DATA_V2,
                 FILENAME_DEMO_DATA]:
    assert os.path.exists(filename)

CONTEXT = 'https://www.wien.gv.at'

URL = 'url'
NAME = 'title'
DESCRIPTION = 'description'
TERMS = "terms"


class TestProviderBuild(unittest.TestCase):

    def setUp(self) -> None:
        self.provider = Provider()

        with open(FILENAME_DEMO_DATA) as json_file:
            self.data = json.load(json_file)

    def test_demo2_data(self):
        with open(FILENAME_DEMO_DATA_V2) as json_file:
            self.data = json.load(json_file)

        keys = self.data[0].keys()

        for key in keys:
            with self.subTest(key):
                # Each/most el is a list (of length 1 or more)

                l = []
                for el in self.data:
                    val = el[key]

                    if isinstance(val, list):
                        l += val

                    else:
                        l.append(val)

                # l = [val for el in self.data for val in el[key]]
                print(l)

    def test_demo3_single(self, debug=True, save=True):
        """
        From a JSON build the RDF. Start of an example on how the RDF can be build.

        Args:
            debug (bool): flag to print intermediate steps.
        Returns:

        """

        data0 = self.data[0].copy()

        def get_po() -> PublicOrganisation:
            with self.subTest('public_organisation'):
                d_pub_org = data0.pop('public_organisation')

                labels = d_pub_org['label']
                spatial = d_pub_org['spatial']
                spatial_uri = spatial["uri"]
                po = PublicOrganisation(pref_label=labels,
                                        spatial=spatial_uri
                                        )

                po_uri = self.provider.public_organisations.add(po, CONTEXT)
                return po

        def get_business_events() -> List[BusinessEvent]:
            l_business_event = []
            with self.subTest('Business Events'):
                names = data0.pop("business_events")

                for name in names:
                    business_event = BusinessEvent(identifier=_id_generator(),  # TODO
                                                   name=name)
                    l_business_event.append(business_event)

            return l_business_event

        def get_life_events() -> List[LifeEvent]:
            l_life_event = []
            with self.subTest('Life Events'):
                names = data0.pop("life_events")

                for name in names:
                    life_event = LifeEvent(identifier=_id_generator(),  # TODO
                                           name=name)
                    l_life_event.append(life_event)

            return l_life_event

        def get_concepts():
            terms = data0.pop(TERMS)
            l_concepts = []
            for term in terms:
                concept = Concept(pref_label=term)
                l_concepts.append(concept)
            return l_concepts

        def get_contact_point() -> List[ContactPoint]:

            email = data0.pop("emails")
            telephone = data0.pop("phone")
            opening_hours = data0.pop("opening_hours")

            contact_point = ContactPoint(email=email,
                                         telephone=telephone,
                                         opening_hours=opening_hours)

            return [contact_point]

        def get_public_service(public_org,
                               l_concepts: List[Concept],
                               l_business_event,
                               l_life_event,
                               l_contact_point: List[ContactPoint]):
            with self.subTest("Public service"):
                identifier = get_single_el_from_list(data0.pop(URL))
                name = data0.pop(NAME)
                description = data0.pop(DESCRIPTION)

                public_service = PublicService(description=description,  # TODO
                                               identifier=identifier,
                                               name=name,
                                               has_competent_authority=public_org,
                                               is_classified_by=l_concepts,
                                               is_grouped_by=l_business_event + l_life_event,
                                               has_contact_point=l_contact_point
                                               )
                self.provider.public_services.add(public_service, CONTEXT)

                return public_service

        po = get_po()

        l_business_event = get_business_events()
        l_life_event = get_life_events()

        l_concepts = get_concepts()

        l_contact_point = get_contact_point()

        public_service = get_public_service(public_org=po,
                                            l_concepts=l_concepts,
                                            l_business_event=l_business_event,
                                            l_life_event=l_life_event,
                                            l_contact_point=l_contact_point
                                            )

        while data0:
            key = list(data0)[0]
            value = data0.pop(key)

            if debug:
                print(key)

            with self.subTest(key):
                if 0:  # TODO
                    pass
                else:
                    self.fail("Every key element should be implemented.")

        with self.subTest("Export"):

            s = self.provider.graph.serialize(format="pretty-xml")
            if debug:
                print(s)

            if save:
                self.provider.graph.serialize(FILENAME_OUT_BASENAME + ".rdf", format="pretty-xml")
                self.provider.graph.serialize(FILENAME_OUT_BASENAME + ".ttl", format="turtle")
                self.provider.graph.serialize(FILENAME_OUT_BASENAME + ".jsonld", format="json-ld")

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
        self.test_demo3_single(debug=False, save=False)

        print("After own", len(self.provider.graph))

        self.provider.graph.serialize(FILENAME_OUT_CONTEXT_BROKER, format='json-ld')
        self.provider.graph.serialize(FILENAME_OUT_CONTEXT_BROKER.rsplit('.', 1)[0] + '.rdf', format='pretty-xml')
