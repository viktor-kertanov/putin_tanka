from pdfminer.high_level import extract_text
import re

# pattern_reg = "\n* * *\n\n"
split_pattern = re.compile(r"(\s\s[\x0c]?\* \* \*\s\s)", re.DOTALL)

sub_pattern = re.compile(r"\n\n\d*\n.*")

a = 'Подле горного храма,\nчто дал мне сегодня приют,\nна веранде открытой\nиз сандалии старой твоей\nраздается пенье сверчка...\n\n12\nПоэзия танка \n* * *\n\nБерег песчаный.\nНа лодку рыбачью присев,\nтебе внимаю\xa0—\nэтой повестью о любви\nзачарован и опьянен...\n'

if __name__ == '__main__':
    book = extract_text('data/japan_haiku_tank_silver_age.pdf')
    book_replace = re.sub(sub_pattern, '', book)
    book_splitted = re.split(split_pattern, book_replace)

    haikus = []
    for haiku in book_splitted:
        new_lines = len(re.findall('\n', haiku))
        if new_lines >= 3 and new_lines <=5 and "* * *" not in haiku:
            haiku = haiku.replace('*','')
            print(haiku)
            print('-'*50)
            haikus.append(haiku)
    print("Hello world!")