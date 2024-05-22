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

# note that word_forms library had to be modified to ensure thread safety of wordnet
# see get_related_lemmas_rec() in word_forms/word_forms.py. my fork of this is https://github.com/skarokin/word_forms_threadsafe
import spacy
import lemminflect
import json
import copy
import random
import os
import concurrent.futures as cf
from threading import Thread
from threading import Lock
import time
import traceback

# mapping to automatically update POS if the new tag falls under a different POS category
# Pranshu's idea; this is necessary for adjective <-> adverb and perhaps other augmentations if the user wants to add them
# NOTE: ignores punctuations, symbols, and affixes
# NOTE: this isn't a true 1-1 mapping because, e.g. all verbs can be 'AUX' or 'VERB' and 'RB' can be 'ADV' or 'PART' but we can ignore
tag_to_pos = {
    'JJ': 'ADJ',
    'JJR': 'ADJ',
    'JJS': 'ADJ',
    'RB': 'ADV',
    'RBR': 'ADV',
    'RBS': 'ADV',
    'WRB': 'ADV',
    'IN': 'ADP',
    'RP': 'ADP',
    'VB': 'VERB',
    'VBD': 'VERB',
    'VBG': 'VERB',
    'VBN': 'VERB',
    'VBP': 'VERB',
    'VBZ': 'VERB',
    'MD': 'VERB',
    'CC': 'CCONJ',
    'DT': 'DET',
    'PDT': 'DET',
    'PRP$': 'DET',
    'WDT': 'DET',
    'WP$': 'DET',
    'UH': 'INTJ',
    'NN': 'NOUN',
    'NNS': 'NOUN',
    'POS': 'PART',
    'TO': 'PART',
    'NNP': 'PROPN',
    'NNPS': 'PROPN',
}

