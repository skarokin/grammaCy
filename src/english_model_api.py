import spacy
import lemminflect   
from word_forms.word_forms import get_word_forms
from get_forms import GetForms
from english_model import EnglishModel
from flask import Flask, request, jsonify
import json

with open('src/adj_to_adv.txt', 'r') as f:
    ADJECTIVE_TO_ADVERB = json.load(f)

with open('src/adv_to_adj.txt', 'r') as f:
    ADVERB_TO_ADJECTIVE = json.load(f)

nlp = spacy.load('data/models/train_1/model-best')

# dep_rel, child_tag_list, head_tag_list, correct_tag_list, child(boolean), error_message
rules = [
    ('aux', ['MD'], ['VBG', 'VBD', 'VBZ'], ['VB'], False, 'Verbs after modals should be in base form'),
    ('advmod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN', 'VBP'], ['RB'], True, 'Adjective/adverb confusion: use an adverb instead'),
    ('amod', ['RB', 'JJ'], ['VBD', 'VBZ', 'VBN'], ['JJ'], True, 'Adjective/adverb confusion: use an adjective instead'),
    ('case', ['IN'], ['VB', 'VBD', 'VBZ', 'VBN', 'VBP'], ['VBG'], False, 'A verb after a preposition should be in gerund form'),
    ('mark', ['IN'], ['VB', 'VBD', 'VBZ', 'VBN', 'VBP'], ['VBG'], False, 'A verb after a subordinating conjunction should be in gerund form')
]

gf = GetForms(nlp, lemminflect, get_word_forms)
em = EnglishModel(nlp, gf, rules)

# ============================================================
# below is temporary; just theorizing how the API would work
# ============================================================

# app = Flask(__name__)
# @app.route('/check', methods=['POST'])
# def process_request(json_data):
#     inp = json_data['input']
#     errors = em.enforce(inp)
#     return jsonify(errors)