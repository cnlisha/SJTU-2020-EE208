# SJTU EE208

from functools import cmp_to_key
import os
import time, os
from math import acos

import numpy as np
from numpy.core.arrayprint import printoptions
import torch
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader

print('Load model: ResNet50')
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
trans = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize,
])

def features(x):
    x = model.conv1(x)
    x = model.bn1(x)
    x = model.relu(x)
    x = model.maxpool(x)
    x = model.layer1(x)
    x = model.layer2(x)
    x = model.layer3(x)
    x = model.layer4(x)
    x = model.avgpool(x)

    return x

target_id = 'targett'
target_file =  target_id + '.jpg' #'img/' +
target_img = default_loader(target_file)
target_input_img = trans(target_img)
target_input_img = torch.unsqueeze(target_input_img, 0)
target_feature = features(target_input_img)
target_feature = target_feature.detach().numpy()

path = 'features'
feature_files = os.listdir(path)
id_theta_list = []
for feature_file in feature_files:
    cur_id = feature_file.split('.')[0]
    if cur_id == target_id:
        continue

    cur_feature = np.load(path + '/' + feature_file)
    theta = acos(np.sum(cur_feature * target_feature) / (np.linalg.norm(cur_feature) * np.linalg.norm(target_feature)))
    id_theta_list.append([cur_id, theta])

sorted_id_theta_list = sorted(id_theta_list, key = lambda s: s[1])
for i in range(5):
    print('top {} img\nid: {}, theta: {}, score: {}'.format(i + 1, sorted_id_theta_list[i][0], sorted_id_theta_list[i][1], 100-100*sorted_id_theta_list[i][1]))