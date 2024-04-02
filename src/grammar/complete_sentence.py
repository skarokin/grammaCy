import spacy
nlp = spacy.load("en_core_web_sm")

sentences = ['I want to go home.',
             'Ted.',
            'I wish I could be there.']


def main(sentences):
  for s in sentences:
    if complete_sentence(s):
      print(f'{s} is complete\n')
    else:
      print(f'{s} is not complete\n')

def complete_sentence(sentence):
  doc = nlp(sentence)
  if doc[0].is_title and doc[-1].is_punct:
    has_noun = 2
    has_verb = 1
  for token in doc:
    if token.pos_ in ['NOUN', 'PROPN', 'PRON']:
      has_noun -= 1
    elif token.pos_ == 'VERB':
      has_verb -= 1
  if has_noun < 1 and has_verb < 1:
    return True
  return False

main(sentences)