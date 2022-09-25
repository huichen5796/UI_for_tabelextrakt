import base64
from email.mime import base
import sys
import json
from functions import Search, TiltCorrection, SizeNormalize, PositionTable, GetTableZone, SaveTable
import re
import numpy as np
import cv2
import os
import torch
import torch.nn as nn
import torchvision
from elasticsearch import Elasticsearch
from elasticsearch import helpers
es = Elasticsearch()

class DenseNet(nn.Module):
    def __init__(self, pretrained=True, requires_grad=True):
        super(DenseNet, self).__init__()
        denseNet = torchvision.models.densenet121(pretrained=True).features
        self.densenet_out_1 = torch.nn.Sequential()
        self.densenet_out_2 = torch.nn.Sequential()
        self.densenet_out_3 = torch.nn.Sequential()

        for x in range(8):
            self.densenet_out_1.add_module(str(x), denseNet[x])
        for x in range(8, 10):
            self.densenet_out_2.add_module(str(x), denseNet[x])

        self.densenet_out_3.add_module(str(10), denseNet[10])

        if not requires_grad:
            for param in self.parameters():
                param.requires_grad = False

    def forward(self, x):

        out_1 = self.densenet_out_1(x)  # torch.Size([1, 256, 64, 64])
        out_2 = self.densenet_out_2(out_1)  # torch.Size([1, 512, 32, 32])
        out_3 = self.densenet_out_3(out_2)  # torch.Size([1, 1024, 32, 32])
        return out_1, out_2, out_3


class TableDecoder(nn.Module):
    def __init__(self, channels, kernels, strides):
        super(TableDecoder, self).__init__()
        self.conv_7_table = nn.Conv2d(
            in_channels=256,
            out_channels=256,
            kernel_size=kernels[0],
            stride=strides[0])
        self.upsample_1_table = nn.ConvTranspose2d(
            in_channels=256,
            out_channels=128,
            kernel_size=kernels[1],
            stride=strides[1])
        self.upsample_2_table = nn.ConvTranspose2d(
            in_channels=128 + channels[0],
            out_channels=256,
            kernel_size=kernels[2],
            stride=strides[2])
        self.upsample_3_table = nn.ConvTranspose2d(
            in_channels=256 + channels[1],
            out_channels=1,
            kernel_size=kernels[3],
            stride=strides[3])

    def forward(self, x, pool_3_out, pool_4_out):
        x = self.conv_7_table(x)  # [1, 256, 32, 32]
        out = self.upsample_1_table(x)  # [1, 128, 64, 64]
        out = torch.cat((out, pool_4_out), dim=1)  # [1, 640, 64, 64]
        out = self.upsample_2_table(out)  # [1, 256, 128, 128]
        out = torch.cat((out, pool_3_out), dim=1)  # [1, 512, 128, 128]
        out = self.upsample_3_table(out)  # [1, 1, 1024, 1024]
        return out


class TableNet(nn.Module):
    def __init__(self, encoder='densenet', use_pretrained_model=True, basemodel_requires_grad=True):
        super(TableNet, self).__init__()

        self.base_model = DenseNet(
            pretrained=use_pretrained_model, requires_grad=basemodel_requires_grad)
        self.pool_channels = [512, 256]
        self.in_channels = 1024
        self.kernels = [(1, 1), (1, 1), (2, 2), (16, 16)]
        self.strides = [(1, 1), (1, 1), (2, 2), (16, 16)]

        # common layer
        self.conv6 = nn.Sequential(
            nn.Conv2d(in_channels=self.in_channels,
                      out_channels=256, kernel_size=(1, 1)),
            nn.ReLU(inplace=True),
            nn.Dropout(0.8),
            nn.Conv2d(in_channels=256, out_channels=256, kernel_size=(1, 1)),
            nn.ReLU(inplace=True),
            nn.Dropout(0.8))

        self.table_decoder = TableDecoder(
            self.pool_channels, self.kernels, self.strides)

    def forward(self, x):

        pool_3_out, pool_4_out, pool_5_out = self.base_model(x)
        conv_out = self.conv6(pool_5_out)  # [1, 256, 32, 32]
        # torch.Size([1, 1, 1024, 1024])
        table_out = self.table_decoder(conv_out, pool_3_out, pool_4_out)
        return table_out


