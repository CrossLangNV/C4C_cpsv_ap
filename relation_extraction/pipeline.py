import os
import time

from rdflib import Literal

from c4c_cpsv_ap.models import Cost, CriterionRequirement, Evidence, Rule
from connectors.translation import ETranslationConnector
from relation_extraction.cities import CityParser
from relation_extraction.methods import RelationExtractor

CEF_LOGIN = os.environ.get("CEF_LOGIN")
CEF_PASSW = os.environ.get("CEF_PASSW")


class RelationExtractor2(RelationExtractor):
    """
    The extended version of RelationExtractor

    TODO
     * Move the whole class to this module.
    """

    def __init__(self, *args,
                 parser: CityParser,
                 url: str,
                 lang_code: str,
                 **kwargs):
        super(RelationExtractor2, self).__init__(*args, **kwargs)

        self.parser = parser
        self.url = url

        self.lang_code = lang_code

    def extract_all(self, *args, verbose=0, **kwargs, ):
        if verbose:
            print("Relation extraction contact info - Start")
        ps = super(RelationExtractor2, self).extract_all(*args, **kwargs)
        if verbose:
            print("Relation extraction contact info - Finish")

        if verbose:
            print("Relation extraction req/rule/evidence/cost - Start")
        d_relations = self.parser.extract_relations(self.html,
                                                    url=self.url,
                                                    verbose=verbose)
        if verbose:
            print("Relation extraction req/rule/evidence/cost - Finish")

        def add_lang2info(info):
            info.name.language_code = self.lang_code

            # Add language info
            if info.description:
                info.description.language_code = self.lang_code

        if d_relations.criterionRequirements:

            for info in d_relations.criterionRequirements:
                add_lang2info(info)

                crit_req = CriterionRequirement(**info.dict(),
                                                identifier=None,
                                                type=[],
                                                )

                uri_cr = self.provider.criterion_requirements.add(crit_req, context=self.context)
                self.provider.public_services.add_criterion(uri_ps=ps.get_uri(),
                                                            uri_crit_req=uri_cr,
                                                            context=self.context)

        if d_relations.rules:

            for info in d_relations.rules:
                add_lang2info(info)

                rule = Rule(**info.dict(),
                            identifier=None,
                            )

                uri_rule = self.provider.rules.add(rule, context=self.context)
                self.provider.public_services.add_rule(uri_ps=ps.get_uri(),
                                                       uri_rule=uri_rule,
                                                       context=self.context)

        if d_relations.evidences:

            for info in d_relations.evidences:
                add_lang2info(info)

                evidence = Evidence(**info.dict(),
                                    identifier=None,
                                    )

                uri_evi = self.provider.evidences.add(evidence, context=self.context)
                self.provider.public_services.add_evidence(uri_ps=ps.get_uri(),
                                                           uri_evi=uri_evi,
                                                           context=self.context)

        if d_relations.costs:
            for info in d_relations.evidences:
                add_lang2info(info)

                cost = Cost(**info.dict(),
                            identifier=None,
                            )

                uri_cost = self.provider.costs.add(cost, context=self.context)
                self.provider.public_services.add_cost(uri_ps=ps.get_uri(),
                                                       uri_cost=uri_cost,
                                                       context=self.context)

        if d_relations.events:
            for event in d_relations.events:
                event.add_related_service(ps)

                uri_event = self.provider.events.add(event, context=self.context)
                self.provider.public_services.add_event(uri_ps=ps.get_uri(),
                                                        uri_event=uri_event,
                                                        context=self.context)

    def translate(self, target: str, source: str):
        """

        Args:
            target: Language code
            source: Language code

        Returns:

        """

        # Go over all Literals

        # Translate

        # Add to

        print("Translating labels - Start")
        t0 = time.time()

        g = self.provider.graph

        l_to_translate = []

        for s, p, o, c in g.quads():
            # Check one by one.
            if isinstance(o, Literal) and o.language and (o.language.upper() == source.upper()):
                # if o.language.upper() == source.upper():
                l_to_translate.append((s, p, o, c))

        translator = ETranslationConnector(username=CEF_LOGIN,
                                           password=CEF_PASSW)

        l_text_source = [str(o) for s, p, o, c in l_to_translate]

        if isinstance(target, str):
            target = [target]

        for target_i in target:

            if target_i == source:
                # No need to translate
                continue

            l_text_target = translator.trans_list_blocking(l_text_source,
                                                           target=target_i,
                                                           source=source)

            for (s, p, _, c), text_trans in zip(l_to_translate, l_text_target):
                quad_trans = (s, p, Literal(text_trans, lang=target_i), c)
                g.add(quad_trans)

        t1 = time.time()
        print(f"Translating labels - End ({t1 - t0:.2f} s)")

        return
