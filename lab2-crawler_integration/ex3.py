# SJTU EE208

import os
import re
import time
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
import queue
import threading

from bs4 import BeautifulSoup


def valid_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def get_page(page):
    try:
        content = urllib.request.urlopen(page, timeout=10).read()
    except urllib.error.URLError:
        return None
    else:
        return content


def get_all_links(content, page):
    links = []
    soup = BeautifulSoup(content, 'lxml')
    for i in soup.findAll('a',{'href':re.compile('^http|^/')}):
        xiangdui = i['href']
        juedui = urllib.parse.urljoin(page,xiangdui)
        links.append(juedui)
    return links

def union_dfs(a, b):
    for e in b:
        if e not in a:
            a.append(e)


def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index2.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html2'  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    index = open(index_filename, 'a')
    index.write(page + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w')
    f.write(str(content))  # 将网页存入文件
    f.close()

count = 1

def working():
    global count
    while q and count < max_page:
        page = q.get()
        if page not in crawled:
            content = get_page(page)
            if content != None:
                add_page_to_folder(page, content)
                outlinks = get_all_links(content, page)
            for link in outlinks:
                q.put(link)
            if varLock.acquire():
                graph[page] = outlinks
                crawled.append(page)
                varLock.release()
            count += 1
            q.task_done()


start = time.time()
NUM = 4
crawled = []
graph = {}
varLock = threading.Lock()
q = queue.Queue()
seed = "https://www.sjtu.edu.cn"
q.put(seed)
max_page = 50
for i in range(NUM):
    t = threading.Thread(target=working)
    t.setDaemon(True)
    t.start()
    t.join()
end = time.time()
print(end - start)