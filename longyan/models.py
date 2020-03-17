from sqlalchemy import Column, String , Integer, BIGINT, TEXT, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

now = datetime.now()

Base = declarative_base()

engine = create_engine('mysql+pymysql://spider8026046:Hph!123456@192.168.79.126/spider_test?charset=utf8')
# engine = create_engine('mysql+pymysql://root:hph1314@47.100.48.93:3306/1919?charset=utf8')
DBSession = sessionmaker(bind=engine)

class Book(Base):
    # __tablename__指的是数据库的表名，每一个副本用不同的表名
    # 这个命名不要和其它的表名冲突
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    # type_code = Column(String(10))
    title = Column(String(200))  # 书名
    author = Column(String(200))  # 作者
    series = Column(String(200))  # 丛书
    page = Column(String(100))  # 页数
    publishing = Column(String(200))  # 出版社
    publish_time = Column(String(50))  # 出版时间
    isbn = Column(String(100))  # isbn号
    code = Column(String(100))
    ssn = Column(String(100))  # ssn
    price = Column(String(100))  # 价钱
    theme = Column(String(255))  # 主题
    literature = Column(String(255))  # 参考文献格式
    desc = Column(TEXT)  # 描述
    url = Column(String(255))
    read = Column(String(255))
    img = Column(String(255))
    source = Column(TEXT)

session = DBSession()

def clean(book):
    keys = ['title', 'author', 'series', 'page', 'publishing', 'publish_time', 'isbn', 'code', 'price',
            'theme', 'literature', 'desc', 'url', 'read', 'img', 'source']
    for key in keys:
        try:
            book[key]
        except KeyError:
            book[key] = ''
    return book

def save_db(book):
    book = clean(book)
    b = Book(
    title = book['title'],  # 书名
    author = book['author'],  # 作者
    series = book['series'],  # 从书名
    page = book['page'],  # 页数
    publishing = book['publishing'],  # 出版社
    publish_time = book['publish_time'],  # 出版时间
    isbn = book['isbn'],  # isbn号
    code = book['code'],  # 中图法编号
    price = book['price'],  # 价钱
    theme = book['theme'],  # 主题
    literature = book['literature'],  # 参考文献格式
    desc = book['desc'],  # 简介
    url = book['url'],  # 书的url
    read = book['read'],  # 试读的url
    img = book['img'],  # 图片链接
    source = book['source']  # 网页源码
    )
    session.add(b)
    session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)