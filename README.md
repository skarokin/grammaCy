# grammaCy
A customizable, multi-language grammar checking library that leverages machine learning techniques to improve rule-based grammar checking systems. 

Check out our fully-fledged English model [here]() with support for many grammar rules!

Some parts of this project are inspired by this paper from Maxim Mozgovoy ["Grammar Checking with Dependency Parsing: A Possible Extension for LanguageTool"](https://mmozgovoy.dev/papers/mozgovoy11b.pdf)

### Whats the point?
Rule-based systems are fast, easy to debug, generate detailed suggestions, and can be developed by a linguist with little to no programming knowledge. However, strictly rule-based systems struggle to keep up with the nuances of natural language, thus developing a comprehensive rule set takes too much time. By leveraging dependency parsing and POS tagging, the nuances of natural language are mitigated. As such, the time to develop a comprehensive rule set is reduced, and the rules performs better across the many exceptions to grammar rules.  

### How it works
- Run an input sentence through a POS tagger and dependency parser, generating the synctatic relations between words and the context-based part of speech of each word.
- Enforce user-defined grammar rules by comparing the POS tags of a specified dependency relation's head and child.
    - Note that some rules such as subject-verb-object order do not require the use of the dependency tree.

### How was the English model made?
1. Found a [library](https://github.com/gutfeeling/word_forms/tree/master) that mapped English word lemmas to all of their different forms. This formed the basis for generating suggestions.
    - I had to fork and make a modification to ensure that it was thread-safe.
    - Later on, I used `lemminflect` in place of this library, and only used the `adj_to_adv.txt` mapping provided from the above library.
2. Converted OntoNotes 5.0 from PTB to CoNLL-U. A script provided by Stanford CoreNLP was used.
3. Augmented OntoNotes 5.0 by injecting grammar errors.
    - Given that grammar errors could be detected by just finding a dependency relation and comparing POS tags...
        - For each grammar error of interest, we looked for the specific dependency relation it could be identified by in the corpus.
        - Then, we changed the POS of either the head or the child of the dependency relation to exactly model the desired grammar error.
4. Converted augmented data into `.spacy.` and trained Tok2Vec, POS tagger, dependency parser, and morphologizer components.
    - We need to identify ungrammatical sentences thus had to train our own Tok2Vec component instead of using pretrained models. This also meant our model ended up very small! (17 mb compared to 1.25 gb).
    - Note that we trained many times with many different hyperparameters and augmented datasets...
6. Finally, we have a model capable of producing correct POS tags and dependency trees for both grammatical sentences and sentences with our desired grammar errors.
    - From here, simply enforce rules by comparing the POS tags of a specific dependency relation or by calling some function on the parsed and tagged input.

### How can I use this for my own grammar rules/language?
- Gather a PTB or CoNLL-U corpus for your language of choice
    - If using PTB (constituency parse) data, you need to use `constituency2dependency.py` in the `preprocessing/` directory
- Augment your data on grammar errors you wish to identify by using `conllu_augmentor.py` (multithreaded and multiprocessed) in the `preprocessing/` directory
    - You can use `conllu_augmentor_singlethread.py` or `conllu_augmentor_multiprocess.py` depending on your system requirements. Note that these files are incomplete, though and will not give you the same reuslts as `conllu_augmentor.py`
    - I highly recommend that you first train Tok2Vec, POS tagger, dependency parser, and morphologizer components on the unaugmented data and do sandbox testing on what kind of grammatical errors the components have a hard time detecting. This not only gives you an idea of what kind of grammar errors you should introduce, but also what grammar errors you SHOULDN'T include as it may either be detrimental to your model performance or is already well captured given the current data
- Convert augmented data into `.spacy` format
    - Since this conversion takes a while to run, I highly recommend converting the unaugmented data into `.spacy` and keeping it saved, and if adjusting augmentations then only convert augmented files to `.spacy` to save yourself a bunch of time
- Train your model on augmented data
- Develop grammar rules based on the augmentations you introduced, and test your model! Repeat training or augmenting as required

### Main developers
- [Sean Kim](https://github.com/skarokin/)
- [Isaac Nguyen](https://github.com/akuwuh)
- [Pranshu Sarin](https://github.com/PranshuS27)
