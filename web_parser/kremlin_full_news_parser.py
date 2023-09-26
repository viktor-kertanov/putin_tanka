import requests
from bs4 import BeautifulSoup
from db_handlers.db import db_session
from db_handlers.model import NewsTitle, NewsText
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import func, nullslast
from fake_useragent import UserAgent
import arrow
from config import logging
import unicodedata
from random import randint
import time

logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

def get_titles_to_parse():
    print(f'Starting db request')
    parsed_news = db_session.query(NewsText.title_id).all()
    all_titles = db_session.query(NewsTitle.id).all()
    
    parsed_ids = {parsed_id.title_id for parsed_id in parsed_news}
    all_titles_ids = {title.id for title in all_titles}
    
    print(f'Finishing db request')
    
    return list(all_titles_ids.difference(parsed_ids))

def parse_full_news(title_id: int):
    title_query = db_session.query(NewsTitle).filter(NewsTitle.id == title_id).first()
    photos_url = relevant_photos = f"{title_query.title_url}/photos"

    ua = UserAgent()
    NEWS_FULL_CONTENT = "div.entry-content"
    PHOTOS_DATA = "ul.photoset__list"
    
    with requests.Session() as session:
        headers = {"user-agent": ua.random}
        print(f'Sending request to {title_query.title_url}')
        req = session.get(title_query.title_url, headers=headers)
        soup = BeautifulSoup(req.content, "html.parser")
        
        #extracting full text of the news
        news_content = soup.select_one(NEWS_FULL_CONTENT)
        unwanted = news_content.select_one("div.read__bottommeta")
        unwanted.extract()

        news_text = [el.text.replace(u'\xa0', u' ') for el in news_content.find_all("p")]
        news_text_full = '\n'.join(news_text) 
        
        #extracting full list of photo urls
        req = session.get(photos_url, headers=headers)
        soup = BeautifulSoup(req.content, "html.parser")
        
        try:
            photo_data = soup.select_one(PHOTOS_DATA).find_all("li", {"class": "photoset__item"})
            photo_urls = [photo.select_one("a.photo").get("href") for photo in photo_data]
            photo_urls_db = ','.join(photo_urls)
        except AttributeError:
            photo_urls_db = None
        

        print(f'The length of our text is {len(news_text_full)}')
        # print(news_text_full)
        return {
            "title_id": title_id,
            "news_full": news_text_full,
            "relevant_media_list": photo_urls_db
        }


def add_bulk_to_db(bulk_to_insert: list[dict]):
    try:
        db_session.bulk_insert_mappings(NewsText, bulk_to_insert, return_defaults=True)
        db_session.commit()
        print(f'Success: INSERTED a batch to db.')
    except SQLAlchemyError as e:
        print(f'Some error occurred: {e}')
        db_session.rollback()

def main_full_text_parser(limiter=5):
    titles_to_parse = get_titles_to_parse()[:limiter]

    news_data_bulk = []
    for title in titles_to_parse:
        news_data = parse_full_news(title)
        news_data_bulk.append(news_data)
    
    add_bulk_to_db(news_data_bulk)

    return None



if __name__ == '__main__':
    trial = 0
    while trial <= 5:
        try:
            for iteration in range(50):
                main_full_text_parser()
                print(f"Iteration # {iteration}. Now sleeping. Trial #{trial}.")
                time.sleep(randint(10,30))
        except TimeoutError:
            print(f'TimeOut Error on iteration #{iteration}.')
            trial+=1
    
    #FUNCTION TESTING WHERE TO PUT THAT?!
    # row1 = {
    #         "title_id": 1,
    #         "news_full": "aaaaaaa",
    #         "relevant_media_list": "dddddddd"
    #     }  
    # row2 = {
    #         "title_id": 2,
    #         "news_full": "bbbbb",
    #         "relevant_media_list": "cccccc"
    #     }
    # test = [row1, row2]
    # add_news_title_to_db(test)
    

    print('Hello world!')