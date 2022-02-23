import json
import unittest

import requests

from context_broker.script_upload import ItemContextBroker, ItemRDF, OrionConnector, URL_ORION


class TestConversion(unittest.TestCase):
    maxDiff = 10000

    def setUp(self, debug=False) -> None:
        self.d_cpsv_ap = {
            '@id': 'http://cefat4cities.crosslang.com/content/BusinessEvent3a219a1b99cb4ad08465933752aed6f2',
            '@type': [
                'http://data.europa.eu/m8g/BusinessEvent',
                # 'http://data.europa.eu/m8g/Event'
            ],
            'http://purl.org/dc/terms/identifier': [
                {'@value': '81ae5cedbe664c0a864c90c65c329414'}],
            'http://purl.org/dc/terms/relation': [
                {'@id': 'http://cefat4cities.crosslang.com/content/PublicService891912a426cb48118dbdfe169cd38a62'}],
            'http://purl.org/dc/terms/title': [
                {'@value': 'Start a new project'}]
        }

        # TODO add DCTerms to context
        # TODO The context broker should accept multiple items.
        self.d_context_broker = {
            '@id': 'c4c:BusinessEvent3a219a1b99cb4ad08465933752aed6f2',
            '@type': 'http://data.europa.eu/m8g/BusinessEvent',
            'http://purl.org/dc/terms/identifier':
                {'value': '81ae5cedbe664c0a864c90c65c329414', 'type': 'Property'},
            'http://purl.org/dc/terms/relation':
                {'object': 'c4c:PublicService891912a426cb48118dbdfe169cd38a62',
                 'type': 'Relationship'},
            'http://purl.org/dc/terms/title':
                {'value': 'Start a new project',
                 'type': 'Property'},
            '@context':
                {'c4c': 'http://cefat4cities.crosslang.com/content/'}
        }
        if debug:
            print(json.dumps(self.d_context_broker))

    def test_from_rdf_to_cb(self):
        cb = ItemContextBroker.from_RDF(self.d_cpsv_ap)

        self.assert_equal_json(self.d_context_broker, cb, 'Context broker')

    def test_from_cb_to_rdf(self):
        rdf = ItemRDF.from_context_broker(self.d_context_broker)

        self.assert_equal_json(self.d_cpsv_ap, rdf, 'JSON-LD')

    def test_from_rdf_to_rdf(self):
        cb = ItemContextBroker.from_RDF(self.d_cpsv_ap)
        rdf = ItemRDF.from_context_broker(cb)

        self.assert_equal_json(self.d_cpsv_ap, rdf, 'JSON-LD')

    def test_from_cb_to_cb(self):
        rdf = ItemRDF.from_context_broker(self.d_context_broker)
        cb = ItemContextBroker.from_RDF(rdf)

        self.assert_equal_json(self.d_context_broker, cb, 'Context broker')

    def assert_equal_json(self, j_gt, j_pred, name=''):
        """
        Custom equal assertion for JSON's: consists of Dictionaries, Lists and Strings.
        Args:
            j_gt:
            j_pred:
            name:

        Returns:

        """

        # with self.subTest(name):
        #     self.assertEqual(j_gt, j_pred)

        if isinstance(j_gt, list):
            # List
            with self.subTest(name):
                self.assertIsInstance(j_pred, list)
                self.assertListEqual(j_gt, j_pred)

            if len(j_gt) == len(j_pred):
                for i, (v_gt, v_pred) in enumerate(zip(j_gt, j_pred)):
                    self.assert_equal_json(v_gt, v_pred, f'{name} - {i}')

        elif isinstance(j_gt, dict):
            # Dict
            with self.subTest(name):
                self.assertIsInstance(j_pred, dict)
                self.assertDictEqual(j_gt, j_pred)

            for key, value in j_gt.items():
                self.assert_equal_json(value, j_pred.get(key), f'{name} - {key}')

        else:
            # Other
            with self.subTest(name):
                self.assertEqual(type(j_gt), type(j_pred))
                self.assertEqual(j_gt, j_pred)


