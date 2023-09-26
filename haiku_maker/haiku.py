from db_handlers.query import get_n_random_titles, get_n_random_haikus, get_haiku_by_id, pu_speech_processed, get_news_by_title_id
from haiku_parser.haiku_parser import OriginalHaiku
import spacy
from spacy.matcher import Matcher
from rusyll import rusyll
from random import choice

nlp = spacy.load("ru_core_news_md")




if __name__ == '__main__':
    aux_pos = ['PUNCT', 'CCONJ', 'DET', 'CONJ', 'ADP', 'PRON', 'PART', 'INTJ', 'SCONTJ', 'PROPN']

    # compost_query = get_n_random_titles(n=10, min_len=20000)
    compost_query = [get_news_by_title_id(330)]
    print(f'Compost obtained')

    haiku_text = get_haiku_by_id(250).haiku_text
    haiku = OriginalHaiku(haiku_text)
    first_haiku_word = haiku_text.split(" ")[0]
    last_haiku_word = haiku_text.split(" ")[-1]
    haiku_data = haiku.get_haiku_data()

    slbls = [int(el) for el in haiku.slbls_structure.split('-')]
    pos = [line.split('-') for line in haiku.haiku_pos_structure_alt.split('==')]
    total_slbls = haiku.total_slbls

    if len(pos) != len(slbls):
        raise

    line_bound = zip(slbls, pos)
    
    patterns = []
    haiku = {}
    haiku_randomizer = []
    for line_idx, line in enumerate(line_bound):
        haiku[line_idx], haiku_randomizer_line, patterns = [], [], []
        main_patterns = [
                {"POS":  {"IN": [el]}}
                if el not in aux_pos
                else {"POS":  {"IN": [el]}, "OP": "*"}
                for el in line[1]
                ]

        for pattern in main_patterns:
            for aux in aux_pos:
                patterns.append({"POS":  {"IN": [aux]}, "OP": "*"})
            patterns.append(pattern)
            {"POS":  {"IN": ["PUNCT"]}, "OP": "*"}
        

        for compost in compost_query:
            pu_text = pu_speech_processed(compost.news_full)
            nlp_doc = nlp(pu_text)
            matcher = Matcher(nlp.vocab)
            matcher.add("strict_matches", [patterns])
            matches = matcher(nlp_doc)
            for_haiku = []
            for match_id, start, end in matches:
                phrase_match = nlp_doc[start:end]
                pharse_context = nlp_doc[(start-2):(end+2)]
                try:
                    slbls = rusyll.word_to_syllables(phrase_match.text)
                    slbls_count = len(slbls)
                except:
                    slbls, slbls_count = 0, 0
                
                if abs(slbls_count - line[0]) <= 0:
                    haiku[line_idx].append(
                        {
                            "pharse_match": phrase_match,
                            "slbls_count": slbls_count,
                            "slbls_target": line[0],
                            "pos": line[1],
                            "news_id": compost.id,
                            "news_title": compost.news_title.original_title,
                            "news_published": compost.news_title.date_published,
                            "phrase_context": pharse_context
                        }
                    )
                    haiku_randomizer_line.append(phrase_match)
                    # print(f'''Match: {phrase_match} ::: Syllables: {slbls_count} POS: {line[1]}.
                    # News: {compost.news_title.original_title}. Pub: {compost.news_title.date_published}.
                    # Context: {pharse_context}''')
        haiku_randomizer.append(haiku_randomizer_line)
    
    for _ in range(200):
        for line in haiku_randomizer:
            print(choice(line))
        print('-'*50)

    # haiku_brochure = {}
    # for line_idx, slbl_count in enumerate(haiku_slbls):


    print('Hello world!')