import re, logging

from lxml import etree
from dianping.base import Font, get

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class Spider():
    def __init__(self, load_history=False):
        self.load_history = load_history
        self.font = Font(load_history=self.load_history)
        self.updateHeader()

    def updateHeader(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'Cookie': self.updateCookie()
        }

    def updateCookie(self):
        cookie = '_lxsdk_cuid=16ef3f978c7c8-03e993cb37663f-7711439-144000-16ef3f978c7c8; _lxsdk=16ef3f978c7c8-03e993cb37663f-7711439-144000-16ef3f978c7c8; _hc.v=e764d9f6-78c6-4cbf-9af9-f136390db5f9.1576051244; ua=%E9%99%AA%E4%BD%A0%E7%9C%8B%E6%B5%81; ctu=3bb4dd8363c72d6291ecc43b9857c32c2cecf66a8cf3466347f099025bd0a910; s_ViewType=10; _dp.ac.v=1074d0bf-318b-49b8-8960-65da0c0aca85; thirdtoken=58094ade-37ed-47d7-93d4-0394f6c6da9c; dper=df9e0a1b29c36d209c5991cac70ee17d0c8b1be59ac07cc82ed51b21b8d88b63f8f598039dad9116966fa89a408c01da27f5fd65768062a5a7507a11d0c87f4fb932b0865dac02bf160ffc1bff3f79bc9e21e1183fa4cdbf00a4344f0775a14d; ll=7fd06e815b796be3df069dec7836c3df; uamo=15565145853; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; dplet=cfe87cd327b481de3b10edeffb9edf73; cy=4; cye=guangzhou; _lxsdk_s=16fb710a9b3-667-e19-0f3%7C%7C688'
        return cookie

    def crawlData(self, url):
        response = get(url, headers=self.headers)
        if not self.load_history: self.parseFont(response)
        return self.parseData(response.text)

    def parseFont(self, response):
        logging.info('Load font...')
        html = etree.HTML(response.text)
        link = html.xpath('//link[@rel="stylesheet"][2]/@href')
        css = get('http:' + link[0])
        self.font.loadFontFromCSS(css.text)

    def parseData(self, text):
        shop_data = []
        lis = re.compile('<li class="" >(.*?)</li>', re.S).findall(text)
        for li in lis:
            html = etree.HTML(li)
            shop_id = html.xpath('//div[@class="tit"]/a/@data-shopid')
            shop_name = html.xpath('//div[@class="tit"]/a/@title')
            star = html.xpath('//div[@class="comment"]/span/@class')
            if shop_id: shop_id = shop_id[0]
            if shop_name: shop_name = shop_name[0]
            if star: star = int(star[0][-2:]) / 10

            comment = re.compile('<div class="comment">(.*?</div>)', re.S).findall(li)
            if comment:
                remarks = self.font.parseFont(re.compile('>(.*?)<').findall(
                    re.compile('<b(.*?)/b>\n条点评', re.S).findall(comment[0])[0]), font_type='shopNum')
                average_price = self.font.parseFont(re.compile('>(.*?)<').findall(
                    re.compile('人均\n.*<b(.*?)/b>', re.S).findall(comment[0])[0]), font_type='shopNum')
                average_price = average_price.replace('￥', '')

            tag_addr = re.compile('<div class="tag-addr">(.*?)</div>', re.S).findall(li)
            if tag_addr:
                tag = self.font.parseFont(re.compile('>(.*?)<').findall(
                    re.compile('<span class="tag"(.*?)/span>', re.S).findall(tag_addr[0])[0]), font_type='tagName')
                addr = self.font.parseFont(re.compile('>(.*?)<').findall(
                    re.compile('<span class="tag"(.*?)/span>', re.S).findall(tag_addr[0])[1]), font_type='tagName')
                address = self.font.parseFont(re.compile('>(.*?)<').findall(
                    re.compile('<span class="addr">(.*?)</span>', re.S).findall(tag_addr[0])[0]), font_type='address')

            # taste_score = self.font.parseFont(re.compile('>(.*?)<').findall(
            #     re.compile('<span >口味(.*?)</span>', re.S).findall(li)[0]), font_type='shopNum')
            # surrounding_score = self.font.parseFont(re.compile('>(.*?)<').findall(
            #     re.compile('<span >环境(.*?)</span>', re.S).findall(li)[0]), font_type='shopNum')
            # service_score = self.font.parseFont(re.compile('>(.*?)<').findall(
            #     re.compile('<span >服务(.*?)</span>', re.S).findall(li)[0]), font_type='shopNum')
            recommend = html.xpath('//div[@class="recommend"]/a/text()')
            if recommend: recommend = '/'.join(recommend)
            shop = {'shop_id': shop_id, 'shop_name': shop_name, 'star': star, 'remarks': remarks,
                    'average_price': average_price, 'tag': tag, 'addr': addr, 'address': address,
                    # 'taste_source': taste_score, 'surrounding_score': surrounding_score, 'service_score': service_score,
                    'recommend': recommend}
            shop_data.append(shop)
        return shop_data


url = 'https://www.dianping.com/search/keyword/2/0_%E5%91%B3%E5%8D%83%E6%8B%89%E9%9D%A2'
s = Spider().crawlData(url)
for i in s: print(i)