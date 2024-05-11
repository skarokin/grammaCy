# depparse-grammar
hybrid ml + rule-based grammar checker using spaCy's dependency parser

some parts of this project are inspired by "Grammar Checking with Dependency Parsing: A Possible Extension for LanguageTool" (Maxim Mozgovoy)

### whats the point?
rule-based systems are desirable for speed and flexibility. they can also very quickly generate suggestions and are easy to debug. but... rule-based systems fail to keep up with the nuances of natural language. by using a dependency parser, we can ensure our rule-based system keeps up with the nuances of natural language. thus, we have an accurate, fast, and flexible grammar checker that generates suggestions quickly and is easy to debug.

### how it works
- run input sentence through a POS tagger and dependency parser
    - this accommodates for the nuances of natural language while leveraging the speed and flexibility of rule-based systems
- enforce user-defined grammar rules by comparing the POS tags of a specified dependency relation's head and child
    - this allows us to quickly generate suggestions via a dictionary lookup without relying on another ML model

### how was the english model made?
1. created a dictionary that mapped english word lemmas to all of their different forms
    - for example, `dictionary['run']['VBG']` returns 'running'
2. converted OntoNotes 5.0 from PTB to CoNLL-U (A script provided by Stanford CoreNLP was used)
3. augmented OntoNotes 5.0 by injecting grammar errors, using the above dictionary as a lookup table
    - given that grammar errors could be detected by just finding a dependency relation and comparing POS tags...
        - for each grammar error of interest, we looked for the specific dependency relation it could be identified by in the corpus
        - then, we changed the POS of one word of the dependency relation to exactly model the desired grammar error
        - we did this for about 35% of the corpus, copying and appending it to the original dataset.
        - by using OntoNotes 5.0 as a baseline, the model understands both grammatical sentences and common mistakes
4. converted augmented data into spaCy binary and trained their POS tagger and dependency parser on the augmented data
5. finally, we have a model capable of producing correct POS tags and dependency trees for both grammatical sentences and sentences with our desired grammar errors
    - from here, simply enforce rules by comparing the POS tags of a specific dependency relation

### how can i use it?
follow the exact same steps as we did to build the English model
- if you want a new language, you need a different corpus
- if you want new grammar rules, you need to train the model on them as we did in step 3
