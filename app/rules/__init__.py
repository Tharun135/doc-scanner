from app.rules.accessibility_terms import check as check_accessibility_terms
from app.rules.ai_bot_terms import check as check_ai_bot_terms
from app.rules.cloud_computing_terms import check as check_cloud_computing_terms
from app.rules.computer_device_terms import check as check_computer_device_terms
from app.rules.keys_keyboard_shortcuts import check as check_keys_keyboard_shortcuts
from app.rules.mouse_interaction_terms import check as check_mouse_interaction_terms
from app.rules.security_terms import check as check_security_terms
from app.rules.special_characters import check as check_special_characters
from app.rules.touch_pen_interaction_terms import check as check_touch_pen_interaction_terms
from app.rules.units_of_measure_terms import check as check_units_of_measure_terms
from app.rules.style_guide import check as check_style_guide
from app.rules.terminology_usage import check as check_terminology_usage
from app.rules.style_formatting import check as check_style_formatting
from app.rules.grammar_word_choice import check as check_grammar_word_choice
from app.rules.terminology_b_terms import check as check_terminology_b_terms
from app.rules.style_formatting_b_terms import check as check_style_formatting_b_terms
from app.rules.technical_terms import check as check_technical_terms
from app.rules.grammar_word_choice_b_terms import check as check_grammar_word_choice_b_terms
from app.rules.c.c_languages_terms import check as check_c_languages_terms
from app.rules.c.cable_terms import check as check_cable_terms
from app.rules.c.cabling_terms import check as check_cabling_terms
from app.rules.c.cache_terms import check as check_cache_terms
from app.rules.c.calendar_terms import check as check_calendar_terms
from app.rules.c.callback_terms import check as check_callback_terms
from app.rules.c.callout_terms import check as check_callout_terms
from app.rules.c.can_may_terms import check as check_can_may_terms
from app.rules.c.cancel_terms import check as check_cancel_terms
from app.rules.c.run_vs_carryout_terms import check as check_run_vs_carryout_terms
from app.rules.c.css_terms import check as check_css_terms
from app.rules.c.catalog_terms import check as check_catalog_terms
from app.rules.word_choice.contractions_rule import check as check_contractions
from app.rules.word_choice.concise_simple_words import check as check_concise_simple_words
from app.rules.passive_voice import check as check_passive_voice
from app.rules.long_sentences import check as check_long_sentences

rule_functions = [
    check_accessibility_terms,
    check_ai_bot_terms,
    check_cloud_computing_terms,
    check_computer_device_terms,
    check_keys_keyboard_shortcuts,
    check_mouse_interaction_terms,
    check_security_terms,
    check_special_characters,
    check_touch_pen_interaction_terms,
    check_units_of_measure_terms,
    check_style_guide,
    check_terminology_usage,
    check_style_formatting,
    check_grammar_word_choice,
    check_terminology_b_terms,
    check_style_formatting_b_terms,
    check_technical_terms,
    check_grammar_word_choice_b_terms, 
    check_c_languages_terms,
    check_cable_terms,
    check_cabling_terms,
    check_cache_terms,
    check_calendar_terms,
    check_callback_terms,
    check_callout_terms, 
    check_can_may_terms,
    check_cancel_terms,
    check_run_vs_carryout_terms,
    check_css_terms,
    check_catalog_terms,
    check_contractions,
    check_concise_simple_words,
    check_passive_voice,
    check_long_sentences,
]

__all__ = ['rule_functions']