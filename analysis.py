import spacy
from spacy.matcher import Matcher
from rusyll import rusyll
from random import choice

nlp = spacy.load("ru_core_news_sm")

class OriginalHaiku:
    def __init__(self, haiku_text: str):
        self.haiku_text = haiku_text
        self.haiku_lines = [l.strip() for l in haiku_text.split('\n')]
        self.ru_vowels = {'а','е', 'ё', 'и','о','у','ы','э','ю','я'}
        self.haiku_pos_structure = []
    
    def get_haiku_data(self):

        haiku_data = []
        for l_idx, line in enumerate(self.haiku_lines):
            doc = nlp(line)
            line_data, line_pos_structure = [], []
            line_slbls = 0
            for word in doc:
                try:
                    slbls = rusyll.word_to_syllables(word.text)
                    vowels_in_word = set(word.text.lower().strip()).intersection(self.ru_vowels)

                    if vowels_in_word:
                        slbls_count = len(slbls)
                        line_slbls += slbls_count
                    else:
                        slbls_count, slbls = 0, 0
                except:
                    slbls_count, slbls = 0, 0
                
                word_data = {
                    "word": word.text,
                    "pos": word.pos_,
                    "slbls": slbls,
                    "slbls_count": slbls_count,
                    "letter_count": len(word.text)
                }
                
                
                line_data.append(word_data)

                if word.pos_ != 'SPACE':
                    line_pos_structure.append(word.pos_)
                
            
            haiku_data.append({l_idx: {"l_data": line_data, "line_slbls": line_slbls}})

            if line_pos_structure:
                self.haiku_pos_structure.append(line_pos_structure)
        
        self.haiku_data = haiku_data
        
        slbls_structure = [str(line[l_idx]['line_slbls']) for l_idx, line in enumerate(self.haiku_data)]
        self.slbls_count = '-'.join(slbls_structure)

        haiku_pos_structure_alt = []
        for line in self.haiku_pos_structure:
            alt_line = '-'.join(line)
            haiku_pos_structure_alt.append(alt_line)
        self.haiku_pos_structure_alt = '=='.join(haiku_pos_structure_alt)
        
        return haiku_data

def putin_input(pos_list, slbls_count_input=False, nlp_doc=False):
    
    file = "data/putin_input.txt"
    nlp_doc = nlp(open(file).read())

    matcher = Matcher(nlp.vocab)

    pattern = []
    for pos_idx, pos in enumerate(pos_list, start=1):
        p_intj =  {"POS": {"IN": ["INTJ"]}, "OP": "*"}
        p0 =  {"POS": {"IN": ["PRON"]}, "OP": "*"}
        p1 = {"POS":  {"IN": [pos]}}
        pattern.append(p0)
        pattern.append(p1) 
        pattern.append(p_intj)
        if pos_idx < len(pos_list):
            p2 = {"IS_PUNCT": True, "OP": "*"}
            p3 = {"POS": {"IN": ["ADP"]}, "OP": "*"}
            p4 =  {"POS": {"IN": ["PART"]}, "OP": "*"}
            p5 =  {"POS": {"IN": ["PRON"]}, "OP": "*"}
            p6 =  {"POS": {"IN": ["CCONJ"]}, "OP": "*"}
            pattern.append(p2)
            pattern.append(p3)
            pattern.append(p4)
            pattern.append(p5)
            pattern.append(p6)
    
    matcher.add("with_without_punct", [pattern])
    matches = matcher(nlp_doc)

    for_haiku = []
    for match_id, start, end in matches:
        word_match = nlp_doc[start:end]
        try:
            slbls = rusyll.word_to_syllables(word_match.text)
            slbls_count = len(slbls)
        except:
            slbls, slbls_count = 0, 0
        
        word_for_haiku_data = {
            "word_for_haiku": word_match.text,
            "slbls": slbls,
            "slbls_count": slbls_count

        }
        if slbls_count_input:
            if slbls_count == slbls_count_input:
                for_haiku.append(word_for_haiku_data)
        else:
            for_haiku.append(word_for_haiku_data)
    
    return for_haiku




if __name__ == '__main__':
    h_text = """Так много уже
у меня скопилось записок
с призывом твоим:
«Приходи поскорее в дюны!»
Вот и лето уже на исходе..."""
    first_haiku = OriginalHaiku(h_text)
    haiku_data = first_haiku.get_haiku_data()
    
    # putin_pickup = first_haiku.putin_words
    
    # for _ in range(5):
    #     final_haiku = []
    #     for place in putin_pickup:
    #         if place:
    #             final_haiku.append(choice(place))
        
    #     final_haiku_print = ' '.join(final_haiku)
    #     print(final_haiku_print)

    #Рабочие схемы
    # ['VERB','NOUN']
    # ['ADJ', 'NOUN']
    # ['PROPN', 'NOUN']
    # ['PRON', 'NOUN']
    # ['ADV', 'NOUN']
    # ['ADV', 'VERB']
    # ['NOUN', 'VERB']
    # ['NUM', 'NOUN']
    # ['VERB', 'ADV', 'DET', 'NOUN']

    '''
    И есть. Но не надо / Не получится и сейчас
    Благодарю вас за труд, поддержку / Переходить из руки в руки.
    белым порошком / грязное дело / западный блок / великая страна
    '''
    a = putin_input(['ADV', 'ADV', 'ADV'])
    b = putin_input(['ADP', 'PRON', 'VERB', 'NOUN'])
    с = putin_input(['ADP', 'NOUN', 'VERB', 'PUNCT'])

    print('Hello world!')