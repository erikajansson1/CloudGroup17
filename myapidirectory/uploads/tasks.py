#from celery import Celery
from glob import glob
import json

#app = Celery('tasks', broker ='pyamqp://guest@localhost//')

#@app.task

han_count = 0
hon_count = 0
hen_count = 0
den_count = 0
det_count = 0
denna_count = 0
denne_count = 0
unique_tweets = 0

def count(text_list):
    global han_count
    global hon_count
    global hen_count
    global den_count
    global det_count
    global denna_count
    global denne_count
    global unique_tweets
    for string in text_list:
        if string == "han":
            han_count += 1
        elif string == "hon":
            hon_count += 1
        elif string == "hen":
            hen_count += 1
        elif string == "den":
            den_count += 1
        elif string == "det":
            det_count += 1
        elif string == "denna":
            denna_count += 1
        elif string == "denne":
            denne_count += 1
    unique_tweets += 1

def create_result():
    result = {
        'Han': han_count,
        'Hon': hon_count,
        'Hen': hen_count,
        'Den': den_count,
        'Det': det_count,
        'Denna': denna_count,
        'Denne': denne_count,
        'Unique_tweets': unique_tweets
    }

    with open('output', 'w') as outfile:
        json.dump(result, outfile)
        outfile.write('\n')


def main():
    for file_name in glob('data/*'):
        data = open(file_name, 'r')
        textfile = data.read()
        json_list = textfile.splitlines()
        json_list = filter(None, json_list)
        for object in json_list:
            dict = json.loads(object)
            text = dict['text']
            text_list = text.split()
            count(text_list)
    create_result()

main()
