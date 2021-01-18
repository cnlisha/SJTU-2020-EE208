# SJTU EE208
import sys, os, lucene
from flask import Flask, redirect, render_template, request, url_for

from java.io import File, StringReader
from java.nio.file import Path
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause

from org.apache.lucene.search.highlight import SimpleHTMLFormatter, QueryScorer, Highlighter, SimpleSpanFragmenter

import jieba


"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""


def run(searcher, analyzer, command):
    title_list = []
    url_list = []
    content_list = []
    command = ' '.join(jieba.cut(command))
    query = QueryParser("content", analyzer).parse(command)
    scoreDocs = searcher.search(query, 20).scoreDocs
    HighlightFormatter = SimpleHTMLFormatter('<span style="color:red; font-weight:bold;">','</span>')
    query_score = QueryScorer (query)
    highlighter = Highlighter(HighlightFormatter, query_score)
    fragmenter  = SimpleSpanFragmenter(query_score, 32)
    highlighter.setTextFragmenter(fragmenter)

    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        title_list.append(doc.get('title')) #网站标题
        # name_list.append(doc.get('name')) #文件名
        url_list.append(doc.get('url')) #url

        text = doc.get('content')
        ts = analyzer.tokenStream('content', StringReader(text))
        content_list.append(highlighter.getBestFragments(ts, text, 1, "..."))
    return [title_list, url_list, content_list]


app = Flask(__name__)

@app.before_first_request
def load_index():
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        


@app.route('/', methods=['POST','GET'])
def keyword():
    if request.method =='POST':
        keyword = request.form['keyword']
        return redirect(url_for('result', keyword=keyword))
    return render_template('search.html')

@app.route('/result', methods=['GET'])
def result():
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    # print('lucene', lucene.VERSION)
    # base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer()

    keyword = request.args.get('keyword')
    data_list = run(searcher, analyzer,keyword)
    name_list = data_list[0]
    url_list = data_list[1]
    content_list = data_list[2]
    num = len(name_list)
    del searcher
    return render_template('result.html', keyword= keyword, name_list= name_list, url_list= url_list, content_list =content_list, num=num)

if __name__ == '__main__':
    STORE_DIR = "index"
    app.run(debug=True, port=8080)
