import urllib.request
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import BytesIO
from flask import Flask,redirect
from flask import request
from flask import render_template
import numpy as np
import os
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
import requests
import json
import base64
from summarizer import Summarizer
from summarizer.sbert import SBertSummarizer
import numpy as np
app = Flask(__name__)


@app.route('/summarise', methods=['GET','POST'])
def my_form_post():
    data = request.args
    data =data.get("text")
    
    if len(data)==0:
        return
    zz=data.split("/")[-1]
    zz=zz.split(".")[0]
    if(not(zz.isidentifier( ))):
            return render_template('output.html', message = "File Name must only contain alphnumeric characters")
    url = "https://www.africau.edu/images/default/sample.pdf"
    writer = PdfFileWriter()
    remoteFile = urllib.request.urlopen("https://iapportal.onrender.com"+data).read()
    memoryFile = BytesIO(remoteFile)
    pdfFile = PdfFileReader(memoryFile)
    data=""
    for pageNum in range(pdfFile.getNumPages()):
        currentPage = pdfFile.getPage(pageNum)
        #currentPage.mergePage(watermark.getPage(0))
        data+=currentPage.extractText()
    bert_model = SBertSummarizer("paraphrase-MiniLM-L6-v2")
    summary = bert_model(data, num_sentences=10)
    return redirect('FirstPage.html', message = summary)

@app.route('/plag', methods=['GET','POST'])
def my_form_post1():
    headers = {
    'Content-type': 'application/json'
    
    }
    
    myobj = json.dumps({'email':'email','key':'key'})
    datas = request.args
    data =datas.get("text")
    doc1=datas.get("text")
    response = requests.post('https://id.copyleaks.com/v3/account/login/api', headers=headers, data=myobj)
    response=response.json()
    if len(data)==0:
        return
    zz=data.split("/")[-1]
    zz=zz.split(".")[0]
    if(not(zz.isidentifier( ))):
            return render_template('output.html', message = "File Name must only contain alphnumeric characters")
    url = "https://www.africau.edu/images/default/sample.pdf"
    writer = PdfFileWriter()
    #remoteFile = urllib.request.urlopen(url).read()
    remoteFile = urllib.request.urlopen("https://iapportal.onrender.com/"+data).read()
    memoryFile = BytesIO(remoteFile)
    pdfFile = PdfFileReader(memoryFile)
    data=""
    for pageNum in range(pdfFile.getNumPages()):
        currentPage = pdfFile.getPage(pageNum)
        #currentPage.mergePage(watermark.getPage(0))
        data+=currentPage.extractText()
    data=data.encode("utf-8","ignore")
    dats=base64.b64encode(data)
    headers = {
    'Content-type': 'application/json',
    'Authorization': "bearer "+response["access_token"]
    }
    print(str(dats)[1:])
    print(response["access_token"])
    print(doc1)
    url='https://api.copyleaks.com/v3/scans/submit/file/dar'+doc1[1:5].lower() 
    url2='https://yoursite.com/webhook/{STATUS}/dar'+doc1[1:5].lower()
    myobj = json.dumps({'base64':str(dats)[2:-1],'filename':'file.pdf','properties':{"action":0,'webhooks':{'status':url2}}})  
    response = requests.put(url , headers=headers, data=myobj)
    print(response)
    return redirect('https://api.copyleaks.com/dashboard/scans')

if __name__ == '__main__':
    app.run(port="8081")
