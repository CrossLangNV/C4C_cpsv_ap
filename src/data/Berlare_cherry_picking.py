"""
A couple of good chosen examples for the city of Berlare
"""
from data.make_dataset_berlare import DIR_PROCESSED
from data.utils.sitemap import DIR_EXT
from relation_extraction.html_parsing.utils import _tmp_filename
from scripts.extract_cpsv_ap import extract_cpsv_ap_from_html


def main(context="https://berlare.be",
         country_code="BE",
         language_code="NL",
         translations=["EN", "NL", "FR", "DE",
                       "EL", "UK"  # Optional ones
                       ],
         ):
    url_adreswijziging = "https://www.berlare.be/adreswijziging-nieuwe-inwoner.html"

    url_recyclage = "https://www.berlare.be/recyclagepark-1.html"

    url_vergunningen = "https://www.berlare.be/omgevingsvergunning-3.html"

    url_geboorte = "https://www.berlare.be/tc111vhzg1477b96.aspx"

    url = url_adreswijziging
    filename_html = _tmp_filename(url, ext='.html',
                                  dir=DIR_EXT)
    filename_html_parsing = _tmp_filename(url, prefix='parsing_', ext='.html',
                                          dir=DIR_PROCESSED)
    filename_rdf = _tmp_filename(url, ext='.rdf',
                                 dir=DIR_PROCESSED)

    extract_cpsv_ap_from_html(filename_html=filename_html,
                              filename_rdf=filename_rdf,
                              extract_concepts=False,
                              context=context,
                              country_code=country_code,
                              url=url,
                              general=True,
                              lang=language_code,
                              translation=translations,
                              filename_html_parsing=filename_html_parsing
                              )

    return


if __name__ == '__main__':
    main()
