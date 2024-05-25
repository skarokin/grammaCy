import spacy
import lemminflect
from src.get_forms import GetForms
from src.english_model import EnglishModel
import json

with open('src/adj_to_adv.txt', 'r') as f:
    ADJECTIVE_TO_ADVERB = json.load(f)

with open('src/adv_to_adj.txt', 'r') as f:
    ADVERB_TO_ADJECTIVE = json.load(f)

def main():
    nlp = spacy.load('data/models/novectors11/model-best')

    sentences = [
        'You can learning word embeddings by running the following command',    # verb after modal should be in base form                                      
        'I drunk fought that guy and can learning word embeddings too',        # adjective/adverb confusion, verb after modal should be in base form                       
        'Anxious, they returned home before the storm',                        # adjective/adverb confusion
        'grammaCy improves rule-based systems with dependency parsing',        # none
        'They ran quickly.',
    ]

    rules = [
        ('aux', ['MD'], ['VBG', 'VBD', 'VBZ'], ['VB'], False, 'Verbs after modals should be in base form'),
        ('advmod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN', 'VBP'], ['RB'], True, 'Adjective/adverb confusion: use an adverb instead'),
        ('amod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN'], ['JJ'], True, 'Adjective/adverb confusion: use an adjective instead'),
        ('case', ['IN'], ['VB', 'VBD', 'VBZ', 'VBN', 'VBP'], ['VBG'], False, 'A verb after a preposition should be in gerund form'),
        ('mark', ['IN'], ['VB', 'VBD', 'VBZ', 'VBN', 'VBP'], ['VBG'], False, 'A verb after a subordinating conjunction should be in gerund form')
    ]

    gf = GetForms(nlp, lemminflect, ADJECTIVE_TO_ADVERB, ADVERB_TO_ADJECTIVE)
    em = EnglishModel(nlp, gf, rules)
    
    for s in sentences:
        for token in nlp(s):
            print(token.text, token.pos_, token.tag_, token.dep_, token.head.text)
        print(em.enforce(s))
        print()
    
if __name__ == '__main__':
    main()