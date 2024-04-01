# pyesl
hybrid (ml + rule-based) grammar checker using spaCy's dependency parser
- parse input sentence into dependency tree
- walk tree, enforce predefined grammar rules

although this paper (Grammar Checking with Dependency Parsing: A Possible Extension for LanguageTool) was not seen until well after development, the fixes to some of the problems encountered was inspired by it.

### primary goals
- hybrid grammar checking model will be deployed on cloud and available to use via web interface
- etl pipeline for analytics on grammar mistakes
- (if deemed possible) make a dataset that includes ungrammatical sentences; this would DRASTICALLY improve grammar checking performance and also allow us to use only the dependency parser without any extra hacks
