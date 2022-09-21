import requests
import sys
import json
from functions import Search


def receivePara():
    msg = sys.argv[1]

    msg = eval(msg)

    if msg['todo'] == 'search' and msg['label'] != 'all':
        results = Search(msg['idx'], msg['label'])
        results = json.loads(results)['hits']['hits']
        table = {}

        for i, result in enumerate(results):
            del result['_source']['uniqueId']
            del result['_source']['fileName']
            table['col%s' % i] = result['_source']

        print(json.dumps(table))

    if msg['todo'] == 'search' and msg['label'] == 'all':
        uniqueId_list = []
        res = Search('table', 'all')
        res = json.loads(res)['hits']['hits']
        for re in res:
            uniqueId_list.append(re['_source']['uniqueId'])
        uniqueId_list = list(set(uniqueId_list))

        print(uniqueId_list)

    # sys.stdout.flush()


def returnData(url, data):
    x = requests.post(url, data)
    print(x.text)


receivePara()

#returnData('http://127.0.0.1:3000/return', data)
