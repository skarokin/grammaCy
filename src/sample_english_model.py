import json
# this English model is fine tuned for these specific rules but can be easily extended to include more rules
# - subject-verb agreement
# - adjective/adverb confusion
# - correct verb form (all kinds of cases, like verbs after {prepositions, auxiliaries, etc})
# - correct auxiliary verb form (to be, to have, to do, etc)
# - complete sentence check
# - correct comparative usage
# - consistent verb tense
# - subject-verb-object order check
class EnglishModel:
    def __init__(self, nlp, get_forms, rules):
        '''
        nlp: a spaCy pipeline
        get_forms: a function that takes (word, lemma, tag) and returns the desired tag form of that word
        rules: a list of either tuples or functions that enforce rules on the input text
              [(dep_rel, child_tag_list, head_tag_list, correct_tag_list, enforce_child_or_head, error_message), ...]
              a function as a rule must take a Doc object and get_forms as input and return (error_message, corrected_text)
        '''
        self.nlp = nlp
        self.get_forms = get_forms    
        self.rules = rules
    
    def enforce(self, input_text):
        errors = []
        for rule in self.rules:
            # if rule is a function, call it with the input text
            # else, if rule is simply using dep_rel, child, and parent, apply the rule
            if callable(rule):
                # call rule(self.input_text, self.get_forms) where input_text is a Doc object
                # rule should return (error_message, corrected_word_index, corrected_word)
                error_message, corrected_word_index, corrected_word = rule(input_text, self.get_forms)
                if error_message:
                    errors.append((error_message, corrected_word_index, corrected_word))
            else:
                dep_rel, child_tag_list, head_tag_list, correct_tag_list, child, error_message = rule
                for token in self.nlp(input_text):
                    if token.dep_ == dep_rel:
                        if token.head.tag_ in head_tag_list and token.tag_ in child_tag_list:
                            if not child:
                                if token.head.tag_ not in correct_tag_list:
                                    errors.append((error_message, token.head.i, self.get_forms.get_forms(token.head.text, correct_tag_list[0])))
                            else:
                                if token.tag_ not in correct_tag_list:
                                    errors.append((error_message, token.i, self.get_forms.get_forms(token.text, correct_tag_list[0])))
        return self.format_errors(errors)
    
    # JSON format: {"errors": [{"error": "error message", "corrected_word_index": 0, "suggestion": "corrected_word"}]
    def format_errors(self, errors):
        return json.dumps({
            "errors": [{"error": error_message, "corrected_word_index": corrected_word_index, "suggestion": suggestion} 
                       for error_message, corrected_word_index, suggestion in errors]
        })
