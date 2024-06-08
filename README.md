# grammaCy
A customizable, multi-language grammar checking library that leverages dependency parsing to improve rule-based grammar checking systems. 
- [Here](https://github.com/akuwuh/grammacy-api) is our Flask endpoint for a fully developed English model with a comprehensive rule set.
- [Here]() is our website to try out the above model, with more comprehensive documentation and a dev blog. 

Some parts of this project are inspired by this paper from Maxim Mozgovoy ["Grammar Checking with Dependency Parsing: A Possible Extension for LanguageTool"](https://mmozgovoy.dev/papers/mozgovoy11b.pdf)

### What's the point?
Rule-based grammar checkers are desirable because they are...
- Fast, as they either do not use machine learning at all or use extremely lightweight models like POS tagging.
- Can generate meaningful suggestions since the violated rule is exactly known.
- Can be developed by a linguist with little to no programming experience.

However, these systems cannot capture the nuances of natural language, thus significant manual effort is required to develop a comprehensive rule set to capture the many exceptions to grammar rules.

We address this major pitfall by introducing dependency parsing. By leveraging the extra context given by a dependency parser, we improve the performance of rule-based checks and reduce manual effort as exceptions are accounted for.

Why not statistical models?
- They are slow, heavy, transformer-based models that are not suited for real-time grammar checking.
- They do not provide meaningful suggestions.
- They are more suited towards spelling correction and enforcing good writing style.

### How it works
- Run an input sentence through a POS tagger and dependency parser, generating the synctatic relations between words and the part of speech of each word.
- Enforce user-defined grammar rules by analyzing the POS tags of a specified dependency relation's head and child.
    - Every dependency relation has a 'whitelist' of grammatical head and child tags. Simply check if the tags are in the whitelist!
    - Note that we incorporated some rules such as subject-verb-object order. These do not require use of the dependency tree and had to be implemented as a separate function.

### How was the English model made?
1. Used [LemmInflect](https://github.com/bjascob/LemmInflect) to generate different forms of a word under the same part of speech.
    - To do adjective<->adverb conversion, the `adj_to_adv.txt` file from [this library](https://github.com/gutfeeling/word_forms/tree/master) was used.
2. Converted OntoNotes 5.0 from PTB constituency parse format to CoNLL-U dependency parse format. A script provided by Stanford CoreNLP was used.
3. Augmented OntoNotes 5.0 by injecting grammar errors, using step 1 as a basis for augmentation.
    - Given that grammar errors could be detected by just finding a dependency relation and comparing POS tags...
        - For each grammar error of interest, we looked for the specific dependency relation it could be identified by in the corpus.
        - Then, we changed the POS of either the head or the child of the dependency relation to exactly model the desired grammar error.
4. Converted augmented data into `.spacy` files and trained the Tok2Vec, POS tagger, dependency parser, and morphologizer components.
    - We had to train our own Tok2Vec component because pretrained vectors (like `en_core_web_lg`) were only trained on grammatical sentences.
6. Finally, we have a model capable of producing correct POS tags and dependency trees for both grammatical sentences and sentences with our desired grammar errors.
    - From here, simply develop a comprehensive rule set!
    - Generating suggestions is simple; use step 1.

**NOTE:** It's extremely important to ensure that the model is trained on both grammatical and ungrammatical data. If the model was only trained on grammatical data, it would always attempt to assign a grammatical sequence of POS tags and dependency relations
- For example, if adjective was used in place of an adverb, a model trained only on grammatical sentences would assign the adjective with an adverb part of speech. Thus, a rule-based check cannot work if the model cannot identify that this 'adverb' is actually a misplaced adjective.

### How can I use this for my own grammar rules/language?
- Clone the repository (this library is all about providing customizable tools for building a language-independent model and developing rules, so it is not a package).
- Gather a PTB or CoNLL-U corpus for your language of choice
    - If using PTB (constituency parse) data, you need to use `constituency2dependency.py` in the `preprocessing/` directory.
- Augment your data on grammar errors you wish to identify by using `conllu_augmentor.py` (multithreaded and multiprocessed) in the `preprocessing/` directory.
    - You can use `conllu_augmentor_singlethread.py` depending on your system requirements. Note that this file is incomplete, though.
    - I highly recommend that you first do sandbox testing on pretrained models provided by spaCy. This not only gives you an idea of what kind of grammar errors you should introduce due to the faults of the pretrained model, but also what grammar errors you SHOULDN'T include as it may either be detrimental to your model performance or is already well captured given the current data.
- Convert augmented data into `.spacy` format.
    - Since this conversion takes a while to run, I highly recommend converting the unaugmented data into `.spacy` and keeping it saved, and if adjusting augmentations then only convert augmented files to `.spacy` to save yourself a bunch of time.
- Train your model on augmented data.
- Develop grammar rules based on the augmentations you introduced, and test your model! Repeat training or augmenting as required.

### Main developers
- [Sean Kim](https://github.com/skarokin/)
- [Isaac Nguyen](https://github.com/akuwuh)
- [Pranshu Sarin](https://github.com/PranshuS27)
