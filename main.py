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
    #msg = { 'todo': 'seeResult', 'image': 'test3.png' }
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
        # try:
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

            res = {
                'massage': 'success',
                'tableNumber': str(len(table_zone))
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

            print(json.dumps({
                'massage':'success',
                'datas':table,
                'label':msg['label']
            }))
        except:
            print(json.dumps({
                'massage': 'error',
            }))

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

    if msg['todo'] == 'upload':
        try:
            with open('assets/uploads/originalName.txt', 'a+') as f:
                f.write(str(msg).replace('\\', '/').replace('//', '/')+'\n')
            print(json.dumps({'massage': 'success',
                              'fileName': '["'+msg['fileName']+'"]'}))
        except:
            print(json.dumps({'massage': 'error', }))

    if msg['todo'] == 'seeDetail':
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
            resInfo = {
                'massage':'success',
                'fileName':msg['image'],
                'path':path_list[-1]['path'],
            }
            number = int(info_list[-1]['tableNumber'])
            for i in range(1, number+1):
                resInfo['the_%sst_table_of_%s' %(i, msg['image'])] = "imageShow/table_%s_of_%s" %(i, msg['image'])
    
            print(json.dumps(resInfo))
 
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

            # deletes whole index
            es.indices.delete(index='table', ignore=[400, 404])

            print(json.dumps({'massage': 'success'}))
        except:
            print(json.dumps({'massage': 'error'}))

    if msg['todo'] == 'cleanEla':
        try:
            # deletes whole index
            es.indices.delete(index='table', ignore=[400, 404])

            print(json.dumps({'massage': 'success'}))
        except:
            print(json.dumps({'massage': 'error'}))

    if msg['todo'] == 'continue':
        try:
            file_list = []
            with open('assets/uploads/originalName.txt', 'r') as f:
                for line in f:
                    file_list.append(eval(line)['fileName'])
                file_list = list(set(file_list))
                if len(file_list) != 0:
                    print(json.dumps({
                        'massage': 'success',
                        'fileName': file_list
                    }))
                else:
                    print(json.dumps({
                        'massage': 'error',
                    }))
        except:
            print(json.dumps({'massage': 'error', }))


receivePara()
