import requests
import sys
import json
from functions import Search
import re

def receivePara():
    msg = sys.argv[1]
    
    msg = eval(msg)

    if msg['todo'] == 'search':
        results = Search(msg['idx'], msg['label'])
        results = json.loads(results)['hits']['hits']
        table = {}

        for i, result in enumerate(results):
            del result['_source']['uniqueId']
            del result['_source']['fileName']
            table['col%s' % i] = result['_source']

        print(json.dumps(table))

    if msg['todo'] == 'searchLabel':
        uniqueId_list = []
        res = Search('table', 'all')
        res = json.loads(res)['hits']['hits']
        for ress in res:
            uniqueId_list.append(ress['_source']['uniqueId'])
        uniqueId_list = list(set(uniqueId_list))

        print(uniqueId_list)

    if msg['todo'] == 'savePath':
        with open('assets\\uploads\\originalName.txt', 'a+') as f:
            f.write(str(msg)+'\n')
            
    if msg['todo'] == 'showOri':
        f = open('assets\\uploads\\originalName.txt', 'r')
        info_list=[]
        for line in f.readlines():
            if re.search(msg['image'], line) != None:
                info = eval(line.split('\n')[0])
                info_list.append(info)
        print(json.dumps({'path':info_list[-1]['path']}))
    # sys.stdout.flush()


def returnData(url, data):
    x = requests.post(url, data)
    print(x.text)


receivePara()

#returnData('http://127.0.0.1:3000/return', data)
