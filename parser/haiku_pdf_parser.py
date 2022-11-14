from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import re
import csv

def silver_age_haiku():
    haikus = []
    for page_layout in extract_pages('data/japan_haiku_tank_silver_age.pdf'):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text_el = element.get_text()
                new_lines = len(re.findall('\n', text_el))
                if new_lines >= 3 and new_lines <=5:
                    haikus.append(text_el.replace('*',''))

    return haikus[3:-59]

def markova_haiku():
    haikus = []
    for page_layout in extract_pages('data/Japan_haiku_tanka_Markova.pdf'):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text_el = element.get_text()
                new_lines = len(re.findall('\n', text_el))
                if new_lines >= 3 and new_lines <=5:
                    haikus.append(text_el.replace('*',''))

    return haikus[76:-67]

def save_to_csv(data):
    with open('haikus_catalog.csv', 'w') as f:
        write = csv.writer(f)
        write.writerows(data)

if __name__ == '__main__':
    book1 = silver_age_haiku()
    book2 = markova_haiku()
    haikus = book1+book2
    
    haikus_to_csv = [[el] for el in haikus]
    save_to_csv(haikus_to_csv)

    print('Hello world!')
