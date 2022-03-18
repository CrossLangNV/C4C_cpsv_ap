from relation_extraction.aalter import AalterParser
from relation_extraction.cities import RegexCPSVAPRelationsClassifier, Relations


class AustrheimCPSVAPRelationsClassifier(RegexCPSVAPRelationsClassifier):
    """
    Austrheim
    """

    def __init__(self,
                 pattern_criterion_requirement=r"Krav til søkjar(.)*",
                 pattern_rule=r"Kva skjer vidare(.)*",
                 pattern_evidence=r"(?=x)(?!x)",  # TODO NOT IMPLEMENTED YET
                 pattern_cost=r"Kva kostar det(.)*",
                 ):
        super(AustrheimCPSVAPRelationsClassifier, self).__init__(
            pattern_criterion_requirement=pattern_criterion_requirement,
            pattern_rule=pattern_rule,
            pattern_evidence=pattern_evidence,
            pattern_cost=pattern_cost
        )


class AustrheimParser(AalterParser):  # CityParser
    """
    Parser for https://austrheim.kommune.no/
    """

    def __init__(self, classifier: AustrheimCPSVAPRelationsClassifier = None):

        if classifier is None:
            # Default behaviour
            classifier = AustrheimCPSVAPRelationsClassifier()

        super(AustrheimParser, self).__init__(classifier=classifier)

    def extract_relations(self, s_html: str, url: str) -> Relations:
        """

        Args:
            s_html:
            url:

        Returns:

        """
        l = self.parse_page(s_html)

        d = Relations()

        # TODO implement events extraction
        # events = list(self.extract_event(s_html, url))
        # d.events = events

        for l_sub in l:
            title = l_sub[0]
            paragraphs = l_sub[1:]
            paragraphs_clean = "\n".join(filter(lambda s: s, paragraphs))

            # if title == self.criterionRequirement:
            if self.classifier.predict_criterion_requirement(title, None):
                d.criterionRequirement = paragraphs_clean

            # elif title == self.rule:
            elif self.classifier.predict_rule(title, None):
                d.rule = paragraphs_clean

            # elif title == self.cost:
            elif self.classifier.predict_cost(title, None):
                d.cost = paragraphs_clean

        return d
