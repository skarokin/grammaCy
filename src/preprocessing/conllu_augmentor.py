# errors pretrained model can't handle:
#   - aux + base form -> aux + gerund
#   - adp + gerund -> adp + base form
#   - adjective -> adverb
# errors pretrained model can handle:
#   - subject verb agreement: pretrained model can already differentiate between all verb forms if they are related by 'nsubj'
#   - auxiliary verbs: pretrained model already can handle wrong form of aux verbs like 'be' and 'have'
#   - and a lot more... just a few grammar errors that it can't handle (but they're very common ones so need to fix)

# note that i previously used a fork of word_forms (https://github.com/skarokin/word_forms_threadsafe) to generate 
# different forms of words, but later found lemminflect (faster) and used a rule-based map of adj<->adv 
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
# (thanks Pranshu for idea) this is only necessary for adjective <-> adverb but added extra just for completeness
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

# NOTE: this messes with lemma data, so pipelines requiring the lemma should use a pretrained lemmatizer 
class ConlluAugmentor:
    '''A class to augment a dataset of .conllu files by injecting errors into sentences of interest'''
    
    # data_dir: directory containing .conllu files
    # rules: list of rule tuples [(dep_rel, child_pos_list, head_pos_list, old_tag_list, aug_tag, child, probability)]
    # - old_tag and child work together; if child is True, then old_tag is the tag of the child to change to aug_tag
    #   if child is False, then old_tag is the tag of the head to change to aug_tag  
    def __init__(self, data_dir: str, ADJECTIVE_TO_ADVERB, ADVERB_TO_ADJECTIVE, rules: list[tuple[any]]=None, model: str='en_core_web_sm'):
        self.data_dir = data_dir
        self.rules = rules
        self.nlp = spacy.load(model)
        self.ADJECTIVE_TO_ADVERB = ADJECTIVE_TO_ADVERB
        self.ADVERB_TO_ADJECTIVE = ADVERB_TO_ADJECTIVE

    def add_rule(self, rule: tuple[any]):
        if (rule[0], rule[1], rule[2], rule[3], rule[4], rule[5]) in self.rules:
            return

        self.rules.append(rule)

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

    # open .conllu file and return formatted data
    def open_conllu_file(self, conllu_path: str) -> list[list[str]]:
        if not conllu_path.endswith('.conllu'):
            return None
        
        with open(conllu_path, 'r', encoding='utf-8') as f:
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
                                aug_sentence[index][3] = tag_to_pos[aug_tag]
                            else:
                                return []
                        # update tag of head if child is False and head exists and head tag is in old_tag_list
                        elif int(word[6]) > 0 and sentence[int(word[6])-1][4] in old_tag_list:
                            head_index = int(word[6]) - 1    # words are 1-indexed in CoNLL-U format
                            new_form = self.get_forms(sentence[head_index][1], sentence[head_index][2], aug_tag, nlp)
                            if new_form:
                                aug_sentence[head_index][4] = aug_tag 
                                aug_sentence[head_index][1] = new_form
                                aug_sentence[head_index][3] = tag_to_pos[aug_tag]
                            else:
                                return []
                        else:
                            continue    
                        
                        return aug_sentence 
        # no rules matched for this sentence 
        return []

    # run augment_sentence on an entire .conllu file
    # creates a new .conllu file with the augmented data and appends it to the data directory
    def augment_conllu_file(self, conllu_path: str, out_file: str, counter: list[int], lock: Lock, counter_lock: Lock, nlp):
        if self.rules is None:
            raise ValueError('No rules specified for augmentation, aborting...')

        formatted_data = self.open_conllu_file(conllu_path)
        print(f'Augmenting {conllu_path}...')

        # augment each sentence in the file then output to a new file 
        # lock ensures that only one thread writes to the file or increments counter at a time
        # all files in the same batch will write augmentations to the same file 
        for sentence in formatted_data:
            aug_sentence = self.augment_sentence(sentence, nlp)
            if aug_sentence != []:
                with lock:
                    with open(out_file, 'a', encoding='utf-8') as file:
                        file.write(f'{self.reverse_format_data(aug_sentence, counter[0])}')
                with counter_lock:
                    counter[0] += 1 # increment counter; remember that counter is a list because int is immutable

    # augments {batch_size} files concurrently (python fake concurrency but this is still significantly faster)
    # writes the augmentations of each file within a batch to a single file (may need to change if batch size is too large)
    def run_batch(self, batch_info: tuple[int, list[tuple[str, str]]], nlp):
        number, file_tuples = batch_info

        print(f"Running batch {number}")

        lock = Lock()
        counter_lock = Lock()
        counter = [0]    # hack to ensure counter is passed by reference
        threads = []
        out_file = f'{file_tuples[0][0]}/1zbatch_{number}_aug.conllu'

        threads = [Thread(target=self.augment_conllu_file, args=(file_tuple[1], out_file, counter, lock, counter_lock, nlp)) for file_tuple in file_tuples]

        for thread in threads:
            thread.start()
        
        start_time = time.time()

        for thread in threads:
            thread.join()
        
        end_time = time.time()

        print(f"Batch {number} finished in {end_time-start_time} seconds")

    # processes {num cores in machine} batches in parallel
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

def main():
    data_dir = 'data/raw/onto'

    # 1. change gerunds and past tense verbs to base form verbs
    # 2. change adjectives to adverbs and vice versa
    # 3. change base form verbs after modals to gerunds
    # 4. change base form verbs after modal to past tense verbs 
    # 5. change gerunds after prepositions to base form verbs
    rules = [# ('nsubj', ['PROPN', 'NN', 'NNS'], ['VERB'], ['VBD', 'VBG'], 'VB', False, 0.10),  <-- may be detrimental to performance
             # ('nsubj', ['PROPN', 'NN', 'NNS'], ['VERB'], ['VB'], 'VBG', False, 0.10),         <-- may be detrimental to performance
             ('advmod', ['ADV'], ['VERB'], ['RB'], 'JJ', True, 0.3),
             # ('amod', ['ADJ'], ['VERB'], ['JJ'], 'RB', True, 0.30),  <-- this rule is literally never triggered so commenting out
             ('aux', ['AUX'], ['VERB'], ['VB'], 'VBG', False, 0.15),
             ('aux', ['AUX'], ['VERB'], ['VB'], 'VBD', False, 0.15),
             ('case', ['ADP'], ['VERB'], ['VBG'], 'VB', False, 0.5), # <-- model has trouble with this rule even though high probability 
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