import sys
import json
from functions import Search, TiltCorrection, SizeNormalize, PositionTable, GetTableZone, SaveTable
import re
import numpy as np
import cv2
import os

def receivePara():
    msg = sys.argv[1]
    msg = eval(msg)
    #msg = { 'todo': 'run', 'file': 'test4.jpg', 'model': 'densenet' }
    if msg['todo'] == 'run':
        f = open('assets\\uploads\\originalName.txt', 'r')
        info_list=[]
        for line in f.readlines():
            if re.search(msg['file'], line) != None:
                info = eval(line.split('\n')[0])
                info_list.append(info)
        blob_path = 'assets' + info_list[-1]['path']

        image = np.fromfile(blob_path, np.uint8, count=-1) #这个image有问题，找找如何将二进制流转换为图片！！
        file_name = info_list[-1]['fileName']
        model = msg['model']
        try:
            shape_list = list(image.shape)
            if len(shape_list) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cv2.imshow('',image)
            cv2.waitKey()
            image_rotate = TiltCorrection(image)  # got gray
            img_3channel = cv2.cvtColor(
                image_rotate, cv2.COLOR_GRAY2BGR)  # gray to 3 channel

            img_1024 = SizeNormalize(img_3channel)
            table_boundRect = PositionTable(
                img_1024, '_', model)  # unet besser
            table_zone = GetTableZone(table_boundRect, img_1024)
            img_path = 'assets\\imageShow\\' + file_name
            for nummer, table in enumerate(table_zone):
                SaveTable(nummer, table, img_path, [],
                        model, [])  # densecol besser
            if len(table_boundRect) == 0:
                massage = 'assets\\imageShow\\noTable.png'
            else:
                massage = 'assets\\imageShow\\{}'.format('table_' + str(nummer+1) + '_of_' + str(os.path.basename(img_path)))
            res = {
            'path':massage
            }
            print(json.dumps(res))

        except Exception as e:
            massage =  'error'

            res = {
                'path':massage
            }
            print(json.dumps(res))

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


receivePara()

