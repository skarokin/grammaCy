from word_forms.word_forms import get_word_forms
import spacy
import copy
import random
import os

# the single-threaded version of ConlluAugmentor. I highly recommend using the multi-threaded version
# because this class is both unoptimized and also unfinished. If you want to use this class, you will need
# to implement the output to a new .conllu file yourself. Sorry :(

class ConlluAugmentorSingleThread:
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
    def get_forms(self, word: str, tag: str) -> str:
        forms = get_word_forms(word)
        for p in forms:
            for w in forms[p]:
                curr = self.nlp(w)[0]
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
    def augment_sentence(self, sentence: list[str]) -> list[str]:
        shuffled_rules = random.sample(self.rules, len(self.rules))
        aug_sentence = copy.deepcopy(sentence)

        for rule in shuffled_rules:
            dep_rel, child_pos_list, head_pos_list, old_tag_list, aug_tag, child, probability = rule
            for index, word in enumerate(aug_sentence):
                # word matches dependency relation, child pos, and head pos
                if word[7] == dep_rel and word[3] in child_pos_list and sentence[int(word[6])-1][3] in head_pos_list and random.uniform(0, 1) < probability: 
                        # update tag of child
                        if child and sentence[index][4] in old_tag_list:
                            new_form = self.get_forms(word[2], aug_tag)
                            if new_form:
                                aug_sentence[index][4] = aug_tag
                                aug_sentence[index][1] = new_form
                            else:
                                return []    # no augmentation possible
                        # update tag of head
                        elif int(word[6]) > 0 and sentence[int(word[6])-1][4] in old_tag_list:
                            head_index = int(word[6]) - 1    # because head is 1-indexed
                            new_form = self.get_forms(sentence[head_index][2], aug_tag)
                            if new_form:
                                aug_sentence[head_index][4] = aug_tag 
                                aug_sentence[head_index][1] = new_form
                            else:
                                return []    # no augmentation possible
                        else:
                            continue    
                        
                        return aug_sentence 
        # no rules matched for this sentence 
        return []

    # for given .conllu file, find a specific dependency relation and specific POS tag to augment and whether to use head or child
    # create a new .conllu file with the augmented data and append the augmented data to original .conllu file (make sure we update sentence id)
    # augments on a file-by-file basis, so we can run this on a deep traversal of the data directory
    def augment_conllu_file(self, conllu_path: str):
        if self.rules is None:
            raise ValueError('No rules specified for augmentation, aborting...')

        formatted_data = self.open_conllu_file(conllu_path)
        aug_formatted_data = copy.deepcopy(formatted_data)
        count = 0

        for sentence in formatted_data:
            aug_sentence = self.augment_sentence(sentence)
                
            if len(aug_sentence) > 0:
                aug_formatted_data.append(aug_sentence)
                final_string = '# sent_id = ' + str(count) +'\n' + '\n'.join(['\t'.join(word) for word in aug_sentence])
                print(final_string)    # temp; must output to new file later
                count += 1

    # augment entire dataset by traversing data directory and augmenting each .conllu file according to rules in add_rules
    def augment_dataset(self):
        try:
            for root, _, filenames in os.walk(self.data_dir):
                for filename in filenames:
                    f = os.path.join(root, filename)
                    self.augment_conllu_file(f)
        except Exception as e:
            print(f'Error augmenting dataset: {e}')

# testing testing :3
def main():
    data_dir = 'sample_data'
    # dep_rel to look for, list of possible child POS, list of possible head POS, 
    # list of old tags to consider, new tag to change old tag to, whether to change child or head, probability of changing
    rules = [('nsubj', ['PROPN', 'NN', 'NNS'], ['VERB'], ['VBD', 'VBG'], 'VB', False, 1.0)]
    ca = ConlluAugmentorSingleThread(data_dir, rules=rules)
    ca.augment_conllu_file('sample_data/raw/validate/a2e_0010.conllu')

if __name__ == "__main__":
    main()