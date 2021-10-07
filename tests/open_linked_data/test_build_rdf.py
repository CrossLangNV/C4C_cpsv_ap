import json
import os
import unittest
from urllib.parse import urlsplit, urlunsplit

from rdflib.term import Literal

from c4c_cpsv_ap.open_linked_data.build_rdf import CPSV_APGraph
from c4c_cpsv_ap.open_linked_data.node import ContactPoint, PublicOrganization, PublicService
from data.examples.PoC_public_organisation import d_pub_org_PoC


class TestOpenRawData(unittest.TestCase):
    def test_example_json(self):
        """ Open test data for further processing

        :return:
        """

        PATH_EXAMPLE = os.path.join(os.path.dirname(__file__), 'tmp/demo2.json')
        PATH_EXPORT = os.path.join(os.path.dirname(__file__), 'tmp/demo2_export.rdf')

        with open(PATH_EXAMPLE) as json_file:
            data = json.load(json_file)

        def foo(l, *args, **kwargs):
            return

        map_do = {'url': foo,
                  'life_events': foo,
                  'terms': foo,
                  'phone': foo,
                  'emails': foo,
                  'opening_hours': foo,
                  'pdf': foo,
                  'title': foo}

        DEFAULT_PUB_ORG_WIEN = ('Stadt Wien', 'http://publications.europa.eu/resource/authority/atu/AUT_STTS_VIE')

        known_keys = map_do.keys()

        with self.subTest('Known keys'):
            keys = {key for page in data for key in page.keys()}

            self.assertEqual(known_keys, keys, 'Only for the stated keys is known how it has to be processed')

        url_id = get_homepage(data[0]['url'][0])

        # Identifier doesn't do much until we connect directly to Fuseki from python
        g = CPSV_APGraph(identifier=url_id)  # Might be problem in the future if we parse multiple websites at once.

        for page in data:
            url_page = page.get('url')[0]

            ps = PublicService.from_dict(page)
            cp = ContactPoint.from_dict(page)

            ps_uri = g.add_public_service(ps)
            cp_uri = g.add_contact_point(cp)

            if cp_uri:  # Only make sense if it's not none.
                g.link_ps_cp(ps_uri=ps.uri,
                             cp_uri=cp_uri)

            l_terms = page.pop('terms')
            g.add_concepts(l_terms, public_service_uri=ps_uri)

            l_life_events = page.pop('life_events')
            g.add_life_events(l_life_events, public_service_uri=ps_uri)

            # Public organisation
            preferred_label, loc_uri = d_pub_org_PoC.get(url_page)
            if preferred_label is None or loc_uri is None:  # TODO
                preferred_label, loc_uri = DEFAULT_PUB_ORG_WIEN

            po = PublicOrganization(preferred_label,
                                    loc_uri)
            po_uri = g.add_public_organization(po)
            g.link_ps_po(ps_uri, po_uri)

            # Unused keys
            for k, v in page.items():
                print(k, '# TODO')

                f = map_do.get(k)
                assert f, 'Unknown key'

                f(v)

        print(g.serialize(format='pretty-xml'))

        print(g.serialize(PATH_EXPORT, format='pretty-xml'))
        print(g.serialize(os.path.splitext(PATH_EXPORT)[0] + '.ttl', format='turtle'))

        return

    def test_life_events(self):

        PS_URI = 'http://example.com'

        g = CPSV_APGraph()

        l_life_events = [
            "a sentence ' with an apostrophe.",
            'a double " .'
        ]

        with self.subTest('Adding'):
            g.add_life_events(l_life_events, public_service_uri=PS_URI)

        with self.subTest('Adding again'):
            len_g_before = len(g)

            g.add_life_events(l_life_events, public_service_uri=PS_URI)

            self.assertEqual(len_g_before, len(g), 'Graph should not grow if life event already exists.')

        with self.subTest('Finding it back with a query'):
            for title in l_life_events:
                q = f"""    
                SELECT ?subject ?predicate 
                WHERE {{
                    ?subject ?predicate {Literal(title)._literal_n3()} .
                }}
                """

                l = list(g.query(q))

                self.assertTrue(l, f'Should have {Literal(title)._literal_n3()} in graph')


def get_homepage(url: str) -> str:
    """ 'http://asas.abc.hostname.com/somethings/anything/' ->  'http://asas.abc.hostname.com'

    :param url: String
    :return: String
    """

    v = urlsplit(url)

    homepage = urlunsplit((v.scheme, v.netloc, '', '', ''))

    return homepage
