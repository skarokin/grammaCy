# checks if subject and verb agree in number and tense
# 1. if subject is singular/plural, verb must be singular/plural
# 2. if multiple subjects connected by 'and', verb must be plural (need custom matching for noun chunks)
# 3. if 1 subject and more than 1 verb, all verbs must be plural (need custom matching for verb phrases)
# 4. if a phrase comes between subject and verb, verb must still agree with subject
# 5. if two or more singular nouns/pronouns connected by 'or' or 'nor', verb must be singular
# 6. if compound subject is joined by 'or' or 'nor', verb agrees with closest subject
# 7. 'each', 'each one', 'either', 'neither', 'everyone', 'everybody', 'anyone', 'anybody', 'nobody', 
#    'somebody', 'someone', 'no one' are singular
# 8. noncount nouns are always singular
# 9. some countable nouns are explicitly plural, i.e. 'earnings' 'proceeds', 'goods', 'odds', ...
# 10. sentences with 'there is' or 'there are', verb (is/are) agrees with the noun that follows it
# 11. collective nouns are singular
# extra rules:
# - cannot add numbers to noncount nouns