def receivePara():
    msg = sys.argv[1]
    msg = eval(msg)
    #msg = {'todo': 'cleanAll'}
    if msg['todo'] == 'run':
        try:
            f = open('assets\\uploads\\originalName.txt', 'r')
            info_list = []
            for line in f.readlines():
                if re.search(msg['file'], line) != None:
                    info = eval(line.split('\n')[0])
                    info_list.append(info)
            blob_path = 'assets' + info_list[-1]['path']

            with open(blob_path, 'rb') as f:

                image = np.frombuffer(f.read(), np.int8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                #cv2.imshow('', image)
                # cv2.waitKey()

            file_name = info_list[-1]['fileName']
            model = msg['model']
        #try:
            shape_list = list(image.shape)
            if len(shape_list) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            image_rotate = TiltCorrection(image)  # got gray
            img_3channel = cv2.cvtColor(
                image_rotate, cv2.COLOR_GRAY2BGR)  # gray to 3 channel

            img_1024 = SizeNormalize(img_3channel)
            table_boundRect = PositionTable(
                img_1024, file_name, model)  # unet besser
            table_zone = GetTableZone(table_boundRect, img_1024)
            img_path = 'assets\\imageShow\\' + file_name
            for nummer, table in enumerate(table_zone):
                SaveTable(nummer, table, img_path, [],
                          model, [])  # densecol besser

            '''mass=[]
            number = len(table_zone)
            for i in range(1, number+1):
                mass.append('"the %sst table of %s":"imageShow\\table_%s_of_%s"' %(i, msg['file'], i, msg['file']))'''

            if len(table_boundRect) != 0:
                #res = "{'massage':'getTable'," + ','.join(mass) + '}'
                res = {
                    'massage': 'getTable'
                }
            else:
                res = {
                    'massage': 'noTable'
                }

            relation = {
                'file': file_name,
                'tableNumber': str(len(table_zone))
            }

            with open('assets\\imageShow\\relation.txt', 'a+') as f:
                f.write(str(relation)+'\n')

            print(json.dumps(res))

        except Exception as e:
            res = {
                'massage': 'error'
            }
            print(json.dumps(res))

    if msg['todo'] == 'search':
        try:
            results = Search(msg['idx'], msg['label'])
            results = json.loads(results)['hits']['hits']
            table = {}

            for i, result in enumerate(results):
                del result['_source']['uniqueId']
                del result['_source']['fileName']
                table['col%s' % i] = result['_source']

            print(json.dumps(table))
        except:
            print(json.dumps({'er':'error'}))

    if msg['todo'] == 'searchLabel':
       
        try:
            uniqueId_list = []
            res = Search('table', 'all')
            res = json.loads(res)['hits']['hits']
            for ress in res:
                uniqueId_list.append(ress['_source']['uniqueId'])
            uniqueId_list = list(set(uniqueId_list))

            print(uniqueId_list)
        except:
            print('["error"]')

    if msg['todo'] == 'savePath':
        try:
            with open('assets/uploads/originalName.txt', 'a+') as f:
                f.write(str(msg).replace('\\', '/').replace('//', '/')+'\n')
            print(json.dumps({'massage': 'success',
                'fileName': '["'+msg['fileName']+'"]'}))
        except:
            print(json.dumps({'massage': 'success',}))

    if msg['todo'] == 'seeResult':
        try:
            f = open('assets/uploads/originalName.txt', 'r')
            path_list = []
            for line in f.readlines():
                if re.search(msg['image'], line) != None:
                    path = eval(line.split('\n')[0])
                    path_list.append(path)

            f = open('assets\\imageShow\\relation.txt', 'r')
            info_list = []
            for line in f.readlines():
                if re.search(msg['image'], line) != None:
                    info = eval(line.split('\n')[0])
                    info_list.append(info)
            mass = []
            number = int(info_list[-1]['tableNumber'])
            for i in range(1, number+1):
                mass.append('"the_%sst_table_of_%s":"imageShow/table_%s_of_%s"' %
                            (i, msg['image'].split('.')[0], i, msg['image'].split('.')[0]))

            print(json.dumps('{"massage":"success","fileName":"'+str(
                msg['image'])+'","path":"'+path_list[-1]['path']+'",'+",".join(mass)+'}'))
        except:
            print(json.dumps({'massage': "error"}))

    if msg['todo'] == 'cleanAll':
        try:
            for file in os.listdir('assets/uploads'):
                file = os.path.join('assets/uploads', file)
                os.remove(file)
            f = open('assets/uploads/originalName.txt', 'w')
            f.close()
            for file in os.listdir('assets/imageShow'):
                file = os.path.join('assets/imageShow', file)
                os.remove(file)
            f = open('assets/imageShow/relation.txt', 'w')
            f.close()

            es.indices.delete(index='table', ignore=[400, 404])  # deletes whole index

            print(json.dumps({'massage':'success'}))
        except:
            print(json.dumps({'massage':'error'}))

    if msg['todo'] == 'cleanEla':
        try:
            es.indices.delete(index='table', ignore=[400, 404])  # deletes whole index

            print(json.dumps({'massage':'success'}))
        except:
            print(json.dumps({'massage':'error'}))


receivePara()
