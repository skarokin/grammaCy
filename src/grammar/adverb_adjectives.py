# checks if adjective and adverb forms are used correctly 
# (e.g. 'i ran quick to the store' is incorrect, 'i ran quickly to the store' is correct)

import spacy
from spacy import displacy
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL
config = {
   "moves": None,
   "update_with_oracle_cut_size": 100,
   "learn_tokens": False,
   "min_action_freq": 30,
   "model": DEFAULT_PARSER_MODEL,
}
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("parser", config=config)


sentences = ['i had to quick run to the store to get some food']



def main(sentences):
  for sentence in sentences:
    adverbAdjective(sentence)



def adverbAdjective(sentence):
    numOfDuplicates = 0
    for sentence in sentences:
        tokenizedSentence = nlp(sentence)
        for word in tokenizedSentence: 
           if word.pos == "ADV":
              if not "ly" in str(word):
                 print("adverbs should have ly")
           elif word.pos == "ADJ":
              if "ly" in str(word):
                 print("adjectives shouldn't have ly")
              


main(sentences)