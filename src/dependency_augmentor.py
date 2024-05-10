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

