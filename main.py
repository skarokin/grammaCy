import spacy
import lemminflect
from src.get_forms import GetForms
from src.english_model import EnglishModel
from word_forms.word_forms import get_word_forms
from memory_profiler import profile

@profile
def main():
    nlp = spacy.load('data/models/train_6_novectors/model-best')

    sentences = [
        'You can learning word embeddings by running the following command',    # rule violated: verb after modal should be in base form
        'I must memorized all the words in this book or else I will fail.',     # rule violated: verb after modal should be in base form
        'You can learn word embeddings by running the following command',       # rule violated: none
        'This backpack was optimized for carry books',                          # rule violated: verb after preposition should be gerund
        'I drunk fought that guy in a bar last night.',                         # rule violated: adjective/adverb confusion
        'I drunk fought that guy and I can learning word embeddings too.'       # rule violated: adjective/adverb confusion, verb after modal should be in base form
    ]

    # disclaimer: word form library has a hard time generating adj form of adv and vice versa
    rules = [
        ('aux', ['MD'], ['VBG', 'VBD', 'VBZ'], ['VB'], False, 'Verbs after modals should be in base form'),
        ('advmod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN'], ['RB'], True, 'Adjective/adverb confusion: use an adverb instead')
    ]

    gf = GetForms(nlp, lemminflect, get_word_forms)
    em = EnglishModel(nlp, gf, rules)
    print(em.enforce(sentences[5]))
    
if __name__ == '__main__':
    main()