class TestConversion2(TestConversion):
    def setUp(self, debug=False) -> None:
        self.d_cpsv_ap = {
            "@id": "http://cefat4cities.crosslang.com/content/ContactPointbf428cc9d6ea47b1acc0b48fb2e1ae7d",
            "@type": ["https://schema.org/ContactPoint"],
            "https://schema.org/email": [{"@value": "E-Mail: foerderungen@ma05.wien.gv.at"}],
            "https://schema.org/hoursAvailable": [{
                "@id": "http://cefat4cities.crosslang.com/content/OpeningHoursSpecificationfeb13cbbbb244309907105951403af44"}],
            "https://schema.org/telephone": [{"@value": "Telefon: +43 1 4000-86528"},
                                             {"@value": "Fax: +43 1 4000-99-86510"}]
        }

        self.d_context_broker = {
            "@context": {
                "c4c": "http://cefat4cities.crosslang.com/content/"
            },
            "@id": "c4c:ContactPointbf428cc9d6ea47b1acc0b48fb2e1ae7d",
            "@type": "https://schema.org/ContactPoint",
            "https://schema.org/email":
                {
                    "value": "E-Mail: foerderungen@ma05.wien.gv.at",
                    "type": "Property"
                }
            ,
            "https://schema.org/hoursAvailable":
                {
                    "object": "c4c:OpeningHoursSpecificationfeb13cbbbb244309907105951403af44",
                    "type": "Relationship"
                }
            ,
            "https://schema.org/telephone":
                {
                    "value": ["Telefon: +43 1 4000-86528", "Fax: +43 1 4000-99-86510"],
                    "type": "Property"
                }

        }
        if debug:
            print(json.dumps(self.d_context_broker))

    def test_from_rdf_to_cb(self):
        super(TestConversion2, self).test_from_rdf_to_cb()


