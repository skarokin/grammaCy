# augments the conllu dataset; for purpose of training POS tagger and dependency parser
# the error injection is only changing the POS tags of the words (and also obviously the word itself) because we want
# to ensure that the dependency parser can recognize the correct dependencies even if the POS tags are wrong
# ERRORS WE NEED TO SIMULATE:
#   - preposition + verb: for each preposition, take its 'prep' dependency and change the verb to base form
#       - this is needed because the current parser would see prep + base form verb as prep + noun
#       - or, it would assign the wrong POS to the preposition (like sconj or particle)
#   - for other confirmed augmentations we will figure this out later (check the pins in discord groupchat)
from word_forms.word_forms import get_word_forms
import spacy

nlp = spacy.load('en_core_web_sm')

# note: not perfect; sometimes generates extra forms that do not exist
# extract first form that matches desired POS 
def get_forms(word, pos):
    forms = get_word_forms(word)
    for p in forms:
        for w in forms[p]:
            curr = nlp(w)[0]
            if curr.tag_ == pos:
                return (curr.text, curr.tag_)

# for given .conllu file, find a specific dependency relation and specific POS tag to augment and whether to use head or child
# create a new .conllu file with the augmented data and append the augmented data to original .conllu file (make sure we update sentence id)
def augment_conllu(conllu_path, dep_rel, pos, child=False):
    pass

print(get_forms('run', 'VBG'))
print(get_forms('amazing', 'RB'))