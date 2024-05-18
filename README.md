# grammaCy
A rule-based grammar checking library that leverages a dependency parser to address the problems of rule-based grammar checking. 

Check out a fully-built English model [here]
- In the future we will have a showcase for another language

Some parts of this project are inspired by this paper from Maxim Mozgovoy ["Grammar Checking with Dependency Parsing: A Possible Extension for LanguageTool"](https://mmozgovoy.dev/papers/mozgovoy11b.pdf)

### Whats the point?
Rule-based systems are desirable for their speed and flexibility. They can also generate detailed suggestions and are easy to debug, but they fail to keep up with the nuances of natural language. By using a dependency parser, we can ensure our rule-based system keeps up with the nuances of natural language, thus we have an accurate, fast, and flexible grammar checker that generates suggestions quickly and is easy to debug.

### How it works
- Run input sentence through a POS tagger and dependency parser
    - This accommodates for the nuances of natural language while leveraging the speed and flexibility of rule-based systems
- Enforce user-defined grammar rules by comparing the POS tags of a specified dependency relation's head and child
    - This allows us to quickly generate suggestions via a dictionary lookup without relying on another ML model

### How was the English model made?
1. Found a [library](https://github.com/gutfeeling/word_forms/tree/master) that mapped English word lemmas to all of their different forms
    - I had to fork and make a modification to ensure that it was thread-safe
2. Converted OntoNotes 5.0 from PTB to CoNLL-U (A script provided by Stanford CoreNLP was used)
3. Augmented OntoNotes 5.0 by injecting grammar errors, using the above library
    - Given that grammar errors could be detected by just finding a dependency relation and comparing POS tags...
        - For each grammar error of interest, we looked for the specific dependency relation it could be identified by in the corpus
        - Then, we changed the POS of either the head or the child of the dependency relation to exactly model the desired grammar error
        - We did this for about 35% of the corpus, copying and appending it to the original dataset.
4. Converted augmented data into spaCy binary and trained their POS tagger and dependency parser on the augmented data
5. Finally, we have a model capable of producing correct POS tags and dependency trees for both grammatical sentences and sentences with our desired grammar errors
    - From here, simply enforce rules by comparing the POS tags of a specific dependency relation

### How can I use this for my own use case?
Follow the exact same steps as we did to build the English model!
- If you want a new language, you need a different corpus
- If you want new grammar rules, you need to train the model on the error it is finding as we did in step 3

### Main developers
- [Sean Kim](https://github.com/skarokin/)
- [Isaac Nguyen](https://github.com/akuwuh)
- [Pranshu Sarin](https://github.com/PranshuS27)
