# pipeline: [(tokenizer) -> (EnglishModel.tagger) -> (EnglishModel.parser) -> (pretrained lemmatizer)]
# input text goes through EnglishGrammarChecker which uses pipeline to check for grammar errors

# import EnglishGrammarChecker from english_grammar_checker
# nlp = spacy.load('models/english_model')
