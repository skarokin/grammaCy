# pipeline: [(tokenizer) -> (EnglishModel.tagger) -> (EnglishModel.parser) -> (pretrained lemmatizer)]
# input text goes through EnglishGrammarChecker which uses pipeline to check for grammar errors
import spacy
from word_forms.word_forms import get_word_forms
from english_model import EnglishModel
from flask import Flask, request, jsonify

# nlp = spacy.load('path/to/model')

# required for the EnglishModel constructor (we define this outside to avoid loading NLTK and WordNet for each request)
def get_forms(word: str, tag: str, nlp, get_word_forms) -> str:
    forms = get_word_forms(word)
    for p in forms:
        for w in forms[p]:
            curr = nlp(w)[0]
            # must enforce word is not the same... eg 'fast' is both an adjective and an adverb
            if curr.tag_ == tag and curr.text != word:
                print(f'Found {tag} form for {word}: {curr.text}')
                return curr.text
        
    print(f'Could not find {tag} form for: {word}')
    return None
            