# NOTE: this messes with lemma data, but lemmas dont matter for us. If you require a lemmatizer then
#       ensure that you use default spaCy lemmatizers and *do not train lemmatizer on this augmented data*
#       **please only train the POS tagger and dependency parser on thie augmented data** 
class ConlluAugmentor:
    '''A class to augment a dataset of .conllu files by injecting errors into sentences of interest'''
    
    # data_dir: directory containing .conllu files
    # rules: list of rule tuples [(dep_rel, child_pos_list, head_pos_list, old_tag_list, aug_tag, child, probability)]
    # NOTE: old_tag and child work together; if child is True, then old_tag is the tag of the child to change to aug_tag
    #       if child is False, then old_tag is the tag of the head to change to aug_tag  
    def __init__(self, data_dir: str, ADJECTIVE_TO_ADVERB, ADVERB_TO_ADJECTIVE, rules: list[tuple[any]]=None, model: str='en_core_web_sm'):
        self.data_dir = data_dir
        self.rules = rules
        self.nlp = spacy.load(model)
        self.ADJECTIVE_TO_ADVERB = ADJECTIVE_TO_ADVERB
        self.ADVERB_TO_ADJECTIVE = ADVERB_TO_ADJECTIVE

    # note: not perfect; sometimes generates extra forms that do not exist
    # extract first form that matches desired POS using spacy's POS tagger
    def get_forms(self, word: str, lemma: str, tag: str, nlp) -> str:
        lemma = nlp(word)[0]._.lemma()
        word = word.lower()
        
        if tag in ['RB', 'RBR', 'RBS']:
            if word in self.ADJECTIVE_TO_ADVERB:
                form = self.ADJECTIVE_TO_ADVERB[word].lower()
                if form != word:
                    print(f'Found {tag} form for {word}: {form}')
                    return form
            return None
        
        elif tag in ['JJ', 'JJR', 'JJS']:
            if word in self.ADVERB_TO_ADJECTIVE:
                form = self.ADVERB_TO_ADJECTIVE[word].lower()
                if form != word:
                    print(f'Found {tag} form for {word}: {form}')
                    return form
                return None
        
        form = nlp(lemma)[0]._.inflect(tag).lower()
        if form != word:
            print(f'Found {tag} form for {word}: {form}')
            return form
    
        print(f'Could not find {tag} form for: {word}')
        return None
            
    # format string of conllu data into a list of sentences, where each sentence is a list of words with all features
    @staticmethod
    def format_data(data: str) -> list[list[str]]:
        data = data.split('# sent_id =')[1:]
        splitted_data = ['' for _ in range(len(data))]

        for item in data:
            item_split = item.split('\n', 1)
            sent_id = int(item_split[0])
            lines = item_split[1].split('\n')
            split_lines = [line.split('\t') for line in lines if line.strip()]  # split by tab, ignore extraneous lines
            splitted_data[sent_id] = split_lines
        
        return splitted_data
    
    # reverses the sentence back to CoNLL-U format, assigning a new sent_id
    @staticmethod
    def reverse_format_data(sentence: list[list[str]], sent_id: int) -> str:
        lines = ['\t'.join(word) for word in sentence]
        return f'# sent_id = {sent_id}\n' + '\n'.join(lines) + '\n\n'

    # add a rule to list of rules
    def add_rule(self, rule: tuple[any]):
        # if dep_rel, pos, aug_tag already exists, this is a duplicate rule
        if (rule[0], rule[1], rule[2]) in self.rules:
            return

        self.rules.append(rule)

    # open .conllu file and return formatted data
    def open_conllu_file(self, conllu_path: str) -> list[list[str]]:
        if not conllu_path.endswith('.conllu'):
            return None
        
        with open(conllu_path, 'r') as f:
            data = f.read()
        
        return self.format_data(data)

    # augments a sentence with the first random rule that matches the sentence
    # if no rule matches, return empty list. else, return the augmented sentence
    # automatically updates POS if the new tag falls under a different POS category
    def augment_sentence(self, sentence: list[str], nlp) -> list[str]:
        shuffled_rules = random.sample(self.rules, len(self.rules))
        aug_sentence = copy.deepcopy(sentence)

        for rule in shuffled_rules:
            dep_rel, child_pos_list, head_pos_list, old_tag_list, aug_tag, child, probability = rule
            for index, word in enumerate(aug_sentence):
                # word matches dependency relation, child pos, and head pos
                if word[7] == dep_rel and word[3] in child_pos_list and sentence[int(word[6])-1][3] in head_pos_list and random.uniform(0, 1) < probability: 
                        # update tag of child if child is True and child tag is in old_tag_list
                        if child and sentence[index][4] in old_tag_list:
                            new_form = self.get_forms(word[1], word[2], aug_tag, nlp)
                            if new_form:
                                aug_sentence[index][4] = aug_tag
                                aug_sentence[index][1] = new_form
                                aug_sentence[index][3] = tag_to_pos[aug_tag] # tag_to_pos is 1-1 (even though actual mapping isnt) so this is safe
                            else:
                                return []    # no augmentation possible
                        # update tag of head if child is False and head exists and head tag is in old_tag_list
                        elif int(word[6]) > 0 and sentence[int(word[6])-1][4] in old_tag_list:
                            head_index = int(word[6]) - 1    # because head is 1-indexed
                            new_form = self.get_forms(sentence[head_index][1], sentence[head_index][2], aug_tag, nlp)
                            if new_form:
                                aug_sentence[head_index][4] = aug_tag 
                                aug_sentence[head_index][1] = new_form
                                aug_sentence[head_index][3] = tag_to_pos[aug_tag]
                            else:
                                return []    # no augmentation possible
                        else:
                            continue    
                        
                        return aug_sentence 
        # no rules matched for this sentence 
        return []

    # for given .conllu file, try to augment each sentence with a random rule 
    # creates a new .conllu file with the augmented data and append the augmented data to that .conllu file
    # augments on a file-by-file basis, so we can run this on a deep traversal of the data directory
    def augment_conllu_file(self, conllu_path: str, out_file: str, counter: list[int], lock: Lock, counter_lock: Lock, nlp):
        if self.rules is None:
            raise ValueError('No rules specified for augmentation, aborting...')

        formatted_data = self.open_conllu_file(conllu_path)
        print(f'Augmenting {conllu_path}...')

        # augment each sentence in the file then output to a new file 
        # lock ensures that only one thread writes to the file at a time
        # all files in the same batch will write augmentations to the same file 
        for sentence in formatted_data:
            aug_sentence = self.augment_sentence(sentence, nlp)
            if aug_sentence != []:
                with lock:
                    with open(out_file, 'a') as file:
                        file.write(f'{self.reverse_format_data(aug_sentence, counter[0])}')
                with counter_lock:
                    counter[0] += 1 # increment counter; remember that counter is a list because int is immutable

    def run_batch(self, batch_info: tuple[int, list[tuple[str, str]]], nlp):
        number, file_tuples = batch_info

        print(f"Running batch {number}")

        lock = Lock()
        counter_lock = Lock()
        counter = [0]    # hack since int is immutable but list is mutable
        threads = []
        out_file = f'{file_tuples[0][0]}/zbatch_{number}_aug.conllu'

        threads = [Thread(target=self.augment_conllu_file, args=(file_tuple[1], out_file, counter, lock, counter_lock, nlp)) for file_tuple in file_tuples]

        # start threads
        for thread in threads:
            thread.start()
        
        start_time = time.time()

        for thread in threads:
            thread.join()
        
        end_time = time.time()

        print(f"Batch {number} finished in {end_time-start_time} seconds")

    # multi-processing version of ConlluAugmentor
    # batch_size: number of files to process in parallel
    def run(self, batch_size: int=20):
        try:
            start = time.time()
            batches = []
            counter = 0
            for root, _, filenames in os.walk(self.data_dir):
                # ensure that batches stay within the same directory
                batch = []
                
                for filename in filenames:
                    if filename.startswith('zbatch_') or not filename.endswith('conllu'): 
                        continue

                    f = (root, os.path.join(root, filename))
                    batch.append(f)

                    if len(batch) == batch_size:
                        batches.append((counter, batch))
                        counter += 1
                        batch = []

                # add remaining files to last batch
                if len(batch) != 0: 
                    batches.append((counter, batch)) 

            end = time.time()
            print(f"Batching finished in {end-start} seconds")

            start = time.time()

            with cf.ProcessPoolExecutor() as executor:
                executor.map(self.run_batch, batches, [self.nlp]*len(batches))
            
            end = time.time()

            print(f"Execution finished in {end-start} seconds")
        
        except Exception as e:
            print(f'Error augmenting dataset: {e}')
            traceback.print_exc()

