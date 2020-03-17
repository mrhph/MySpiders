import threading
import redis
import sys
import os
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)  # 将项目路径存入环境变量

from queue import Queue, Empty

from longyan.crawl_book_info import book_info
from longyan.models import save_db
from longyan.utils.log import logger

logging = logger('bookInfo')
book_url_queue = Queue()
book_info_queue = Queue()

class RedisUrl:
    def __init__(self):
        self.redis = redis.Redis(host='47.100.48.93', port=6379, db=0)
        self.name = 'quantu_url'

    def get_url(self):
        url = self.redis.spop(self.name)
        try:
            return url.decode('utf-8')
        except:
            return None

    def put_url(self, url):
        return self.redis.sadd(self.name, url)



class CrawlBookInfo(threading.Thread):
    """爬取书的信息"""
    def __init__(self, thread_name, red):
        super(CrawlBookInfo, self).__init__()
        self.thread_name = thread_name
        self.red = red

    def run(self):
        logging.info('爬取图书信息线程开启, thread *{}*  ==>RUN'.format(self.thread_name))
        while True:
            url = self.red.get_url()
            if url == None:
                logging.info('链接池URL读取完毕, thread：*{}* 关闭  ==>EXIT'.format(self.thread_name))
                return
            try:
                book = book_info(url)
                book_info_queue.put(book)
                time.sleep(0.3)
            except Exception:
                logging.error('URL 爬取失败，，重新放入链接池。。。。。。')
                self.red.put(url)


class SaveToDB(threading.Thread):
    """保存数据库"""
    def __init__(self, thread_name):
        super(SaveToDB, self).__init__()
        self.thread_name = thread_name

    def run(self):
        logging.info('数据保存线程开启, thread：*{}*   ==>RUN'.format(self.thread_name))
        while True:
            try:
                book = book_info_queue.get(timeout=10)
            except Empty:
                logging.info('数据保存完毕, thread：*{}* 关闭  ==>RUN'.format(self.thread_name))
                return
            try:
                save_db(book)
                logging.info('{} ==> SAVE'.format(book['title']))
            except Exception as e:
                logging.error('happen error in ==save data to DB==')
                logging.error('The reason is: {}'.format(e))


def main():
    try:
        red = RedisUrl()
    except:
        logging.info('连接 Redis 线程池失败，程序退出!!!')
        return
    logging.info('连接 Redis 线程池成功!!!')

    crawl_book_info_thread = []
    crawl_book_info_thread_name = ['Crawl book info thread 1', 'Crawl book info thread 2']
    for thread_name in crawl_book_info_thread_name:
        thread = CrawlBookInfo(thread_name, red)
        thread.start()
        crawl_book_info_thread.append(thread)

    save_data_thread = []
    save_data_thread_name = ['save one']
    for thread_name in save_data_thread_name:
        thread = SaveToDB(thread_name)
        thread.start()
        save_data_thread.append(thread)

    for thread in crawl_book_info_thread:
        thread.join()
    for thread in save_data_thread:
        thread.join()
    logging.info('程序退出！！！！！')


if __name__ == '__main__':
    main()