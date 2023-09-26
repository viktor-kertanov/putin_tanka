from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from db_handlers.db import Base, engine

class NewsSource(Base):
    __tablename__ = 'news_sources'

    id = Column(Integer, primary_key=True)
    source_name = Column(String, unique=True)
    source_domain = Column(String, unique=True)

    news_title = relationship('NewsTitle', backref='news_source')

    def __repr__(self):
        return f'<Source id: {self.id}, source name: {self.source_name}, source domain: {self.source_domain}>'

class NewsTitle(Base):
    __tablename__ = 'titles'

    id = Column(Integer, primary_key=True)
    author = Column(String, nullable=True)
    original_title = Column(String, nullable=False)
    title_url = Column(String, unique=True)
    aux_url = Column(String, unique=False)
    source_id = Column(Integer, ForeignKey(NewsSource.id), nullable=False)
    date_published = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<News title: {self.original_title}, url: {self.title_url}>'

class NewsText(Base):
    __tablename__ = 'news_texts'

    id = Column(Integer, primary_key=True)
    title_id = Column(Integer, ForeignKey(NewsTitle.id), index=True)
    news_full = Column(Text, nullable=False)
    relevant_media_list = Column(String, unique=False, nullable=True)
    
    news_title = relationship('NewsTitle', backref='news_text')

    def __repr__(self):
        return f'<News id: {self.id}, news_title_id: {self.title_id}>'

class HaikuCatalog(Base):
    __tablename__ = 'haiku_catalog'

    id = Column(Integer, primary_key=True)
    haiku_text = Column(Text, nullable=False, unique=True)
    total_slbls = Column(Integer, nullable=False, unique=False)
    slbls_structure = Column(String, nullable=False, unique=False)
    pos_structure = Column(String, nullable=False, unique=False)

    def __repr__(self):
        return f'<Haiku id: {self.id}, haiku_text: {self.haiku_text}>'



if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)