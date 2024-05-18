# check if preposition + verb is in gerund form
# EXAMPLES:
#   'Akira Toriyama is known for create Dragon Ball.' -> 'Akira Toriyama is known for creating Dragon Ball.'
#   'This backpack was made for carry books.' -> 'This backpack was made for carrying books.'
#   'I told him to going to the store' -> 'I told him to go to the store'
# (edge case: if preposition is 'to', it should be followed by a verb in base form)

import spacy
from spacy import displacy

nlp = spacy.load('en_core_web_lg')

sentences = [
    'Akira Toriyama is known for create Dragon Ball.', 'Akira Toriyama is known for creating Dragon Ball.',
    'This backpack was made for carry books.', 'This backpack was made for carrying books.',
    'I told him to going to the store', 'I told him to go to the store',
    'Zuko is known for betraying his uncle.', 'Zuko is known for betray his uncle.',
    'That is for walking.', 'That is for walk.',
]


    

displacy.serve(list(nlp(s) for s in sentences), style='dep')

    