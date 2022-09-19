import requests
'''
getDataUrl = 'http://127.0.0.1:3000/run'

data = requests.get(getDataUrl)

print(data.text)
'''
import sys, json

def receivePara():
    msg = sys.argv[1]
    print('got:', msg)
    # sys.stdout.flush()

    
receivePara()

