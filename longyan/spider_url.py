import re
import threading
import redis
import sys
import os
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir) 

from queue import Queue, Empty
from math import ceil
from fake_useragent import UserAgent
from lxml import etree

from longyan.utils import session
from longyan.utils.log import logger

logging = logger('bookUrl')

headers = {
    'User-Agent': UserAgent(verify_ssl=False, use_cache_server=False).random
}

# 代理，换成自己的，切记如果拉副本同时跑，一个副本里要放新的代理，不要和其他的重复
# 如果同一个副本里先跑url在跑书的信息，代理这个可以和跑url的一样，因为那个执行外才执行这个，不影响使用
proxies = {
    'http': 'http://H5S88F107UL200DD:DF87F2134F0F265B@http-dyn.abuyun.com:9020',
    'https': 'http://H5S88F107UL200DD:DF87F2134F0F265B@http-dyn.abuyun.com:9020'
}

# book_code存放书的分类的编码，爬取不同分类需要进行替换
# 比如 book_code = ['C0', 'C01', 'C02']
book_code = ['B0', 'B0-0', 'B01', 'B02', 'B03', 'B08', 'B1', 'B2', 'B20', 'B21', 'B22', 'B23', 'B24', 'B25', 'B26', 'B27', 'B3', 'B4', 'B5', 'B6', 'B7', 'B80', 'B81', 'B82', 'B821', 'B822', 'B822.9', 'B823', 'B824', 'B825', 'B829', 'B83', 'B84', 'B841', 'B842', 'B843', 'B844', 'B845', 'B845.1', 'B845.9', 'B846', 'B848', 'B848.1', 'B848.2', 'B848.3', 'B848.4', 'B848.5', 'B848.6', 'B848.8', 'B849', 'B9', 'B91', 'B92', 'B94', 'B95', 'B96', 'B97', 'B98', 'B99']

# 这里years不要改
years = ['2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006',
         '2005', '2004', '2003', '2002', '2001', '2000', '1999', '1998', '1997', '1996', '1995', '1994', '1993',
         '1992', '1991', '1990', '1980-1989', '1970-1979', '1960-1969', '100-1959']

code_queue = Queue()
for code in book_code:
    code_queue.put(code)

def get_count(url):
    """获取网页上的数量"""
    response = session.get(url, headers=headers, proxies=proxies)
    try:
        html = etree.HTML(response.text)
        b = html.xpath('//div[@id="searchinfo"]//span[@class="leftF"]//b/text()')[0]
        pattern = re.compile('(.*?)种', re.S)
        count = pattern.findall(b)[0].strip()
    except:
        return 1
    return int(count)

get_page = lambda count: ceil(count/50) if count <= 2000 else 40  # 将数量转换成页数

def get_url(url):
    """获取网页上书的详情的链接"""
    response = session.get(url, headers=headers, proxies=proxies, timeout=30)
    try:
        html = etree.HTML(response.text)
    except:
        return []
    url_list = html.xpath('//div[@class="books"]/ul/li/div[@class="divImg"]/a/@href')
    return ['http://book.ucdrs.superlib.net' + url for url in url_list]


class RedisUrl:
    def __init__(self):
        self.redis = redis.Redis(host='47.100.48.93', port=6379, db=0)
        self.redis.flushdb()
        self.name = 'quantu_url'

    def put_url(self, url):
        self.redis.sadd(self.name, url)


class CrawlBookUrl(threading.Thread):
    def __init__(self, thread_name, red):
        super(CrawlBookUrl, self).__init__()
        self.thread_name = thread_name
        self.red = red

    def run(self):
        logging.info('爬取URL线程开启, thread: *{}*  ==>RUN'.format(self.thread_name))
        while True:
            try:
                code = code_queue.get(timeout=5)
            except Empty:
                logging.info('URL爬取完毕线程退出, thread *{}*  ==>EXIT'.format(self.thread_name))
                return
            self.crawl_book_url(code)
            time.sleep(0.3)

    def crawl_book_url(self, code):
        u = 'http://book.ucdrs.superlib.net/advsearch?' \
              'Pages=1&cnfenlei={}&rn=50&ecode=utf-8&Sort=&channel=search#searchinfo'.format(code)
        count = get_count(u)
        logging.info('分类：{}， 统计：{}'.format(code, count))
        if count >= 2000:
            for i in range(0, len(years)):  # 年份
                y_url = 'http://book.ucdrs.superlib.net/advsearch?cnfenlei={}&rn=50&ecode=utf-8&adminid=&btype=' \
                        '&seb=0&pid=0&showc=0&fenleiID=&authid=0&sectyear={}#searchinfo'.format(code, years[i])
                y_count = get_count(y_url)
                logging.info('|{} {}| count: {}'.format(code, years[i], y_count))
                page = get_page(y_count)
                for p in range(1, page + 1):
                    url = 'http://book.ucdrs.superlib.net/advsearch?Pages={}&cnfenlei={}&sectyear={}&rn=50' \
                          '&ecode=utf-8&sectyear={}&Sort=&channel=search#searchinfo'.format(p, code, years[i], years[i])
                    for url in get_url(url):
                        self.red.put_url(url)
                        logging.info('|{} {}| {}'.format(code, years[i], url))
        else:
            page = get_page(count)
            for p in range(1, page + 1):
                url = 'http://book.ucdrs.superlib.net/advsearch?' \
                      'Pages={}&cnfenlei={}&rn=50&ecode=utf-8&Sort=&channel=search#searchinfo'.format(p, code)
                for url in get_url(url):
                    self.red.put_url(url)
                    logging.info('|{}| {}'.format(code, url))

def main():
    try:
        red = RedisUrl()
    except:
        logging.info('连接 Redis 线程池失败，程序退出!!!')
        return
    logging.info('连接 Redis 线程池成功!!!')

    crawl_book_url_thread = []
    crawl_book_url_thread_name = ['Crawl book url thread 1', 'Crawl book url thread 2']
    for thread_name in crawl_book_url_thread_name:
        thread = CrawlBookUrl(thread_name, red)
        thread.start()
        crawl_book_url_thread.append(thread)
    for thread in crawl_book_url_thread:
        thread.join()
    logging.info('程序退出！！！！！')


if __name__ == '__main__':
    main()