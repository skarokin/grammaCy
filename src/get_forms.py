# a class to get different forms of a word given its lemma and tag
# constructor takes in a spaCy nlp object, a lemminflect import, and a word_forms import
# constructor is like this because we want to prevent latency of loading these objects for every request
class GetForms():
    def __init__(self, nlp, lemminflect, word_forms):
        self.nlp = nlp
        self.lemminflect = lemminflect
        self.word_forms = word_forms

    def get_forms(self, word: str, lemma: str, tag: str) -> str:
        word = word.lower()
        # if trying to convert adj to adv or vice versa, use word_forms library because lemminflect cannot convert between adj and adv
        if tag in ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']:
            forms = self.word_forms(lemma)
            for p in forms:
                for w in forms[p]:
                    curr = self.nlp(w)[0]
                    # must enforce word is not the same... eg 'fast' is both an adjective and an adverb
                    if curr.tag_ == tag and curr.text != word:
                        print(f'Found {tag} form for {word}: {curr.text}')
                        return curr.text
            
            print(f'Could not find {tag} form for: {word}')
            return None
        # else, use lemminflect cause it's faster and more accurate
        form = self.nlp(lemma)[0]._.inflect(tag)
        if form != word:
            print(f'Found {tag} form for {word}: {form}')
            return form
        print(f'Could not find {tag} form for: {word}')
        return None