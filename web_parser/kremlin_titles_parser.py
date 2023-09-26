'''
Module to parse  news titles from kremlin.ru transcripts. We don't parse full text of the news, but we have the original title,
we have the date of publish, we have the url to parse the full text in the future.
'''
import requests
from bs4 import BeautifulSoup
from db_handlers.db import db_session
from db_handlers.model import NewsTitle
from sqlalchemy.exc import SQLAlchemyError
from fake_useragent import UserAgent
import arrow
from config import logging
import unicodedata

logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

def get_max_parsed_page():
    '''Parsing only those pages that are not present in the NewsTitle model.'''
    parsed_pages = db_session.query(NewsTitle.aux_url).all()
    if parsed_pages:
        return max({int(page["aux_url"].split('/')[-1]) for page in parsed_pages})
    else:
        return 0

def parse_propaganda_title():
    ua = UserAgent()
    CONTENT_LOCATOR = 'div.entry-content'
    NEWS_TITLES_LOCATOR_PARENT = "h3"
    NEWS_TITLES_LOCATOR_CHILD = "hentry__title hentry__title_special"
    SOURCE_DOMAIN = "http://kremlin.ru"

    max_parsed_page = get_max_parsed_page()
    print(f'Our max parsed page from Kremlin.ru is: {max_parsed_page}.')
    
    while True:
        with requests.Session() as session:
            PUTIN_WORDS_URL = f"http://www.kremlin.ru/events/president/transcripts/page/{max_parsed_page+1}"
            headers = {"user-agent": ua.random}
            req = session.get(PUTIN_WORDS_URL, headers=headers)
            soup = BeautifulSoup(req.content, "html.parser")
            news_titles = soup.select_one(CONTENT_LOCATOR).find_all(NEWS_TITLES_LOCATOR_PARENT, {"class": NEWS_TITLES_LOCATOR_CHILD})

            news_titles_batch = []
            for idx, title in enumerate(news_titles, start=1):
                title_data = title.select_one("a")
                raw_date = title_data.select_one("time.published").text
                date_published = arrow.get(raw_date.replace(" года", ""), 'D MMMM YYYY, HH:mm', tzinfo='Europe/Moscow', locale='ru').to('utc').datetime
                
                row = {
                    "original_title": title_data.select_one('span.entry-title').text.replace(u'\xa0', u' '),
                    "author": "Отдел редакции официального сайта Президента России",
                    "title_url": f"{SOURCE_DOMAIN}{title_data.get('href')}",
                    "aux_url": PUTIN_WORDS_URL,
                    "date_published": date_published,
                    "source_id": 1,
                }
                news_titles_batch.append(row)
                print(f'Page {max_parsed_page+1}. News #{idx}. {row["original_title"]}.')     
        
            yield news_titles_batch
            max_parsed_page+=1


def add_news_title_to_db(bulk_to_insert: list[dict]):
    try:
        db_session.bulk_insert_mappings(NewsTitle, bulk_to_insert, return_defaults=True)
        db_session.commit()
        print(f'Success: INSERTED a batch to db.')
    except SQLAlchemyError as e:
        print(f'Some error occurred: {e}')
        db_session.rollback()

def main_add_n_pages_with_titles(n=1):
    news_title_bulk = parse_propaganda_title()
    for _ in range(n):
        add_news_title_to_db(next(news_title_bulk))

if __name__ == '__main__':
    main_add_n_pages_with_titles(n=10)
    
    print('Hello world!')