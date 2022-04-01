import os
import unittest
import warnings

from data.html import url2html
from scripts.extract_cpsv_ap import get_parser, main

DIR_SOURCE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
FILENAME_AFFLIGEM = os.path.join(DIR_SOURCE, "data/relation_extraction/AFFLIGEM_HANDTEKENING.html")
FILENAME_AUSTRHEIM = os.path.join(DIR_SOURCE,
                                  "tests/relation_extraction/EXAMPLE_FILES/https_austrheim_kommune_no_innhald_helse_sosial_og_omsorg_pleie_og_omsorg_omsorgsbustader_.html")

DIR_EXAMPLES = os.path.join(os.path.dirname(__file__), "examples")

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
        l_args = [
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_AFFLIGEM.rdf"),
            "-l", "NL",
            "-c", "BE",
            "-m", "https://affligem.be/",
            "-u",
            "https://www.affligem.be/Affligem/Nederlands/Leven/identiteitsbewijzen,-rijbewijzen-en-afschriften/afschriften-uittreksels-getuigschriften/wettiging-van-handtekening/page.aspx/169#",
            FILENAME_AFFLIGEM
        ]

        args = parser.parse_args(l_args)

        # Command
        self.print_command(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_4_concept_extraction(self):
        """
        """

        parser = get_parser()

        # Set args
        l_args = [
            "-t",
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_AFFLIGEM_CONCEPTS.rdf"),
            "-l", "NL",
            "-c", "BE",
            "-m", "https://affligem.be/",
            "-u",
            "https://www.affligem.be/Affligem/Nederlands/Leven/identiteitsbewijzen,-rijbewijzen-en-afschriften/afschriften-uittreksels-getuigschriften/wettiging-van-handtekening/page.aspx/169#",
            FILENAME_AFFLIGEM
        ]

        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_5_Norway(self):
        parser = get_parser()

        # Set args

        # Set args
        l_args = [
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_AUSTRHEIM.rdf"),
            "-l", "NO",
            "-c", "NO",
            "-m", "austrheim.kommune.no",
            "-u", "https://austrheim.kommune.no/innhald/helse-sosial-og-omsorg/pleie-og-omsorg/omsorgsbustader/",
            FILENAME_AUSTRHEIM
        ]

        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_5_Belgium(self):
        parser = get_parser()

        # Set args
        l_args = [
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_BELGIUM.rdf"),
            "-l", "NL",
            "-c", "BE",
            "-m", "www.aalter.be",
            "-u", "https://www.aalter.be/verhuizen",
            os.path.join(DIR_SOURCE, "tests/relation_extraction/EXAMPLE_FILES/https_www_aalter_be_verhuizen.html"),
        ]

        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_5_Italy(self):
        parser = get_parser()

        # Set args
        l_args = [
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_ITALY.rdf"),
            "-l", "IT",
            "-c", "IT",
            "-m", "www.comune.sanpaolo.bs.it",
            "-u",
            "https://www.comune.sanpaolo.bs.it/procedure%3As_italia%3Atrasferimento.residenza.estero%3Bdichiarazione?source=1104",
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_comune_sanpaolo_bs_it_procedure_3As_italia_3Atrasferimento_residenza_estero_3Bdichiarazione_source_1104.html"),
        ]

        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_5_Slovenia(self):
        parser = get_parser()

        l_args = [
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_SLOVENIA.rdf"),
            "-l", "SI",
            "-c", "SL",
            "-m", "www.nova-gorica.si",
            "-u", "https://www.nova-gorica.si/za-obcane/postopki-in-obrazci/2011101410574355/",
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_nova_gorica_si_za_obcane_postopki_in_obrazci_2011101410574355_.html"),
        ]

        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_5_Austria(self):
        parser = get_parser()

        # Set args
        l_args = [
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_AUSTRIA.rdf"),
            "-l", "DE",
            "-c", "AT",
            "-m", "www.wien.gv.at",
            "-u", "https://www.wien.gv.at/amtshelfer/verkehr/fahrzeuge/aenderungen/einzelgenehmigung.html",
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_wien_gv_at_amtshelfer_verkehr_fahrzeuge_aenderungen_einzelgenehmigung_html.html"),
        ]

        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_5_Croatia(self):
        parser = get_parser()

        # Set args
        l_args = [

        ]

        # Set args
        l_args = [
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_CROATIA.rdf"),
            "-l", "HR",
            "-c", "HR",
            "-m", "www.zagreb.hr",
            "-u", "https://www.zagreb.hr/novcana-pomoc-za-opremu-novorodjenog-djeteta/5723",
            os.path.join(DIR_SOURCE,
                         "tests/relation_extraction/EXAMPLE_FILES/https_www_zagreb_hr_novcana_pomoc_za_opremu_novorodjenog_djeteta_5723.html"),
        ]

        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
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
            "-g",
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_BELGIUM_GENERAL.rdf"),
            "-l", "NL",
            "-c", "BE",
            "-m", "www.aalter.be",
            "-u", "https://www.aalter.be/verhuizen",
            os.path.join(DIR_SOURCE, "tests/relation_extraction/EXAMPLE_FILES/https_www_aalter_be_verhuizen.html"),
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_general_args(self):
        parser = get_parser()

        # Set args
        l_args = [
            "-g",
            "-o", os.path.join(DIR_EXAMPLES, "DEMO_PROCEDURE_GENERAL.rdf"),
            "-l", "NL",
            "-c", "BE",
            "-m", "aalter.be",
            os.path.join(DIR_SOURCE, "scripts/DEMO_PROCEDURE.html"),
        ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.path,
             filename_rdf=args.output,
             extract_concepts=args.terms,
             context=args.municipality,
             country_code=args.country,
             url=args.url,
             general=args.general,
             lang=args.language
             )

    def test_demo(self, run=True):
        if 1:
            url = "https://stad.gent/nl/over-gent-stadsbestuur/belastingen/online-aangiften/belasting-op-woningen-zonder-inschrijving-het-bevolkingsregister-zogenaamde-tweede-verblijven"
            lang = "NL"
            country = "BE"
            homepage = "https://stad.gent"

        elif 1:
            url = "https://www.turnhout.be/inname-openbaar-domein"
            lang = "NL"
            country = "BE"
            homepage = "https://www.turnhout.be"

        # auto
        basename_html = "DEMO_PROCEDURE.html"
        basename_rdf = "DEMO_PROCEDURE_GENERAL.rdf"
        filename_html = os.path.join(DIR_SOURCE, "scripts", basename_html)
        url2html(url, filename_html)

        # Set args
        l_args = [
            "-g",
            "-o", basename_rdf,
            "-l", lang,
            "-c", country,
            "-m", homepage,
            basename_html,
        ]
        # Command
        print("copy the following command")
        self.print_command(l_args)

        if run:
            parser = get_parser()
            args = parser.parse_args(l_args)

            def path_scripts(basename):
                return os.path.join(DIR_SOURCE, "scripts", basename)

            main(filename_html=path_scripts(args.path),
                 filename_rdf=path_scripts(args.output),
                 extract_concepts=args.terms,
                 context=args.municipality,
                 country_code=args.country,
                 url=args.url,
                 general=args.general,
                 lang=args.language
                 )

        return

    @staticmethod
    def print_command(l_args):
        print()
        print("$ python extract_cpsv_ap.py", *l_args)
        print()


class TestCLIBreaking(unittest.TestCase):
    """Testing out edge cases"""

    def test_could_not_find_html(self):
        parser = get_parser()

        FILENAME_DOES_NOT_EXIST = "../data/relation_extraction/THIS_FILE_SHOULD_NOT_EXISTS.html"

        # Set args
        l_args = [
            "-o", "basename_rdf",
            "-l", "lang",
            "-c", "country",
            "-m", "homepage.com",
            FILENAME_DOES_NOT_EXIST,
        ]

        args = parser.parse_args(l_args)

        with self.assertRaises(FileNotFoundError) as context:
            main(filename_html=args.path,
                 filename_rdf=args.output,
                 extract_concepts=args.terms,
                 context=args.municipality,
                 country_code=args.country,
                 url=args.url,
                 general=args.general,
                 lang=args.language
                 )

        self.assertTrue(context.exception)
