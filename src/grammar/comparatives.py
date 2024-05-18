# checks if comparatives are used correctly (e.g. 'it is more good' is incorrect)
# also checks for incomplete comparisons (e.g. 'it was much hotter' is incorrect, 'it was much hotter than yesterday' is correct)

import spacy
from spacy import displacy
import re

# temporary until our own model is trained
nlp = spacy.load('en_core_web_sm')
def checkIfEndOfSentence (sentences):

    numOfDuplicates = 0
    for sentence in sentences:
        tokenizedSentence = nlp(sentence)
        
    return numOfDuplicates

def main(sentences):
    
    res = checkIfEndOfSentence(sentences)
    if res>0:
        print ("Minor Style Error: Detected two or more \"and\" in the sentence")

    