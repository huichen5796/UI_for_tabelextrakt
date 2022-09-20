import requests
import sys, json
from functions import Search

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
            table['col%s'%i] = result['_source']
        
        print(json.dumps(table))

    #sys.stdout.flush()

def returnData(url,data):
    x=requests.post(url,data)
    print(x.text)
    
receivePara()

#returnData('http://127.0.0.1:3000/return', data)
