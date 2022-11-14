from rusyll import rusyll
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("ru_core_news_sm")
file = "data/test_putin.txt"
doc = nlp(open(file).read())

matcher = Matcher(nlp.vocab)


# pattern = [{'POS':  {"IN": ["NOUN","ADJ"]} },
#            {'POS':  {"IN": ["NOUN","ADJ"]} }]

pattern = [
    {'POS':  {"IN": ["ADP"]}},
    {'POS':  {"IN": ["ADJ"]}},
    {'POS':  {"IN": ["NOUN"]}}
    ]
matcher.add("TwoWords", [pattern])

matches = matcher(doc)


for match_id,start,end in matches:
    print(doc[start:end])


if __name__ == '__main__':
    print('Hello world!')
    # test_word = "традиционные"
    # a = rusyll.word_to_syllables(test_word)
    # print(a)