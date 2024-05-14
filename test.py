import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_trf")

sentences = [
    "They were going to the store",
    "I was go to the store",
    "He is jumping over the fence",
    "He is jump over the fence",
]

displacy.serve(list(nlp(s) for s in sentences), style='dep')
