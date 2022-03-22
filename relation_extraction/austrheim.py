from relation_extraction.aalter import AalterCPSVAPRelationsClassifier, AalterParser


class AustrheimCPSVAPRelationsClassifier(AalterCPSVAPRelationsClassifier):
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
