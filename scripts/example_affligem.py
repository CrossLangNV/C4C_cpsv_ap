import os

from c4c_cpsv_ap.models import Cost, CriterionRequirement, Evidence, Rule
from data.html import FILENAME_HTML_AFFLIGEM, get_html
from relation_extraction.affligem import AffligemParser
from relation_extraction.methods import RelationExtractor


def main(filename: str,  # input filename html
         context: str,  # URL
         country_code: str,  # ISO 3166
         filename_rdf: str,
         extract_concepts=True):  # output filename
    """
    """

    # Get the HTML page
    html = get_html(filename)

    parser = AffligemParser()
    d_relations = parser.extract_relations(html)

    # Apply relation extraction
    relation_extractor = RelationExtractor(html,
                                           context=context,
                                           country_code=country_code)

    uri_ps = relation_extractor.extract_all(extract_concepts=extract_concepts)

    # TODO add new relations

    DEFAULT_NAME = "DEFAULT NAME"

    crit_req = CriterionRequirement(identifier=None,
                                    name=DEFAULT_NAME,
                                    type=[],
                                    description=d_relations.criterionRequirement
                                    )
    rule = Rule(identifier=None,
                description=d_relations.rule,
                name=DEFAULT_NAME
                )
    evidence = Evidence(identifier=None,
                        name=DEFAULT_NAME,
                        description=d_relations.evidence
                        )
    cost = Cost(identifier=None,
                description=d_relations.cost
                )

    uri_cr = relation_extractor.provider.criterion_requirements.add(crit_req, context=context)
    relation_extractor.provider.public_services.add_criterion(uri_ps=uri_ps,
                                                              uri_crit_req=uri_cr,
                                                              context=context)

    uri_rule = relation_extractor.provider.rules.add(rule, context=context)
    relation_extractor.provider.public_services.add_rule(uri_ps=uri_ps,
                                                         uri_rule=uri_rule,
                                                         context=context)

    uri_evi = relation_extractor.provider.evidences.add(evidence, context=context)
    relation_extractor.provider.public_services.add_evidence(uri_ps=uri_ps,
                                                             uri_evi=uri_evi,
                                                             context=context)

    uri_cost = relation_extractor.provider.costs.add(cost, context=context)
    relation_extractor.provider.public_services.add_cost(uri_ps=uri_ps,
                                                         uri_cost=uri_cost,
                                                         context=context)

    # -- Save in RDF --
    relation_extractor.export(filename_rdf)

    return


if __name__ == '__main__':
    main(filename=FILENAME_HTML_AFFLIGEM,
         context="https://www.affligem.be",
         country_code="BE",
         filename_rdf=os.path.join(os.path.dirname(__file__), 'example_affligem.rdf'),
         extract_concepts=False)
