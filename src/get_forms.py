class GetForms():
    def __init__(self, nlp, lemminflect, ADJECTIVE_TO_ADVERB, ADVERB_TO_ADJECTIVE):
        self.nlp = nlp
        self.lemminflect = lemminflect
        self.ADJECTIVE_TO_ADVERB = ADJECTIVE_TO_ADVERB
        self.ADVERB_TO_ADJECTIVE = ADVERB_TO_ADJECTIVE

    # get the {tag} form of {word}
    def get_forms(self, word: str, tag: str) -> str:
        lemma = self.nlp(word)[0]._.lemma()
        word = word.lower()
        
        if tag in ['RB', 'RBR', 'RBS']:
            if word in self.ADJECTIVE_TO_ADVERB:
                form = self.ADJECTIVE_TO_ADVERB[word]
                print(f'Found {tag} form for {word}: {form}')
                return form
        elif tag in ['JJ', 'JJR', 'JJS']:
            if word in self.ADVERB_TO_ADJECTIVE:
                form = self.ADVERB_TO_ADJECTIVE[word]
                print(f'Found {tag} form for {word}: {form}')
                return form
        
        # other than adjective/adverb conversion, we don't need to convert cross-POS and can use lemminflect to convert within the same POS
        form = self.nlp(lemma)[0]._.inflect(tag)
        if form != word:
            print(f'Found {tag} form for {word}: {form}')
            return form
    
        print(f'Could not find {tag} form for: {word}')
        return None