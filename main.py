import spacy
import lemminflect

nlp = spacy.load('data/models/train_6_novectors/model-best')

sentences = [
    'You can learning word embeddings by run the following command',    # train_6_novectors correct
    'This backpack was optimized for carry books',                      # train_6_novectors incorrect
    'I drunk fought that guy in the bar.',                              # train_6_novectors correct
]

for sentence in sentences:
    doc = nlp(sentence)
    for token in doc:
        print(token.text, token.pos_, token.tag_, token.dep_)
    print('\n')