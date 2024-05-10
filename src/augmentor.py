# 1. takes in treebank from data/raw
# 2. unpacks treebank into dictionary
# 3. injects errors 
# 4. repacks treebank into CoNLL-U format
# 5. runs the preprocess script on augmented treebank
# 6. saves augmented treebank in .spacy format to data/processed
# the error injection is only changing the POS tags of the words (and also obviously the word itself) because we want
# to ensure that the dependency parser can recognize the correct dependencies even if the POS tags are wrong
# so, we are not changing the dependency relations themselves but only the POS tags
# ERRORS WE NEED TO SIMULATE:
#   - preposition + verb: for each preposition, take its 'prep' dependency and change the verb to base form
#       - this is needed because the current parser would see prep + base form verb as prep + noun
#       - or, it would assign the wrong POS to the preposition (like sconj or particle)
# ERRORS WE DONT NEED TO SIMULATE:
#   - adjective + adverb: from empirical testing, current parser does just fine
#   - subject-verb agreement: from empirical testing, current parser does just fine
import spacy
from spacy import displacy

nlp = spacy.load('en_core_web_lg', disable=['ner'])

sentences = [
    'Akira Toriyama is known for create Dragon Ball.', 'Akira Toriyama is known for creating Dragon Ball.',
    'This backpack was made for carry books.', 'This backpack was made for carrying books.',
    'I told him to going to the store', 'I told him to go to the store',
    'Zuko is known for betraying his uncle.', 'Zuko is known for betray his uncle.',
    'That is for walking.', 'That is for walk.',
    'This item is optimized for walking.', 'This item is optimized for walk the dogs.'
]
    

displacy.serve(list(nlp(s) for s in sentences), style='dep')