# testing testing :3
def main():
    data_dir = 'data/raw/'

    # dep_rel to look for, list of possible child POS, list of possible head POS, 
    # list of old tags to consider, new tag to change old tag to, whether to change child or head, probability of changing
    # 1. change gerunds and past tense verbs to base form verbs
    # 2. change adjectives to adverbs and vice versa
    # 3. change base form verbs after modals to gerunds
    # 4. change base form verbs after modal to past tense verbs 
    # 5. change gerunds after prepositions to base form verbs
    rules = [# ('nsubj', ['PROPN', 'NN', 'NNS'], ['VERB'], ['VBD', 'VBG'], 'VB', False, 0.10),  <-- detrimental to performance
             # ('nsubj', ['PROPN', 'NN', 'NNS'], ['VERB'], ['VB'], 'VBG', False, 0.10),         <-- detrimental to performance
             ('advmod', ['ADV'], ['VERB'], ['RB'], 'JJ', True, 0.30),
             # ('amod', ['ADJ'], ['VERB'], ['JJ'], 'RB', True, 0.30),  <-- for some reason this rule is literally never triggered so commenting out
             ('aux', ['AUX'], ['VERB'], ['VB'], 'VBG', False, 0.10),
             ('aux', ['AUX'], ['VERB'], ['VB'], 'VBD', False, 0.10),
             ('case', ['ADP'], ['VERB'], ['VBG'], 'VB', False, 0.50),
            ]
    
    with open('src/adj_to_adv.txt', 'r') as f:
        ADJECTIVE_TO_ADVERB = json.load(f)
    with open('src/adv_to_adj.txt', 'r') as f:
        ADVERB_TO_ADJECTIVE = json.load(f)
    
    ca = ConlluAugmentor(data_dir, ADJECTIVE_TO_ADVERB, ADVERB_TO_ADJECTIVE, rules=rules)
    start = time.time()
    
    ca.run(batch_size=120)
    end = time.time()
    print(f"finished in {end-start} seconds")

if __name__ == "__main__":
    main()