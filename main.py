# a sample implementation of the EnglishModel class. Our actual production model
# contains a more complex set of rules and a custom model. This is a simplified version for demonstration purposes.
import spacy
import lemminflect
from src.get_forms import GetForms
from src.sample_english_model import EnglishModel
import json

with open('src/adj_to_adv.txt', 'r') as f:
    ADJECTIVE_TO_ADVERB = json.load(f)

with open('src/adv_to_adj.txt', 'r') as f:
    ADVERB_TO_ADJECTIVE = json.load(f)

def main():
    # note that en_core_web_sm fails on most of the sample rules given below
    # to see our production model in action, visit https://www.grammacy.com
    # if you wish to use our production model, visit https://github.com/akuwuh/grammacy-api
    nlp = spacy.load('en_core_web_sm')

    sentences = [
        'You can learning word embeddings by running the following command',                         
        'I drunk fought that guy and can learning word embeddings too',         
        'Anxious, they returned home before the storm',                        
        'This backpack was optimized for carry heavy books',
        'She ran.',
        'She is beautifully.'
    ]

    rules = [
        ('aux', ['MD'], ['VBG', 'VBD', 'VBZ'], ['VB'], False, 'Verbs after modals should be in base form'),
        ('advmod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN', 'VBP', 'VBG'], ['RB'], True, 'Adjective/adverb confusion: use an adverb instead'),
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