class TestOrionConnector(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = OrionConnector(URL_ORION)

        self.id_test = 'c4c:ItemTest01'

        with self.subTest("Sanity check, not yet exists"):
            r_remove = self.conn.remove_item(id=self.id_test)

            self.assertTrue(r_remove.ok or r_remove.json().get('title') == "Entity not found",
                            f"Failed to make sure item is deleted: {r_remove.text}.")

    def test_init(self):
        conn = OrionConnector(URL_ORION)

        response = requests.get(conn.url + conn.PATH_V2)
        self.assertTrue(response.ok)

    def test_add_item(self):
        d = {'@context': {'c4c': 'http://cefat4cities.crosslang.com/content/',
                          'skos': 'http://www.w3.org/2004/02/skos/core#'},
             '@id': self.id_test,
             '@type': 'skos:Concept',
             'skos:prefLabel': {'value': 'Finanzielles', 'type': 'Property'}}

        r = self.conn.add_item(d)

        self.assertTrue(r.ok)

    def test_add_item_fail(self):
        d = {"foo": "bar"}

        r = self.conn.add_item(d)

        self.assertFalse(r.ok)

    def test_add_validate_typo_abbreviation(self):
        d = {'@context': {'c4c': 'http://cefat4cities.crosslang.com/content/',
                          'skos': 'http://www.w3.org/2004/02/skos/core#'},
             '@id': self.id_test,
             '@type': 'sko:Concept',  # Typo
             'skos:prefLabel': {'value': 'Finanzielles', 'type': 'Property'}}

        with self.subTest("Sanity check, not yet exists"):
            r_remove = self.conn.remove_item(id=d["@id"])

            self.assertTrue(r_remove.ok or r_remove.json().get('title') == "Entity not found",
                            f"Failed to make sure item is deleted: {r_remove.text}.")

        r = self.conn.add_item(d)

        with self.subTest("!TODO decide if needed to catch typo"):
            self.assertFalse(r.ok, 'Does not seem to catch typo')

    def test_add_public_service(self):
        d = DataExamples.get_public_service_small()

        ngsi_ld = ItemContextBroker.from_RDF(d)
        ngsi_ld['@context'] = DataExamples.get_context()

        with self.subTest("Sanity check, not yet exists"):
            r_remove = self.conn.remove_item(id=ngsi_ld["@id"])

            self.assertTrue(r_remove.ok or r_remove.json().get('title') == "Entity not found",
                            f"Failed to make sure item is deleted: {r_remove.text}.")

        r = self.conn.add_item(ngsi_ld)

        self.assertTrue(r.ok)

    def test_add_validate(self):
        # From trento.jsonld

        d = DataExamples.get_public_service_empty()

        ngsi_ld = ItemContextBroker.from_RDF(d)
        ngsi_ld['@context'] = DataExamples.get_context()

        with self.subTest("Sanity check, not yet exists"):
            r_remove = self.conn.remove_item(id=ngsi_ld["@id"])

            self.assertTrue(r_remove.ok or r_remove.json().get('title') == "Entity not found",
                            f"Failed to make sure item is deleted: {r_remove.text}.")

        r = self.conn.add_item(ngsi_ld)

        with self.subTest("!TODO decide if needed to catch typo"):
            self.assertFalse(r.ok, 'Does not seem to catch typo')


class DataExamples:
    """
    From trento.jsonld
    """

    @staticmethod
    def get_public_service(id="http://cpsvap.semic.eu/p_TN_1519"):

        d = {"@id": id,
             "@type": "cpsv:PublicService",
             "cpsv:hasInput": [
                 {
                     "@id": "http://cpsvap.semic.eu/a0777fd1-2e0f-466c-9150-c5dd6e5d9515"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/956f5350-aba1-439d-aa5f-03de060cac97"
                 }
             ],
             "cpsv:produces": {
                 "@id": "http://cpsvap.semic.eu/output_fb"
             },
             "cv:hasChannel": {
                 "@id": "http://cpsvap.semic.eu/CH_PS_GeAPF"
             },
             "cv:hasCompetentAuthority": {
                 "@id": "http://cpsvap.semic.eu/LYMI3J"
             },
             "cv:hasContactPoint": [
                 {
                     "@id": "http://cpsvap.semic.eu/CP_LYMI3J"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/CP_LYMI3J_pec"
                 }
             ],
             "cv:hasCost": [
                 {
                     "@id": "http://cpsvap.semic.eu/94957bab-e8cb-44fe-bc7a-3447cf478760"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/2189a486-6ffd-4cd5-939f-4848b3189ad4"
                 }
             ],
             "cv:hasCriterion": {
                 "@id": "http://cpsvap.semic.eu/19194197-782b-418e-b5d2-e033c9147a63"
             },
             "cv:hasLegalResource": [
                 {
                     "@id": "http://cpsvap.semic.eu/DGP-2015-1945"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/LP-1983-19"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/LP-2011-1"
                 }
             ],
             "cv:isDescribedAt": {
                 "@id": "http://cpsvap.semic.eu/WEB_p_TN_1519"
             },
             "cv:isGroupedBy": [
                 {
                     "@id": "http://cpsvap.semic.eu/BE_1.7"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/BE_3.4"
                 }
             ],
             "dct:description": {
                 "@type": "rdfs:Literal",
                 "@value": "I datori di lavoro privati possono richiedere un contributo per la realizzazione di interventi di riorganizzazione e di rimodulazione degli orari di lavoro collegati ad impegni di cura e di assistenza, anche utilizzando il telelavoro, volti ad aumentare la possibilità di conciliare la vita familiare e quella lavorativa dei dipendenti.\nIl contributo è concesso per ogni lavoratore coinvolto in forme di flessibilità o per ogni disoccupato assunto a tempo indeterminato. Il contributo può anche riguardare le spese di consulenza per la riorganizzazione aziendale e le spese di attuazione del progetto riorganizzativo. In tal caso il contributo non può superare il 70% delle relative spese.\n\nIl contributo è ridotto nella misura corrispondente al finanziamento riconosciuto nell'ambito del Family-Audit, nel caso in cui il datore di lavoro aderisca alla sperimentazione nazionale del Family-Audit."
             },
             "dct:identifier": {
                 "@type": "rdfs:Literal",
                 "@value": "p_TN_1519"
             },
             "dct:language": {
                 "@id": "http://publications.europa.eu/resource/authority/language/ITA"
             },
             "dct:title": {
                 "@type": "rdfs:Literal",
                 "@value": "Work family - progetti sui regimi di orario"
             },
             "dct:type": [
                 {
                     "@id": "http://cpsvap.semic.eu/01.3.1"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/10.4.0"
                 }
             ]
             }

        return d

    @staticmethod
    def get_public_service_small(id="http://cpsvap.semic.eu/p_TN_1519"):

        d = {"@id": id,
             "@type": "cpsv:PublicService",
             "cpsv:hasInput": [
                 {
                     "@id": "http://cpsvap.semic.eu/a0777fd1-2e0f-466c-9150-c5dd6e5d9515"
                 },
                 {
                     "@id": "http://cpsvap.semic.eu/956f5350-aba1-439d-aa5f-03de060cac97"
                 }
             ],
             # "cpsv:produces": {
             #     "@id": "http://cpsvap.semic.eu/output_fb"
             # },
             # "cv:hasChannel": {
             #     "@id": "http://cpsvap.semic.eu/CH_PS_GeAPF"
             # },
             "cv:hasCompetentAuthority": {
                 "@id": "http://cpsvap.semic.eu/LYMI3J"
             },
             # "cv:hasContactPoint": [
             #     {
             #         "@id": "http://cpsvap.semic.eu/CP_LYMI3J"
             #     },
             #     {
             #         "@id": "http://cpsvap.semic.eu/CP_LYMI3J_pec"
             #     }
             # ],
             # "cv:hasCost": [
             #     {
             #         "@id": "http://cpsvap.semic.eu/94957bab-e8cb-44fe-bc7a-3447cf478760"
             #     },
             #     {
             #         "@id": "http://cpsvap.semic.eu/2189a486-6ffd-4cd5-939f-4848b3189ad4"
             #     }
             # ],
             # "cv:hasCriterion": {
             #     "@id": "http://cpsvap.semic.eu/19194197-782b-418e-b5d2-e033c9147a63"
             # },
             # "cv:hasLegalResource": [
             #     {
             #         "@id": "http://cpsvap.semic.eu/DGP-2015-1945"
             #     },
             #     {
             #         "@id": "http://cpsvap.semic.eu/LP-1983-19"
             #     },
             #     {
             #         "@id": "http://cpsvap.semic.eu/LP-2011-1"
             #     }
             # ],
             # "cv:isDescribedAt": {
             #     "@id": "http://cpsvap.semic.eu/WEB_p_TN_1519"
             # },
             # "cv:isGroupedBy": [
             #     {
             #         "@id": "http://cpsvap.semic.eu/BE_1.7"
             #     },
             #     {
             #         "@id": "http://cpsvap.semic.eu/BE_3.4"
             #     }
             # ],
             "dct:description": {
                 "@type": "rdfs:Literal",
                 "@value": "I datori di lavoro privati possono richiedere un contributo per la realizzazione di interventi di riorganizzazione e di rimodulazione degli orari di lavoro collegati ad impegni di cura e di assistenza, anche utilizzando il telelavoro, volti ad aumentare la possibilità di conciliare la vita familiare e quella lavorativa dei dipendenti.\nIl contributo è concesso per ogni lavoratore coinvolto in forme di flessibilità o per ogni disoccupato assunto a tempo indeterminato. Il contributo può anche riguardare le spese di consulenza per la riorganizzazione aziendale e le spese di attuazione del progetto riorganizzativo. In tal caso il contributo non può superare il 70% delle relative spese.\n\nIl contributo è ridotto nella misura corrispondente al finanziamento riconosciuto nell'ambito del Family-Audit, nel caso in cui il datore di lavoro aderisca alla sperimentazione nazionale del Family-Audit."
             },
             "dct:identifier": {
                 "@type": "rdfs:Literal",
                 "@value": "p_TN_1519"
             },
             # "dct:language": {
             #     "@id": "http://publications.europa.eu/resource/authority/language/ITA"
             # },
             "dct:title": {
                 "@type": "rdfs:Literal",
                 "@value": "Work family - progetti sui regimi di orario"
             },
             # "dct:type": [
             #     {
             #         "@id": "http://cpsvap.semic.eu/01.3.1"
             #     },
             #     {
             #         "@id": "http://cpsvap.semic.eu/10.4.0"
             #     }
             # ]
             }

        return d

    @staticmethod
    def get_public_service_empty(id="http://cpsvap.semic.eu/p_TN_1519"):

        d = {"@id": id,
             "@type": "cpsv:PublicService"}

        return d

    @staticmethod
    def get_context():
        if 0:
            context = {
                "adms": "http://www.w3.org/ns/adms#",
                "cpsv": "http://purl.org/vocab/cpsv#",
                "cv": "http://data.europa.eu/m8g/",
                "dcat": "http://www.w3.org/ns/dcat#",
                "dct": "http://purl.org/dc/terms/",
                "eli": "http://data.europa.eu/eli/ontology#",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "locn": "http://www.w3.org/ns/locn#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "schema": "https://schema.org/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            }
        else:
            context = {}
        return context
