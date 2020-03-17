import re
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from lxml import etree
from fake_useragent import UserAgent
from longyan.utils import session

proxies = {
    'http': 'http://H5S88F107UL200DD:DF87F2134F0F265B@http-dyn.abuyun.com:9020',
    'https': 'http://H5S88F107UL200DD:DF87F2134F0F265B@http-dyn.abuyun.com:9020'
}
headers = {
    'User-Agent': UserAgent(use_cache_server=False).random,
}

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

book_code = ['B0', 'B0-0', 'B01', 'B02', 'B03', 'B08', 'B1', 'B2', 'B20', 'B21', 'B22', 'B23', 'B24', 'B25', 'B26', 'B27', 'B3', 'B4', 'B5', 'B6', 'B7', 'B80', 'B81', 'B82', 'B821', 'B822', 'B822.9', 'B823', 'B824', 'B825', 'B829', 'B83', 'B84', 'B841', 'B842', 'B843', 'B844', 'B845', 'B845.1', 'B845.9', 'B846', 'B848', 'B848.1', 'B848.2', 'B848.3', 'B848.4', 'B848.5', 'B848.6', 'B848.8', 'B849', 'B9', 'B91', 'B92', 'B94', 'B95', 'B96', 'B97', 'B98', 'B99']

def statistics_book_count():
    all = 0
    f = open('./data/count.txt', 'w', encoding='utf-8')
    for code in book_code:
        url = 'http://book.ucdrs.superlib.net/advsearch?' \
              'Pages=1&cnfenlei={}&rn=50&ecode=utf-8&Sort=&channel=search#searchinfo'.format(code)
        count = get_count(url)
        all += count
        print(code, count)
        f.write(code + ':  ' + str(count) + '\n')
    f.write('总计：{}'.format(all))
    f.close()


if __name__ == '__main__':
    statistics_book_count()