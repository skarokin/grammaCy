# a different version of ConlluAugmentor that modifies exact words, instead of using dependency relations and POS tags
# for the purpose of homophone augmentation and subjective vs objective pronoun augmentation
import copy
import random
import os
import concurrent.futures as cf
from threading import Thread
from threading import Lock
import time
import traceback

# NOTE: this messes with lemma data, so pipelines requiring the lemma should use a pretrained lemmatizer 
class ConlluAugmentorExactWords:
    '''A class to augment a dataset of .conllu files by injecting errors into sentences of interest'''
    
    # data_dir: directory containing .conllu files
    # rules: source-target pairs, adjusted POS, adjusted tag, adjusted features, probability
    def __init__(self, data_dir: str, rules: list[tuple[any]]=None):
        self.data_dir = data_dir
        self.rules = rules

    def add_rule(self, rule: tuple[any]):
        if (rule[0], rule[1], rule[2], rule[3], rule[4], rule[5]) in self.rules:
            return

        self.rules.append(rule)
            
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
    def augment_sentence(self, sentence: list[str]) -> list[str]:
        shuffled_rules = random.sample(self.rules, len(self.rules))
        aug_sentence = copy.deepcopy(sentence)

        for rule in shuffled_rules:
            source, target, aug_pos, aug_tag, aug_feat, probability = rule
            for index, word in enumerate(aug_sentence):
                # by default, this is child=True
                if word[1] == source and random.uniform(0, 1) < probability:
                    print(f'changing {source} to {target}')
                    aug_sentence[index][1] = target
                    aug_sentence[index][3] = aug_pos
                    aug_sentence[index][4] = aug_tag
                    if aug_feat:
                        aug_sentence[index][5] = aug_feat
                    return aug_sentence
        return []

    # run augment_sentence on an entire .conllu file
    # creates a new .conllu file with the augmented data and appends it to the data directory
    def augment_conllu_file(self, conllu_path: str, out_file: str, counter: list[int], lock: Lock, counter_lock: Lock):
        if self.rules is None:
            raise ValueError('No rules specified for augmentation, aborting...')

        formatted_data = self.open_conllu_file(conllu_path)
        print(f'Augmenting {conllu_path}...')

        # augment each sentence in the file then output to a new file 
        # lock ensures that only one thread writes to the file or increments counter at a time
        # all files in the same batch will write augmentations to the same file 
        for sentence in formatted_data:
            aug_sentence = self.augment_sentence(sentence)
            if aug_sentence != []:
                with lock:
                    with open(out_file, 'a', encoding='utf-8') as file:
                        file.write(f'{self.reverse_format_data(aug_sentence, counter[0])}')
                with counter_lock:
                    counter[0] += 1 # increment counter; remember that counter is a list because int is immutable

    # augments {batch_size} files concurrently (python fake concurrency but this is still significantly faster)
    # writes the augmentations of each file within a batch to a single file (may need to change if batch size is too large)
    def run_batch(self, batch_info: tuple[int, list[tuple[str, str]]]):
        number, file_tuples = batch_info

        print(f"Running batch {number}")

        lock = Lock()
        counter_lock = Lock()
        counter = [0]    # hack to ensure counter is passed by reference
        threads = []
        out_file = f'{file_tuples[0][0]}/1zbatchexact_{number}_aug.conllu'

        threads = [Thread(target=self.augment_conllu_file, args=(file_tuple[1], out_file, counter, lock, counter_lock)) for file_tuple in file_tuples]

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
                    # dont augment augmented files or non-conllu files
                    if filename.startswith('1zbatchexact_') or filename.startswith('1zbatch_') or not filename.endswith('conllu'): 
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
                executor.map(self.run_batch, batches)
            
            end = time.time()

            print(f"Execution finished in {end-start} seconds")
        
        except Exception as e:
            print(f'Error augmenting dataset: {e}')
            traceback.print_exc()

def main():
    data_dir = 'data/raw/gum_cleaned'

    # does not intefere with aumgnetations made from conllu_augmentor.py (by simply skipping over them, as they are prefixed with 1zbatch_)
    # 1. there/their (cant do they're because it contains apostrophe unfortunately and spacy separates into two tokens thus too complicated)
    # 2. I/me, he/him, she/her, we/us, they/them (subjective<->objective pronouns)
    # 3. affect/effect
    # 4. than/then
    # 5. to/too/two
    rules = [
        ("there", "their", "PRON", "PRP$", "Case=Gen|Number=Plur|Person=3|Poss=Yes|PronType=Prs", 0.2),
        ("their", "there", "ADV", "RB", "", 0.2),
        ("I", "me", "PRON", "PRP", "Case=Acc|Number=Sing|Person=1|PronType=Prs", 0.2),
        ("me", "I", "PRON", "PRP", "Case=Nom|Number=Sing|Person=1|PronType=Prs", 0.2),  
        ("he", "him", "PRON", "PRP", "Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs", 0.2),
        ("him", "he", "PRON", "PRP", "Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs", 0.2),  
        ("she", "her", "PRON", "PRP", "Case=Acc|Gender=Fem|Number=Sing|Person=3|PronType=Prs", 0.2),
        ("her", "she", "PRON", "PRP", "Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs", 0.2),
        ("we", "us", "PRON", "PRP", "Case=Acc|Number=Plur|Person=1|PronType=Prs", 0.2),
        ("us", "we", "PRON", "PRP", "Case=Nom|Number=Plur|Person=1|PronType=Prs", 0.2),
        ("they", "them", "PRON", "PRP", "Case=Acc|Number=Plur|Person=3|PronType=Prs", 0.2),
        ("them", "they", "PRON", "PRP", "Case=Nom|Number=Plur|Person=3|PronType=Prs", 0.2),
        ("affect", "effect", "NOUN", "NN", "Number=Sing", 0.2),
        ("effect", "affect", "VERB", "VB", "", 0.2),
        ("than", "then", "ADV", "RB", "", 0.2),
        ("then", "than", "ADP", "IN", "", 0.2),
        ("to", "too", "ADV", "RB", "", 0.2),
        ("too", "to", "PART", "TO", "", 0.2),
        ("to", "two", "NUM", "CD", "NumForm=Word|NumType=Card", 0.2),
        ("two", "to", "PART", "TO", "", 0.2)
    ]
    
    ca = ConlluAugmentorExactWords(data_dir, rules=rules)
    start = time.time()
    
    ca.run(batch_size=5)
    end = time.time()
    print(f"finished in {end-start} seconds")

if __name__ == "__main__":
    main()