from re import search
from threading import local
from flask import Flask, redirect, render_template, request, url_for
import sys, os, lucene, jieba
from java.io import File
from java.io import StringReader
from java.nio.file import Path
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.search.highlight import Highlighter, SimpleHTMLFormatter, QueryScorer, SimpleSpanFragmenter
from org.apache.lucene.analysis.standard import StandardAnalyzer


def parseCommand(command):
    allowed_opt = ['site']
    command_dict = {}
    opt = 'contents'
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = command_dict.get(opt, '') + ' ' + value
        else:
            command_dict[opt] = command_dict.get(opt, '') + ' ' + i
    return command_dict

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def search():
    return render_template('search.html')

@app.route('/result', methods = ['GET'])
def show():
    
    def run(searcher, analyzer, command):
        while True:
            if command == '':
                return
            
            command_dict = parseCommand(command)
            querys = BooleanQuery.Builder()
            for k,v in command_dict.items():
                if k == 'contents':
                    v = ' '.join(jieba.lcut_for_search(v))
                    query = QueryParser(k, analyzer).parse(v)
                    querys.add(query, BooleanClause.Occur.MUST)
                else:
                    query = QueryParser(k, analyzer).parse(v)
                    querys.add(query, BooleanClause.Occur.MUST)
            scoreDocs = searcher.search(querys.build(), 50).scoreDocs

            results = []
            query = QueryParser('contents', analyzer).parse(command_dict['contents'])
            HighlighterFormatter = SimpleHTMLFormatter('<font color="red">', '</font>')
            query_score = QueryScorer(query)
            highlighter = Highlighter(HighlighterFormatter, query_score)
            fragmenter  = SimpleSpanFragmenter(query_score, 100)
            highlighter.setTextFragmenter(fragmenter) 

            for scoreDoc in scoreDocs:
                doc = searcher.doc(scoreDoc.doc)
                contents = doc.get('contents')
                ts = analyzer.tokenStream('contents', StringReader(contents))
                results.append([doc.get('title'), doc.get('url'), highlighter.getBestFragments(ts, contents, 1, '...')])
            return results
    STORE_DIR = "index"
    try:
        vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    except:
        vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = WhitespaceAnalyzer()
    keyword = request.args.get('keyword')
    results = run(searcher = searcher, analyzer = analyzer, command = keyword)
    return render_template('result.html', keyword = keyword, results = results)

@app.route('/im', methods = ['POST', 'GET'])
def imsearch():
    return render_template('imsearch.html')

@app.route('/imresult', methods = ['GET'])
def imshow():

    def run(searcher, analyzer, command):
        while True:
            if command == '':
                return
            
            command = ''.join(jieba.cut(command))
            query = QueryParser("contents", analyzer).parse(command)
            scoreDocs = searcher.search(query, 50).scoreDocs
            results = []
            for scoreDoc in scoreDocs:
                doc = searcher.doc(scoreDoc.doc)
                results.append([doc.get('urltitle'), doc.get('url'), doc.get('imgurl')])
            return results
    STORE_DIR = "indeximg"
    try:
        vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    except:
        vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer()
    keyword = request.args.get('keyword')
    results = run(searcher = searcher, analyzer = analyzer, command = keyword)
    return render_template('imresult.html', keyword = keyword, results = results)


if __name__ == '__main__':   
    app.run(debug=True, port=8080)
