import csv
import spacy
from spacy.matcher import Matcher
from rusyll import rusyll
from db_handlers.db import db_session
from db_handlers.model import HaikuCatalog
from sqlalchemy.sql.expression import func, nullslast
from sqlalchemy.exc import SQLAlchemyError

HAIKUS_CATALOG = 'data/haikus_catalog.csv'

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
        self.slbls_structure = '-'.join(slbls_structure)
        self.total_slbls = sum([int(el) for el in self.slbls_structure.split('-')])

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

def read_haiku_csv():
    with open(HAIKUS_CATALOG, mode='r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            haiku_text = row[0].replace(u'\xa0', u' ').strip()
            query = db_session.query(HaikuCatalog).filter(HaikuCatalog.haiku_text == haiku_text).first()
            if not query:
                yield haiku_text
            else:
                print(f'We already have the poem')
                yield None

def add_bulk_to_db(bulk_to_insert: list[dict]):
    try:
        db_session.bulk_insert_mappings(HaikuCatalog, bulk_to_insert, return_defaults=True)
        db_session.commit()
        print(f'Success: INSERTED a batch to db.')
    except SQLAlchemyError as e:
        print(f'Some error occurred: {e}')
        db_session.rollback()
        print(f'Rolled back')

def get_haiku_data(haiku_reader, limiter=5):

    haiku_bulk = []
    for _ in range(limiter):
        try:
            haiku_text = next(haiku_reader)
        except StopIteration:
            add_bulk_to_db(haiku_bulk)
        if not haiku_text:
            continue
        haiku = OriginalHaiku(haiku_text)
        haiku.get_haiku_data()

        haiku_row = {
            'haiku_text': haiku_text,
            'slbls_structure': haiku.slbls_structure,
            'pos_structure': haiku.haiku_pos_structure_alt,
            'total_slbls': haiku.total_slbls
                }
        haiku_bulk.append(haiku_row)
    if haiku_bulk:
        add_bulk_to_db(haiku_bulk)
    else:
        print(f'Our haiku bulk is empty')
    
    return haiku_bulk


if __name__ == '__main__':
    haiku_reader = read_haiku_csv()
    for _ in range(1000):
        get_haiku_data(haiku_reader)
    
    print('Hello world!')
            
