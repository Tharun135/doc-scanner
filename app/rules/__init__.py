from app.rules.grammar_rules import check as check_grammar_rules
from app.rules.style_rules import check as check_style_rules
from app.rules.passive_voice import check as check_passive_voice
from app.rules.terminology_rules import check as check_terminology_rules
from app.rules.consistency_rules import check as check_consistency_rules
from app.rules.long_sentence import check as check_long_sentence
from app.rules.vague_terms import check as check_vague_terms
from app.rules.verb_tense import check_verb_tense

rule_functions = [
    check_grammar_rules,
    check_style_rules,
    check_passive_voice,
    check_terminology_rules,
    check_consistency_rules,
    check_long_sentence,
    check_vague_terms,
    check_verb_tense,
]

__all__ = ['rule_functions']
