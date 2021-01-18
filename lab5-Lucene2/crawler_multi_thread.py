# SJTU EE208

import threading
import queue
import time

import os
import re
import string
import sys
import urllib.error
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup

def valid_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def get_page(page):
    try:
        contenthtml =urllib.request.urlopen(page,timeout=100)
        #httpmessage = contenthtml.info()
        contenttype = contenthtml.headers['Content-type'][:9:1] ## content-type
        if "text/html" != contenttype:
            return None
        else:
            print('downloading page %s' % page)
            content = contenthtml.read().decode('utf-8','ignore')##预处理
            time.sleep(0.5)
    except:
        return None

    return content


def get_all_links(content, page):
    links = []
    soup = BeautifulSoup(content,features="html.parser")
    #匹配以http开头的绝对链接和以/开头的相对链接
    for i in soup.findAll('a',{'href':re.compile('^http|^/')}):
        urlrelative = i['href']
        urlabsolute = urllib.parse.urljoin(page,urlrelative)
        links.append(urlabsolute)
    return links

def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index_2.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html_2'  # 存放网页的文件夹 不需要额外再更改相对路经
    filename = valid_filename(page)  # 将网址变成合法的文件名
    index = open(index_filename, 'a')
    ###
    index.write(page + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w',encoding="utf-8") #w
    f.write(content)  # 将网页存入文件
    f.close()



def working():
    #退出条件
    while True and len(crawled)<=6000:
        page = q.get()
        # if varLock.acquire():
        if page not in crawled:
            # varLock.release()
            # else:
            # varLock.release()
            #print(page)
            content = get_page(page)
            if content != None:
                add_page_to_folder(page,content)
                outlinks = get_all_links(content,page)
                for link in outlinks:
                    q.put(link)
                if varLock.acquire():
                    graph[page] = outlinks
                    crawled.append(page)
                    varLock.release()
                q.task_done()


start = time.time()
NUM = 100      ## 100个

crawled = []
graph = {}
varLock = threading.Lock()
q = queue.Queue()
#q.put('A')
q.put('https://www.suning.com/')
thread_list_real = [] #是否并发初始化
for i in range(NUM):
    t = threading.Thread(target=working)
    thread_list_real.append(t)
print(thread_list_real)
for t in thread_list_real:
    t.setDaemon(True)
    t.start()
for t in thread_list_real:
    t.join()
# q.join()
end = time.time()
print(end - start)
