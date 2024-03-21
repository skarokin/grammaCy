# checks if subject and verb agree in number and tense
# 1. if subject is singular/plural, verb must be singular/plural
# 2. if multiple subjects connected by 'and', verb must be plural (need custom matching for noun chunks)
# 3. if 1 subject and more than 1 verb, all verbs must be plural (need custom matching for verb phrases)
# 4. if a phrase comes between subject and verb, verb must still agree with subject
# 5. if two or more singular nouns/pronouns connected by 'or' or 'nor', verb must be singular
# 6. if compound subject is joined by 'or' or 'nor', verb agrees with closest subject
# 7. 'each', 'each one', 'either', 'neither', 'everyone', 'everybody', 'anyone', 'anybody', 'nobody', 
#    'somebody', 'someone', 'no one' are singular
# 8. noncount nouns are always singular
# 9. some countable nouns are explicitly plural, i.e. 'earnings' 'proceeds', 'goods', 'odds', ...
# 10. sentences with 'there is' or 'there are', verb (is/are) agrees with the noun that follows it
# 11. collective nouns are singular
# extra rules:
# - cannot add numbers to noncount nouns

import spacy
from spacy import displacy

# temporary until our own model is trained
nlp = spacy.load('en_core_web_sm')

# a verb phrase is simply [helping verb(s) + main verb + prepositional phrase(s)] so we can use two pointer expansion
# remember that adverb must come before the verb, and preposition must come after
def extract_verb_phrases(token, doc):
    verb_phrases = []
    left = token.i
    right = token.i
    while left > 0 and doc[left-1].pos_ in ['AUX', 'ADV']:
        left -= 1
    while right < len(doc)-1 and doc[right+1].pos_ in ['AUX', 'ADP']:
        right += 1
    verb_phrases.append(doc[left:right+1])
    return verb_phrases

def extract_noun_chunks(doc):
    return list(doc.noun_chunks)

def subject_verb_relationship(doc):
    # the i-th noun chunk is the subject of the i-th verb phrase
    noun_chunks = extract_noun_chunks(doc)
    verb_phrases = []

    for nc in noun_chunks:
        if nc.root.head.pos_ == 'VERB' or nc.root.head.pos_ == 'AUX':
            verb_phrases.extend(extract_verb_phrases(nc.root.head, doc))
    
    return noun_chunks[:len(verb_phrases)], verb_phrases

sentences = ['The dog quickly ran to the park.',
             'She is sleeping in the house.',
             'I just went to the store to buy a new computer.',
             'My mousepad is a little bit dirty.',
             'He has been working hard, but is still not making enough money.']

for s in sentences:
    doc = nlp(s)
    noun_chunks, verb_phrases = subject_verb_relationship(doc)
    print(noun_chunks, verb_phrases)

displacy.serve(list(nlp(s) for s in sentences), style='dep')