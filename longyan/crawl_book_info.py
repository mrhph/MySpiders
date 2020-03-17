import re

from fake_useragent import UserAgent
from lxml import etree

from longyan.utils import session

headers = {
    'User-Agent': UserAgent(use_cache_server=False).random,
}

# 代理，换成自己的，切记如果拉副本同时跑，一个副本里要放新的代理，不要和其他的重复
# 如果同一个副本里先跑url在跑书的信息，代理这个可以和跑url的一样，因为那个执行外才执行这个，不影响使用
proxies = {
    'http': 'http://H5S88F107UL200DD:DF87F2134F0F265B@http-dyn.abuyun.com:9020',
    'https': 'http://H5S88F107UL200DD:DF87F2134F0F265B@http-dyn.abuyun.com:9020'
}
# proxies = {}


def book_info(url):
    response = session.get(url, headers=headers, proxies=proxies)
    html = etree.HTML(response.text)
    book = {}
    source = html.xpath('//div[@class="leftnav_tu"]')[0]
    source_str = etree.tostring(source, encoding='utf-8').decode()
    ssn = re.compile('ssn=(.*?)&', re.S).findall(response.text)
    book['source'] = source_str
    book['title'] = source.xpath('//div[@class="tutilte"]/text()')[0].strip()
    try:
        book['ssn'] = ssn[0]
    except:
        book['ssn'] = ''
    try:
        book['desc'] = source.xpath('//div[@class="tu_content"]/br')[0].tail.strip()
    except:
        book['desc'] = ''
    try:
        book['read'] = 'http://book.ucdrs.superlib.net' + source.xpath('//div[@class="testimg"]/a/@href')[0].strip()
    except:
        book['read'] = ''
    try:
        book['img'] = source.xpath('//div[@class="tubookimg"]/img/@src')[0]
    except:
        book['img'] = ''
    book['url'] = url
    book['series'] = ''
    for item in source.xpath('//dl/dd/text()'):
        item = item.strip()
        if '作　者' in item:
            book['author'] = item.split('】')[1].strip()
        elif '丛书' in item:
            book['series'] = item.split('】')[1].strip()
        elif '形态项' in item:
            book['page'] = item.split('】')[1].replace('\t', '').replace('\r', '').replace('\n', '').strip()
        elif 'ISBN号' in item:
            book['isbn'] = item.split('】')[1].replace('-', '').strip()
        elif '出版项' in item:
            try:
                book['publishing'] = item.split('】')[1].split(',')[0].replace('\t', '').replace('\r', '').replace('\n', '').strip()
                book['publish_time'] = item.split('】')[1].split(',')[1].strip()
            except:
                book['publishing'] = item.split('】')[1]
                book['publish_time'] = ''
        elif '中图法分类号' in item:
            book['code'] = item.split('】')[1].strip()
        elif '原书定价' in item:
            book['price'] = item.split('】')[1].strip()
        elif '主题词' in item:
            book['theme'] = item.split('】')[1].strip()
        elif '参考文献格式' in item:
            book['literature'] = item.split('】')[1].replace('\t', '').replace('\r', '').replace('\n', '').strip()
    return book


if __name__ == '__main__':
    url = 'http://book.ucdrs.superlib.net/views/specific/2929/bookDetail.jsp?dxNumber=000007964749&d=5A7C851E0A7AE3BA2539826AE7931C83&fenlei=02040102'
    print(book_info(url))