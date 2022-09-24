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
    #msg = { 'todo': 'run', 'file': 'test4.jpg', 'model': 'densenet' }
    if msg['todo'] == 'run':
        f = open('assets\\uploads\\originalName.txt', 'r')
        info_list=[]
        for line in f.readlines():
            if re.search(msg['file'], line) != None:
                info = eval(line.split('\n')[0])
                info_list.append(info)
        blob_path = 'assets' + info_list[-1]['path']

        with open(blob_path,'rb') as f:
        
            image = np.frombuffer(f.read(), np.int8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        
            #cv2.imshow('', image)
            #cv2.waitKey()

        file_name = info_list[-1]['fileName']
        model = msg['model']
        try:
            shape_list = list(image.shape)
            if len(shape_list) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
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

