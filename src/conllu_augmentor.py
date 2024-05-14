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
import copy
import random
import os

class ConlluAugmentor:
    '''A class to augment a dataset of .conllu files by injecting errors into sentences of interest'''
    # data_dir: directory containing .conllu files
    # rules: list of rule tuples [(dep_rel, pos, aug_pos, child=False, probability=0.5)] 
    def __init__(self, data_dir, rules=None, model='en_core_web_sm'):
        self.data_dir = data_dir
        self.rules = rules
        self.nlp = spacy.load(model) 

    # note: not perfect; sometimes generates extra forms that do not exist
    # extract first form that matches desired POS using spacy's POS tagger
    @staticmethod
    def get_forms(word, pos):
        forms = get_word_forms(word)
        for p in forms:
            for w in forms[p]:
                curr = ConlluAugmentor.nlp(w)[0]
                if curr.tag_ == pos:
                    return (curr.text, curr.tag_)
            
    # format string of conllu data into a list of sentences, where each sentence is a list of words with all features
    @staticmethod
    def format_data(data):
        data = data.split('# sent_id =')[1:]
        splitted_data = ['' for _ in range(len(data))]
        for item in data:
            item_split = item.split('\n', 1)
            sent_id = int(item_split[0])
            lines = item_split[1].split('\n')
            split_lines = [line.split('\t') for line in lines if line.strip()]  # split by tab, ignore extraneous lines
            splitted_data[sent_id] = split_lines
        return splitted_data
    
    # look for specific relation between two words and inject desired error
    # [(dep_rel, pos, aug_pos, child=False, probability=0.5), ...]
    # dep_rel: dependency relation to look for
    # pos: POS tag to look for in the dependency relation
    # aug_pos: POS tag to change to
    # child: whether to augment child or head of dependency relation
    # probability: probability of augmenting sentence if it matches dep_rel and pos
    def add_rules(self, rule):
        # if dep_rel, pos, aug_pos already exists, this is a duplicate rule
        if (rule[0], rule[1], rule[2]) in self.rules:
            return

        self.rules.append(rule)

    # returns augmented sentence
    def augment_sentence(self, sentence):
        for rule in self.rules:
            dep_rel, pos, aug_pos, child, probability = rule
            
            aug_sentence = copy.deepcopy(sentence)
            for index, word in enumerate(sentence):
                if word[7] == dep_rel and word[3] == pos and random.uniform(0, 1) < probability: # word matches dependency relation and pos tag 
                        aug_sentence[index][7] = aug_pos # augment
                        return aug_sentence  
        return []
            
            
            
    # open .conllu file and return formatted data
    def open_conllu_file(self, conllu_path):
        if not conllu_path.endswith('.conllu'):
            return None
        
        with open(self.conllu_path, 'r') as f:
            data = f.read()
        return self.format_data(data)

    # for given .conllu file, find a specific dependency relation and specific POS tag to augment and whether to use head or child
    # create a new .conllu file with the augmented data and append the augmented data to original .conllu file (make sure we update sentence id)
    # augments on a file-by-file basis, so we can run this on a deep traversal of the data directory
    def augment_conllu_file(self, conllu_path):
        if self.rules is None:
            raise ValueError('No rules specified for augmentation, aborting...')
        formatted_data = self.open_conllu_file(conllu_path)
        for sentence in formatted_data:
            aug_sentence = self.augment_sentence(sentence)
            if len(aug_sentence) != 0:
            
                # append augmented sentence to original .conllu file    
                pass   

            print("BRUH BRUH DO SOMETHING BRUH POLS")

    # augment entire dataset by traversing data directory and augmenting each .conllu file according to rules in add_rules
    def augment_dataset(self):

        try:
            for filename in os.walk(self.data_dir): # change
                f = os.path.join(self.data_dir, filename)
                # checking if it is a file
                if os.path.isfile(f):
                    self.augment_collu_file(f)

        except Exception as e:
            print(f'Error augmenting dataset: {e}')

        pass
