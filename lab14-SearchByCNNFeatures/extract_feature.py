# SJTU EE208

import os
import time, os

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
    
path = "img"
store_path = 'features/'
files = os.listdir(path)

for file in files:
    file_name = file.split('.')[0]
    img = default_loader(path + '/' + file)
    input_img = trans(img)
    input_img = torch.unsqueeze(input_img, 0)

    img_feature = features(input_img)
    img_feature = img_feature.detach().numpy()

    np.save(store_path + file_name + '.npy', img_feature)

