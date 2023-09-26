from db_handlers.db import db_session
from db_handlers.model import NewsTitle, NewsText, NewsSource, HaikuCatalog
from sqlalchemy.sql.expression import func, nullslast
from config import logging
import re

def get_one_putin_speech(title_id):
    query = db_session.query(NewsText).filter(NewsText.title_id == title_id).first()
    return query

def pu_speech_processed(news):
    # putin_news =get_one_putin_speech(news_title_id)
    full_text = news.split('\n')

    start_of_speech_pattern = re.compile(r"^[А-Я]\..*:")
    putin_pattern = re.compile(r"^В.Путин:")

    putin_words = []
    putin_on = False
    for paragraph in full_text:
        find_putin = re.search(putin_pattern, paragraph)
        find_another = re.search(start_of_speech_pattern, paragraph)
        if find_another and not find_putin:
            putin_on = False
        elif find_putin or putin_on:
            putin_on = True
            putin_words.append(re.sub(putin_pattern, ' ', paragraph).strip())
            # print(f'Putin starts speaking:\n{paragraph}\n{"-"*50}')
    

    return ' '.join(putin_words)

def get_n_random_titles(n=20, min_len=30000):
    random_order = func.random()
    
    query = db_session.query(NewsText).filter(func.length(NewsText.news_full)>min_len).order_by(random_order).limit(n).all()
    
    return query

def get_news_by_title_id(title_id):
    query = db_session.query(NewsText).filter(NewsText.title_id == title_id).first()

    return query

def get_n_random_haikus(n=1):
    random_order = func.random()

    query = db_session.query(HaikuCatalog).order_by(random_order).limit(n).all()
    
    return [el.id for el in query]

def get_haiku_by_id(haiku_id):
    return db_session.query(HaikuCatalog).filter(HaikuCatalog.id == haiku_id).first()

if __name__ == '__main__':
    
    random_titles = [news.title_id for news in get_n_random_titles()]

    for title_id in random_titles:
        a = len(get_news_by_title_id(title_id).news_full)
        print(a)

    compost = pu_speech_processed(255)

    for line in compost.split('\n'):
        print(line)
    
    print('Hello world!')