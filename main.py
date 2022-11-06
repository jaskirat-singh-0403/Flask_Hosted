import urllib.request
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import BytesIO
from flask import Flask
from flask import request
from flask import render_template
import numpy as np
import os
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def my_form_post():
    data = request.args
    data =data.get("text")
    
    if len(data)==0:
        return
    if(not(data.split("/")[-1].isalnum( ))):
            return render_template('output.html', message = "File Name must only contain alphnumeric characters")
    url = "https://www.africau.edu/images/default/sample.pdf"
    writer = PdfFileWriter()
    remoteFile = urllib.request.urlopen("https://iapportal.herokuapp.com/"+data).read()
    memoryFile = BytesIO(remoteFile)
    pdfFile = PdfFileReader(memoryFile)
    data=""
    for pageNum in range(pdfFile.getNumPages()):
        currentPage = pdfFile.getPage(pageNum)
        #currentPage.mergePage(watermark.getPage(0))
        data+=currentPage.extractText()
    stopwords = list(STOP_WORDS)
    
    doc1=data
    nlp =spacy.load('en_core_web_sm')
    
    docx = nlp(doc1)
    
    mytokens = [token.text for token in docx]
    
    word_freq={}
    for word in docx:
        if word.text not in stopwords:
            if word.text not in word_freq.keys():
                word_freq[word.text]=1;
                
            else:
                word_freq[word.text]+=1;
                
    max_freq=max(word_freq.values())

    for word in word_freq:
        word_freq[word]=(word_freq[word]/max_freq)     
        
    sentence_list = [ sentence for sentence in docx.sents]
    
    [w.text.lower() for t in sentence_list for w in t ]
    
    
    sentence_scores={}
    for sentence in sentence_list:
        for word in sentence:
            if word.text in word_freq.keys():
                if len(sentence.text.split(' ')) < 30:
                    if sentence not in sentence_scores.keys():
                        sentence_scores[sentence] = word_freq[word.text]
                    else:
                        sentence_scores[sentence] += word_freq[word.text]
                        
                        
    from heapq import nlargest
    
    sum_sentences = nlargest(8, sentence_scores, key=sentence_scores.get)
    
    final_sentences = [ w.text for w in sum_sentences ] 
    
    
    summary = ' '.join(final_sentences)
    
    print(len(doc1))
    print(len(summary))
    return render_template('output.html', message = summary)

if __name__ == '__main__':
    app.run()