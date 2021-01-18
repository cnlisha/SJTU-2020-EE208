# SJTU EE208

INDEX_DIR = "IndexFiles_2.index"

import sys, os, lucene, threading, time, re
from datetime import datetime
import jieba
import urllib.parse

from urllib.parse import urlparse
from bs4 import BeautifulSoup

from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField, TextField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version


"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

def getinfo(img):
    try:
        contents = img['alt']
    except:
        try:
            contents = str(img.parent.string)
        except:
            try:
                contents = str(img.parent.nextSibling.string)
            except:
                return None
    return contents


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = WhitespaceAnalyzer()
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def getTxtAttribute(self, contents, attr):
        m = re.search(attr + ': (.*?)\n',contents)
        if m:
            return m.group(1)
        else:
            return ''

    def indexDocs(self, root, writer):

        # 改编码格式
        filedic = {}
        fileindextxt = open('index_2.txt', "r", encoding='utf-8')
        for file_url in fileindextxt.readlines():
            file_url = file_url.split('\t')
            #print(file_url)
            try:
                filedic[file_url[1].strip()]= file_url[0].strip()   ##注意格式
            except:
                continue
        fileindextxt.close()

        # name, path
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed

        # contents
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                '''
                if not filename.endswith('.txt'):
                    continue
                '''
                
                try:
                    path = os.path.join(root, filename)
                    file = open(path) # ! encoding='utf8'
                    print("adding", filename)
                    contents = file.read()
                    
                    soup = BeautifulSoup(contents, features="html.parser")
                    try:
                        title = soup.head.title.string
                    except:
                        title = str(soup.title)[7:-8].strip()
                    # contents = ''.join(soup.findAll(text=True))
                    # img_seq_list = jieba.cut(contents)
                    # contents = " ".join(img_seq_list)
                    imgurls = soup.findAll('img')
                    file.close()

                    domain = urllib.parse.urlsplit(filedic[filename])[1].split(':')[0]
                    Title = urllib.parse.urlsplit(filedic[filename])[0]
                    
                    trans = Title + "://" + domain
                    for img in imgurls:
                        imgurl = img['src']
                        imgurl= urllib.parse.urljoin(trans, imgurl)

                        #print(imgsrc)
                        strs = getinfo(img)
                        img_seq_list = jieba.cut(strs)
                        contents = ' '.join(img_seq_list)
                        
                        doc = Document()
                        doc.add(Field("imgurl", imgurl, t1))
                        doc.add(Field("urltitle", title, t1))
                        #site = urlparse(filedic[filename]).netloc
                        doc.add(Field("url", filedic[filename], t1))

                        try:
                            if len(contents) > 0:
                                doc.add(Field("contents", contents, t2))
                            else:
                                contents = ''.join(soup.findAll(text=True))
                                img_seq_list = jieba.cut(contents)
                                contents = " ".join(img_seq_list)
                                doc.add(Field("contents", contents, t2))
                        except:
                            print("warning: no content in %s" % filename)
                        writer.addDocument(doc)

                except Exception as e:
                    print("Failed in indexDocs:", e)

if __name__ == '__main__':
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    lucene.initVM() # vmargs=['-Djava.awt.headless=true']
    print('lucene', lucene.VERSION)
    start = datetime.now()
    try:
        """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
                   """
        # analyzer = StandardAnalyzer()
        IndexFiles('html_2', "index_2")
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e
