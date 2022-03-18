from c4c_cpsv_ap.models import Cost, CriterionRequirement, Evidence, Rule
from relation_extraction.cities import CityParser
from relation_extraction.methods import RelationExtractor


class RelationExtractor2(RelationExtractor):
    """
    The extended version of RelationExtractor

    TODO
     * Move the whole class to this module.
    """

    def __init__(self, *args,
                 parser: CityParser,
                 url: str,
                 **kwargs):
        super(RelationExtractor2, self).__init__(*args, **kwargs)

        self.parser = parser
        self.url = url

    def extract_all(self, *args, **kwargs):
        ps = super(RelationExtractor2, self).extract_all(*args, **kwargs)

        # TODO add new relations

        DEFAULT_NAME = "DEFAULT NAME"

        d_relations = self.parser.extract_relations(self.html,
                                                    url=self.url)

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

        events = d_relations.events
        if events:
            for event in events:
                event.add_related_service(ps)

                uri_event = self.provider.events.add(event, context=self.context)
                self.provider.public_services.add_event(uri_ps=ps.get_uri(),
                                                        uri_event=uri_event,
                                                        context=self.context)

        uri_cr = self.provider.criterion_requirements.add(crit_req, context=self.context)
        self.provider.public_services.add_criterion(uri_ps=ps.get_uri(),
                                                    uri_crit_req=uri_cr,
                                                    context=self.context)

        uri_rule = self.provider.rules.add(rule, context=self.context)
        self.provider.public_services.add_rule(uri_ps=ps.get_uri(),
                                               uri_rule=uri_rule,
                                               context=self.context)

        uri_evi = self.provider.evidences.add(evidence, context=self.context)
        self.provider.public_services.add_evidence(uri_ps=ps.get_uri(),
                                                   uri_evi=uri_evi,
                                                   context=self.context)

        uri_cost = self.provider.costs.add(cost, context=self.context)
        self.provider.public_services.add_cost(uri_ps=ps.get_uri(),
                                               uri_cost=uri_cost,
                                               context=self.context)
