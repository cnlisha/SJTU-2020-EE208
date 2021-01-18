# SJTU EE208

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time, re
from datetime import datetime
import jieba

from urllib.parse import urlparse
from bs4 import BeautifulSoup

from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField, TextField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.core import WhitespaceAnalyzer

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

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
        fileindextxt = open('index_1.txt', "r", encoding='utf-8')
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
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        # url
        t3 = FieldType()
        t3.setStored(True)
        t3.setTokenized(False)
        t3.setIndexOptions(IndexOptions.NONE)

        # site
        t4 = FieldType()
        t4.setStored(True)
        t4.setTokenized(False)
        t4.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        # title
        t5 = FieldType()
        t5.setStored(True)
        t5.setTokenized(False)
        t5.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                '''
                if not filename.endswith('.txt'):
                    continue
                '''
                
                try:
                    path = os.path.join(root, filename)
                    file = open(path, encoding='utf8')
                    print("adding", filename)
                    contents = file.read()
                    
                    soup = BeautifulSoup(contents, features="html.parser")
                    try:
                        title = soup.head.title.string
                    except:
                        title = str(soup.title)[7:-8].strip()
                    contents = ''.join(soup.findAll(text=True))
                    seg_list = jieba.cut(contents)
                    contents = " ".join(seg_list)

                    file.close()

                    doc = Document()

                    '''
                    doc.add(Field("name", filename, t1))
                    doc.add(Field("path", path, t1))
                    doc.add(Field("title", contents[1], t1))
                    doc.add(Field("url", contents[4], t1))

                    doc.add(Field("field", contents[0], t2))
                    doc.add(Field("feature", contents[2], t2))
                    doc.add(Field("content", content_str, t2))
                    '''
                    doc.add(Field("name", filename, t1))
                    doc.add(Field("path", path, t1))
                    
                    if len(contents) > 0:
                        doc.add(Field("contents", contents, t2))
                    else:
                        print("warning: no content in %s" % filename)
                    
                    site = urlparse(filedic[filename]).netloc
                    doc.add(Field("url", filedic[filename], t3))
                    doc.add(Field("site",site,t4))
                    doc.add(Field("title", title, t5))
                    
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
        IndexFiles('html_1', "index_1")
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e