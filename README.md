# pyesl
hybrid (ml + rule-based) grammar checker using spaCy's dependency parser
- parse input sentence into dependency tree
- walk tree, enforce predefined grammar rules

some parts of this project are inspired by 'Grammar Checking with Dependency Parsing: A Possible Extension for LanguageTool'.

### to-do
- make treebank augmentor to ensure that dependency relations are not changed when POS of a word is changed
    - e.g. if sentence has preposition + verb, change that verb to base form to ensure that the parser knows a preposition + base form verb is possible, and to not assign the base form verb as a noun or the preposition as something else

### primary goals
- hybrid grammar checking model will be deployed on cloud and available to use via web interface
- etl pipeline for analytics on grammar mistakes
