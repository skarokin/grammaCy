# checks if subject and verb agree in number and tense
# below rules come from a website lol
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

import spacy
from spacy import displacy

# temporary until our own model is trained
nlp = spacy.load('en_core_web_lg')

def extract_verb_phrases(token, doc):
    '''
    extracts the verb phrase of a given noun chunk's head verb with a two pointer expansion
    '''
    verb_phrases = []
    left = token.i
    right = token.i
    while left > 0 and doc[left-1].pos_ in ['AUX', 'ADV', 'VERB', 'PART']:
        left -= 1
    while right < len(doc)-1 and doc[right+1].pos_ in ['AUX', 'ADP', 'VERB', 'PART']:
        right += 1
    verb_phrases.append(doc[left:right+1])
    return verb_phrases

def extract_noun_chunks(doc):
    '''
    extract only those noun chunks that are subjects of verbs
    extracting objects are unnecessary for subject-verb agreement
    '''
    return [nc for nc in doc.noun_chunks if nc.root.dep_ in ('nsubj', 'nsubjpass', 'csubj', 'csubjpass')]

def subject_verb_relationship(doc):
    '''
    returns two lists of noun chunks and verb phrases
    where the i-th noun chunk is the subject of the i-th verb phrase
    we can use zip() to iterate over both lists and check for agreement
    '''
    noun_chunks = extract_noun_chunks(doc)
    verb_phrases = []

    for nc in noun_chunks:
        if nc.root.head.pos_ in ('VERB', 'AUX'):
            verb_phrases.extend(extract_verb_phrases(nc.root.head, doc))
    
    return noun_chunks, verb_phrases

# --------------------------------------------
#                 TESTING
# --------------------------------------------

sentences = [
    'You have to let go of Katara if you want to master the Avatar State.', 'You have to lets go of Katara if you wants to master the Avatar State.',
    'Sokka may have been the best character in the show.', 'Sokka may has been the best character in the show.',
    'Aang and Katara are in love.', 'Aang and Katara is in love.',
    'Toph became the greatest earthbender in the world.', 'Toph become the greatest earthbender in the world.',
    'Jin always visits the Jasmine Dragon to see Zuko.', 'Jin always visit the Jasmine Dragon to see Zuko.',
    'Zuko dressed as the Blue Spirit to save Aang.', 'Zuko dress as the Blue Spirit to save Aang.',
    'He insists on check.'
]
# 'to lets' is marked as a noun chunk; maybe we need to check whether the assigned POS is correct?

# VBZ: 3rd person singular present, should be used with singular subjects
# VBP: non-3rd person singular present, should be used with plural subjects
# pranshu add extra tests if you wanna
# btw you can do noun.morph.get('Number') to determine plurality, but you CANNOT do this with verbs

for s in sentences:
    # if singular noun, check if verb agrees
    # if plural noun, check if verb agrees
    doc = nlp(s)
    noun_chunks, verb_phrases = subject_verb_relationship(doc)
    print(noun_chunks, verb_phrases)
    for nc, vp in zip(noun_chunks, verb_phrases):
        print(f'verb morphologies: {[(v.text, v.morph, v.tag_) for v in vp]}')
        

displacy.serve(list(nlp(s) for s in sentences), style='dep')