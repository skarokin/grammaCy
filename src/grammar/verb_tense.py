# check if verb tense is consistent through the whole sentence
# checks if conjunctions are used correctly, i.e. 'and' is used to join two words, not 'or'
# cannot have multiple 'and's in a sentence
import spacy
from spacy import displacy
import re

# temporary until our own model is trained
nlp = spacy.load('en_core_web_sm')
def checkTense (sentences):

    for sentence in sentences:
        tokenizedSentence = nlp(sentence)
        tense = "False"; 
        for tokenizedWord in tokenizedSentence:
            if tokenizedWord.pos == 'VERB':
                if tense == "False":
                    tense = tokenizedWord.morph 
                elif tokenizedWord.morph != tense: 
                    print("there is an error with tenses")

def main(sentences):
    
    res = checkTense(sentences)

    

sentences = ['I like Chelsea and Juventus and hate Tottenham and AC Milan',
              'I went to the Andes and Lake Titicaca',
              'And then I walked and then I slept']
main(sentences)
