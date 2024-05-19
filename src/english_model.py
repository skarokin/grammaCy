import spacy

# NOTE: our API is containerized and kept alive with the spaCy pipeline and get_forms function already loaded in memory
#       this ensures low latency by avoiding the overhead of loading the pipeline and get_forms function for each request
class EnglishModel:
    def __init__(self, spacy_pipeline, get_forms, input_text, rules):
        '''
        spacy_pipeline: a spaCy pipeline
        get_forms: a function that takes a token and desired tag and returns the form of the token with that tag
        input_text: the string to be processed
        rules: a list of either tuples or functions that enforce rules on the input text
              [(dep_rel, child_tag_list, head_tag_list, correct_tag_list, enforce_child_or_head, error_message), ...]
              a function as a rule must take a Doc object and get_forms as input and return (error_message, corrected_text)
        '''
        self.nlp = spacy.load(spacy_pipeline)
        self.get_forms = get_forms
        self.input_text = self.nlp(input_text)
        self.rules = rules
    
    def enforce_rules(self):
        for rule in self.rules:
            # if rule is a function, call it with the input text
            # else, if rule is simply using dep_rel, child, and parent, apply the rule
            if callable(rule):
                # call rule(self.input_text, self.get_forms)
                # rule should return (error_message, corrected_word)
                pass
            else:
                pass
