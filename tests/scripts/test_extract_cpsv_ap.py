import os
import unittest
import warnings

from scripts.extract_cpsv_ap import get_parser, main

DIR_SOURCE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
FILENAME_AFFLIGEM = os.path.join(DIR_SOURCE, "data/relation_extraction/AFFLIGEM_HANDTEKENING.html")
FILENAME_AUSTRHEIM = os.path.join(DIR_SOURCE,
                                  "tests/relation_extraction/EXAMPLE_FILES/https_austrheim_kommune_no_innhald_helse_sosial_og_omsorg_pleie_og_omsorg_omsorgsbustader_.html")

for filename in [DIR_SOURCE, FILENAME_AFFLIGEM, FILENAME_AUSTRHEIM]:
    if not os.path.exists(filename):
        warnings.warn(f"Could not find file: {filename}")


class TestCLI(unittest.TestCase):
    def test_1_missing_args(self):
        """
        Running the CLI without any arguments
        """
        parser = get_parser()

        # Command
        l_args = []
        self.print_command(l_args)

        with self.assertRaises(SystemExit) as context:
            args = parser.parse_args(l_args)

        self.assertTrue(context.exception)
        self.assertEqual(2, context.exception.code)

    def test_2_help(self):
        parser = get_parser()

        # Command
        l_args = ["-h"]
        self.print_command(l_args)

        # Set args
        with self.assertRaises(SystemExit) as context:
            args = parser.parse_args(l_args)

        self.assertTrue(context.exception)
        self.assertEqual(0, context.exception.code)

    def test_3_path(self):
        """
        Simple call

        >> python .\extract_cpsv_ap.py "../data/relation_extraction/AFFLIGEM_HANDTEKENING.html"
        """

        parser = get_parser()

        # Set args
        l_args = [FILENAME_AFFLIGEM,
                  "DEMO_AFFLIGEM.rdf"]
        args = parser.parse_args(l_args)

        # Command
        self.print_command(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts)

    def test_4_concept_extraction(self):
        """
        """

        parser = get_parser()

        # Set args
        l_args = ["--concepts",
                  FILENAME_AFFLIGEM,
                  "DEMO_AFFLIGEM_CONCEPTS.rdf"
                  ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts)

    def test_5_Norway(self):
        parser = get_parser()

        # Set args
        l_args = [
            FILENAME_AUSTRHEIM,
            "DEMO_AUSTRHEIM.rdf"
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="austrheim.kommune.no",  # TODO add flags
             country_code="NO",  # TODO add flags
             url="https://austrheim.kommune.no/innhald/helse-sosial-og-omsorg/pleie-og-omsorg/omsorgsbustader/")

    def test_5_Belgium(self):
        parser = get_parser()

        # Set args
        l_args = [
            os.path.join(DIR_SOURCE, "tests/relation_extraction/EXAMPLE_FILES/https_www_aalter_be_verhuizen.html"),
            "DEMO_BELGIUM.rdf"
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="www.aalter.be",  # TODO add flags
             country_code="BE",  # TODO add flags
             url="https://www.aalter.be/verhuizen"
             )

    def test_5_Italy(self):
        parser = get_parser()

        # Set args
        l_args = [
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_comune_sanpaolo_bs_it_procedure_3As_italia_3Atrasferimento_residenza_estero_3Bdichiarazione_source_1104.html"),
            "DEMO_ITALY.rdf"
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="www.comune.sanpaolo.bs.it",  # TODO add flags
             country_code="IT",  # TODO add flags
             url="https://www.comune.sanpaolo.bs.it/procedure%3As_italia%3Atrasferimento.residenza.estero%3Bdichiarazione?source=1104"
             )

    def test_5_Slovenia(self):
        parser = get_parser()

        # Set args
        l_args = [
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_nova_gorica_si_za_obcane_postopki_in_obrazci_2011101410574355_.html"),
            "DEMO_SLOVENIA.rdf"
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="www.nova-gorica.si",  # TODO add flags
             country_code="SL",  # TODO add flags
             url="https://www.nova-gorica.si/za-obcane/postopki-in-obrazci/2011101410574355/"
             )

    def test_5_Austria(self):
        parser = get_parser()

        # Set args
        l_args = [
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_wien_gv_at_amtshelfer_verkehr_fahrzeuge_aenderungen_einzelgenehmigung_html.html"),
            "DEMO_AUSTRIA.rdf"
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="www.wien.gv.at",  # TODO add flags
             country_code="AT",  # TODO add flags
             url="https://www.wien.gv.at/amtshelfer/verkehr/fahrzeuge/aenderungen/einzelgenehmigung.html"
             )

    def test_5_Croatia(self):
        parser = get_parser()

        # Set args
        l_args = [
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_zagreb_hr_novcana_pomoc_za_opremu_novorodjenog_djeteta_5723.html"),
            "DEMO_CROATIA.rdf"
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="www.zagreb.hr",  # TODO add flags
             country_code="HR",  # TODO add flags
             url="https://www.zagreb.hr/novcana-pomoc-za-opremu-novorodjenog-djeteta/5723"
             )

    @staticmethod
    def print_command(l_args):
        print()
        print("$ python extract_cpsv_ap.py", *l_args)
        print()


class TestCLIGeneral(unittest.TestCase):
    def test_general_Belgium(self):
        parser = get_parser()

        # Set args
        l_args = [
            os.path.join(DIR_SOURCE, "tests/relation_extraction/EXAMPLE_FILES/https_www_aalter_be_verhuizen.html"),
            "DEMO_BELGIUM_GENERAL.rdf"
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="www.aalter.be",  # TODO add flags
             country_code="BE",  # TODO add flags
             url="https://www.aalter.be/verhuizen",
             general=True
             )

    @staticmethod
    def print_command(l_args):
        print()
        print("$ python extract_cpsv_ap.py", *l_args)
        print()


class TestCLIBreaking(unittest.TestCase):
    """Testing out edge cases"""

    def setUp(self) -> None:
        self.RDF_DEBUG = "DEMO_AFFLIGEM_DEBUG.rdf"

    def test_could_not_find_html(self):
        parser = get_parser()

        # Set args
        args = ["../data/relation_extraction/THIS_FILE_SHOULD_NOT_EXISTS.html",
                self.RDF_DEBUG]

        args = parser.parse_args(args)

        with self.assertRaises(FileNotFoundError) as context:
            main(filename_html=args.Path,
                 filename_rdf=args.RDF)

        self.assertTrue(context.exception)

