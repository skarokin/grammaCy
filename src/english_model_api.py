import spacy
import lemminflect    # shows up as unused import but is used as a spaCy extension so don't remove :D
from word_forms.word_forms import get_word_forms
from get_forms import GetForms
from english_model import EnglishModel
from flask import Flask, request, jsonify

nlp = spacy.load('data/models/train_1/model-best')
rules = [

]

gf = GetForms(nlp, lemminflect, get_word_forms)
em = EnglishModel(nlp, gf, rules)