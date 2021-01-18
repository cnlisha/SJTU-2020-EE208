# SJTU EE208

import re
import sys
import urllib.request

from bs4 import BeautifulSoup


def parseIMG(content):                  #爬取url
    urlset = set()                      #新集合
    soup = BeautifulSoup(content)
    for i in soup.findAll('img'):         #标签为a
        url = i.get('src','')          #抓取href
        urlset.add(url)                 #添加进集合
    return urlset


def write_outputs(urls, filename):
    file = open(filename, 'w', encoding='utf-8')
    for i in urls:
        file.write(i)
        file.write('\n')
    file.close()


def main():
    url = "http://www.baidu.com"
    content = urllib.request.urlopen(url).read()
    urlSet = parseIMG(content)
    write_outputs(urlSet, "result2.txt")


if __name__ == '__main__':
    main()