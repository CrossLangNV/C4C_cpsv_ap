import json
import os
import unittest

from c4c_cpsv_ap.open_linked_data.build_rdf import CPSV_APGraph
from c4c_cpsv_ap.open_linked_data.node import PublicOrganization, PublicService
from data.examples.PoC_public_organisation import d_pub_org_PoC


class TestPublicOrganization(unittest.TestCase):

    def setUp(self) -> None:
        PATH_EXAMPLE = os.path.join(os.path.dirname(__file__), '../../data/examples/demo2.json')

        with open(PATH_EXAMPLE) as json_file:
            self.data = json.load(json_file)

    def test_init(self):
        # Competent authority/ Zuständige Stelle (DE)
        l_titles = [t for p in self.data for t in p.get('life_events') if 'Stelle' in t]
        titles_cp = set(l_titles)

        # TODO extract Competent Authority
        URL_POC = 'https://www.wien.gv.at/amtshelfer/finanzielles/rechnungswesen/abgaben/dienstgeberabgabe.html'

        p_poc = [p for p in self.data if p.get('url')[0] == URL_POC][0]

        preferredLabel = 'Kontoführende Stelle'

        # FROM https://op.europa.eu/en/web/eu-vocabularies/dataset/-/resource?uri=http://publications.europa.eu/resource/dataset/atu
        loc_uri = 'http://publications.europa.eu/resource/authority/atu/AUT_GBK_VIE09'

        po = PublicOrganization(preferredLabel,
                                loc_uri)

        g = CPSV_APGraph(
            # identifier=url_id
        )

        po_uri = g.add_public_organization(po)

        q = """
            PREFIX cv: <http://data.europa.eu/m8g/>
                
            SELECT ?po
            WHERE {
                
                
                #Graph ?graph { 
                    ?po a cv:PublicOrganisation .
                #}
            }
        """

        l = list(g.query(q))

        with self.subTest('One PO'):
            self.assertEqual(len(l), 1)

        with self.subTest('Same URI'):
            self.assertEqual(l[0][0], po_uri, 'Should return same URI')

        return

    def test_build_ps_and_po(self):

        g = CPSV_APGraph()

        default_pub_org_wien = ('Stadt Wien', 'http://publications.europa.eu/resource/authority/atu/AUT_STTS_VIE')

        for page in self.data:

            url_page = page.get('url')[0]

            ps = PublicService.from_dict(page)
            ps_uri = g.add_public_service(ps)

            preferred_label, loc_uri = d_pub_org_PoC.get(url_page)

            if preferred_label is None or loc_uri is None:  # TODO
                preferred_label, loc_uri = default_pub_org_wien

            po = PublicOrganization(preferred_label,
                                    loc_uri)

            po_uri = g.add_public_organization(po)

            g.link_ps_po(ps_uri, po_uri)

        with self.subTest('Non-empty graph'):
            self.assertGreater(len(g), 0)

        with self.subTest("Return PO's"):
            q = """
                PREFIX cv: <http://data.europa.eu/m8g/>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX dct: <http://purl.org/dc/terms/>
                
                SELECT ?po ?label ?spatial
                WHERE {

                    ?po a cv:PublicOrganisation ;
                        skos:prefLabel ?label ; 
                        dct:spatial ?spatial .

                }
            """

            l = list(g.query(q))
            self.assertGreater(len(l), 0)

        with self.subTest("Unique PO's"):
            q = """
                PREFIX cv: <http://data.europa.eu/m8g/>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX dct: <http://purl.org/dc/terms/>

                SELECT ?label ?spatial
                WHERE {

                    ?po a cv:PublicOrganisation ;
                        skos:prefLabel ?label ; 
                        dct:spatial ?spatial .

                }
            """

            l = list(g.query(q))

            self.assertEqual(len(l), len(set(l)), "All PO's should be unique")

        q = """
            PREFIX cv: <http://data.europa.eu/m8g/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX cpsv: <http://purl.org/vocab/cpsv#>

            SELECT ?ps ?po
            WHERE {

                ?ps a cpsv:PublicService .

                OPTIONAL {
                    ?ps ?abc ?po .
                    ?po a cv:PublicOrganisation ;
                }
            }
        """

        l = list(g.query(q))

        with self.subTest('All public services.'):
            self.assertEqual(len(l), len(self.data), 'Should include all public services.')

        for i, (ps_i, po_i) in enumerate(l):
            with self.subTest(f'Exactly one PO per PS. #{i}'):
                self.assertIsNotNone(po_i, f"Couldn't find a PO for {ps_i}")

        return
