from word_forms.word_forms import get_word_forms
import spacy
import copy
import random
import os
import time
import traceback
import concurrent.futures as cf

# note that word_forms library had to be modified to ensure thread safety of wordnet
# see get_related_lemmas_rec() in word_forms/word_forms.py

class ConlluAugmentor:
    '''A class to augment a dataset of .conllu files by injecting errors into sentences of interest'''
    
    # data_dir: directory containing .conllu files
    # rules: list of rule tuples [(dep_rel, child_pos_list, head_pos_list, old_tag_list, aug_tag, child, probability)]
    # NOTE: old_tag and child work together; if child is True, then old_tag is the tag of the child to change to aug_tag
    #       if child is False, then old_tag is the tag of the head to change to aug_tag  
    def __init__(self, data_dir: str, rules: list[tuple[any]]=None, model: str='en_core_web_sm'):
        self.data_dir = data_dir
        self.rules = rules
        self.nlp = spacy.load(model) 

    # note: not perfect; sometimes generates extra forms that do not exist
    # extract first form that matches desired POS using spacy's POS tagger
    def get_forms(self, word: str, tag: str, nlp, get_word_forms) -> str:
        forms = get_word_forms(word)
        for p in forms:
            for w in forms[p]:
                curr = nlp(w)[0]
                if curr.tag_ == tag:
                    print('found form:', curr.text)
                    return curr.text
        print('could not find form for', word, tag)
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

    # returns augmented sentence
    def augment_sentence(self, sentence: list[str], nlp, get_word_forms) -> list[str]:
        shuffled_rules = random.sample(self.rules, len(self.rules))
        aug_sentence = copy.deepcopy(sentence)

        for rule in shuffled_rules:
            dep_rel, child_pos_list, head_pos_list, old_tag_list, aug_tag, child, probability = rule
            for index, word in enumerate(aug_sentence):
                # word matches dependency relation, child pos, and head pos
                if word[7] == dep_rel and word[3] in child_pos_list and sentence[int(word[6])-1][3] in head_pos_list and random.uniform(0, 1) < probability: 
                        # update tag of child
                        if child and sentence[index][4] in old_tag_list:
                            new_form = self.get_forms(word[2], aug_tag, nlp, get_word_forms)
                            if new_form:
                                aug_sentence[index][4] = aug_tag
                                aug_sentence[index][1] = new_form
                            else:
                                print(f"Could not find form for child {word[2]} with tag {aug_tag}")
                                return []    # no augmentation possible
                        # update tag of head
                        elif int(word[6]) > 0 and sentence[int(word[6])-1][4] in old_tag_list:
                            head_index = int(word[6]) - 1    # because head is 1-indexed
                            new_form = self.get_forms(sentence[head_index][2], aug_tag, nlp, get_word_forms)
                            if new_form:
                                aug_sentence[head_index][4] = aug_tag 
                                aug_sentence[head_index][1] = new_form
                            else:
                                print(f"Could not find form for head {sentence[head_index][2]} with tag {aug_tag}")
                                return []    # no augmentation possible
                        else:
                            continue    
                        
                        return aug_sentence 
        # no rules matched for this sentence 
        return []

    # for given .conllu file, find a specific dependency relation and specific POS tag to augment and whether to use head or child
    # create a new .conllu file with the augmented data and append the augmented data to original .conllu file (make sure we update sentence id)
    # augments on a file-by-file basis, so we can run this on a deep traversal of the data directory
    def augment_conllu_file(self, conllu_path: str, file, nlp, get_word_forms):
        if self.rules is None:
            raise ValueError('No rules specified for augmentation, aborting...')

        formatted_data = self.open_conllu_file(conllu_path)
        print(f'Augmenting {conllu_path}...')

        for sentence in formatted_data:
            aug_sentence = self.augment_sentence(sentence, nlp, get_word_forms)
            if aug_sentence != []:
                file.write(f'{aug_sentence}\n')

    # run augmentation concurrently on a batch of files
    def run_batch(self, args: tuple[int, list[str]], nlp, get_word_forms):
        number, files = args
        print(f"Running batch {number}")
        
        out_dir = 'sample_data/augmented'
        out_file = open(f'{out_dir}/tr_aug_{number}.conllu', 'a')

        for file in files:
            self.augment_conllu_file(file, out_file, nlp, get_word_forms)
        
        out_file.close()
        
        print(f"Batch {number} finished and written to {out_dir}/tr_aug_{number}.conllu")

    # group files into batches by thread count and run augmentation on each batch in parallel
    def run(self, num_processes: int=4, batch_size: int=10):
        try:
            start = time.time()
            batches = []
            counter = 0
            for root, _, filenames in os.walk(self.data_dir):
                batch = []
                
                for filename in filenames:
                    if filename.startswith('tr_aug') or not filename.endswith('conllu'): 
                        continue

                    f = os.path.join(root, filename)
                    batch.append(f)

                    if len(batch) == batch_size:
                        batches.append((counter, batch))
                        counter += 1
                        batch = []

                if len(batch) != 0: 
                    batches.append((counter, batch))

            end = time.time()
            print(f"Batching Finished in {end-start} seconds")

            start = time.time()

            out_dir = self.data_dir + '/augmented'
            os.makedirs(out_dir, exist_ok=True)

            with cf.ProcessPoolExecutor(max_workers=num_processes) as executor:
                executor.map(self.run_batch, batches, [self.nlp]*len(batches), [get_word_forms]*len(batches))
            
            end = time.time()

            print(f"Execution Finished in {end-start} seconds")
        
        except Exception as e:
            print(f'Error augmenting dataset: {e}')
            traceback.print_exc()

# testing testing :3
def main():
    data_dir = 'data/raw/'
    # dep_rel to look for, list of possible child POS, list of possible head POS, 
    # list of old tags to consider, new tag to change old tag to, whether to change child or head, probability of changing
    rules = [('nsubj', ['PROPN', 'NN', 'NNS'], ['VERB'], ['VBD', 'VBG'], 'VB', False, 1.0)]
    ca = ConlluAugmentor(data_dir, rules=rules)
    start = time.time()
    ca.run(6, 100)
    end = time.time()
    print(f"finished in {end-start} seconds")

if __name__ == "__main__":
    main()