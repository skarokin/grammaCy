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
    nlp = spacy.load('data/models/novectors1/model-last')

    sentences = [
        'You can learning word embeddings by running the following command',    # rule violated: verb after modal should be in base form
        'You can learn word embeddings by running the following command',       # rule violated: none                                         
        'I drunk fought that guy and can learning word embeddings too.',        # rule violated: adjective/adverb confusion, verb after modal should be in base form
        'She is beautiful.',                                                    # rule violated: none
        'Fortunate, Lucy recorded the event.',
    ]

    rules = [
        ('aux', ['MD'], ['VBG', 'VBD', 'VBZ'], ['VB'], False, 'Verbs after modals should be in base form'),
        ('advmod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN'], ['RB'], True, 'Adjective/adverb confusion: use an adverb instead'),
        ('amod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN'], ['JJ'], True, 'Adjective/adverb confusion: use an adjective instead'),
    ]

    gf = GetForms(nlp, lemminflect, ADJECTIVE_TO_ADVERB, ADVERB_TO_ADJECTIVE)
    em = EnglishModel(nlp, gf, rules)
    
    for s in sentences:
        print(em.enforce(s))
    
if __name__ == '__main__':
    main()