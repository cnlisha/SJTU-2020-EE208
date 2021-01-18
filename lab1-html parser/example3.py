# SJTU EE208

import re
import sys
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


def parseZhihuDaily(content, url):
    zhihulist = list()
    
    soup = BeautifulSoup(content, features="html.parser")
    for i in soup.findAll(name='div',attrs={'class': 'wrap'}):
        con = i.contents[0].contents[0]
        link = urllib.parse.urljoin(url,con.get('href',''))
        con2 = con.contents[0]
        con3 = con.contents[1]
        lis = [con2.get('src'), con3.get_text(), link]
        zhihulist.append(lis)

    return zhihulist


def write_outputs(zhihus, filename):
    file = open(filename, "w", encoding='utf-8')
    for zhihu in zhihus:
        for element in zhihu:
            file.write(element)
            file.write('\t')
        file.write('\n')
    file.close()


def main():
    url = "http://daily.zhihu.com/"
    content = urllib.request.urlopen(url).read()
    zhihus = parseZhihuDaily(content, url)
    write_outputs(zhihus, "result3.txt")


if __name__ == '__main__':
    main()
