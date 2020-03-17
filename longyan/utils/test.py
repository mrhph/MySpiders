f = open('url.txt', 'r', encoding='utf-8')

import re

url_set = set()

for url in f.readlines():
    pattern = re.compile('dxNumber=(.*?)&', re.S)
    dx = pattern.findall(url)[0]
    if dx in url_set:
        continue
    url_set.add(dx)

print(len(url_set))