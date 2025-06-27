import re
import spacy
import textstat

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def get_readability_scores(text):
    scores = {}
    scores["flesch_reading_ease"] = textstat.flesch_reading_ease(text)
    scores["gunning_fog"] = textstat.gunning_fog(text)
    scores["smog_index"] = textstat.smog_index(text)
    scores["automated_readability_index"] = textstat.automated_readability_index(text)
    return scores

def detect_passive_voice(sentence):
    doc = nlp(sentence)
    passive_sentences = []
    for sent in doc.sents:
        if any(token.dep_ == "auxpass" for token in sent):
            passive_sentences.append(sent.text.strip())
    return passive_sentences

def identify_long_sentences(sentence, max_length=25):
    doc = nlp(sentence)
    long_sents = []
    for sent in doc.sents:
        if len(sent) > max_length:
            long_sents.append(sent.text.strip())
    return long_sents

def compute_quality_score(readability_scores, sentence_feedback):
    flesch = readability_scores.get("flesch_reading_ease", 60.0)
    if flesch > 100:
        flesch = 100
    elif flesch < 0:
        flesch = 0
    penalty = len(sentence_feedback) * 5
    base_score = flesch - penalty
    if base_score < 0:
        base_score = 0
    return base_score

def analyze_sentence(sentence):
    passive_feedback = detect_passive_voice(sentence)
    complexity_feedback = identify_long_sentences(sentence, max_length=25)
    readability_scores = get_readability_scores(sentence)
    feedback = passive_feedback + complexity_feedback
    quality_score = compute_quality_score(readability_scores, feedback)
    return feedback, readability_scores, quality_score