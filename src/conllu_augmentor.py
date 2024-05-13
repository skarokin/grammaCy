# augments the conllu dataset; for purpose of training POS tagger and dependency parser
# the error injection is only changing the POS tags of the words (and also obviously the word itself) because we want
# to ensure that the dependency parser can recognize the correct dependencies even if the POS tags are wrong
# ERRORS WE NEED TO SIMULATE:
#   - noun + gerund: if gerund is 'nsubj' of noun, change gerund to base form verb
#       - in auxiliary + base form verb, model sometimes thinks the base form verb is a noun
#   - adp + gerund: if gerund is 'pcomp' of preposition, change gerund to base form verb 
#       - in adp + base form verb, model thinks the base form verb is a noun
#   - adjective: for each adjective, change to adverb (and vice versa)
#       - model sometimes thinks misplaced adjectives are adverbs and vice versa
#       - suggestion: if adjective is 'advmod' of verb, suggest change to adverb (bc this is incorrect placement of adjective) and etc
# ERRORS WE DON'T NEED TO SIMULATE:
#   - subject verb agreement: model already diffentiates between singular and plural nouns even if ungrammatical sentence
#       - suggest a different form of the verb before the noun
#   - auxiliary verbs: model already can handle wrong form of aux verbs like 'be' and 'have'
#       - suggest a different form of auxiliary verb based on context
#   - gerund vs past tense: model already can differentiate between gerund and past tense verbs
#       - suggest adding a preposition before the gerund OR making the gerund a past tense verb
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