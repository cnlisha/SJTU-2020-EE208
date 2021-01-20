import numpy as np
import cv2 as cv2
from matplotlib import pyplot as plt
'''
img = cv2.imread('images/img1.jpg')
color = ('b', 'g', 'r')
for i, col in enumerate(color):
    histr = cv2.calcHist([img], [i], None, [256], [0, 256])
    plt.plot(histr, color=col)
    plt.xlim([0, 256])
plt.savefig("1_color_img1.png")
#plt.show()

img = cv2.imread('images/img2.jpg')
color = ('b', 'g', 'r')
for i, col in enumerate(color):
    histr = cv2.calcHist([img], [i], None, [256], [0, 256])
    plt.plot(histr, color=col)
    plt.xlim([0, 256])
plt.savefig("1_color_img2.png")
#plt.show()
'''
img = cv2.imread('images/img3.jpg')
color = ('b', 'g', 'r')
for i, col in enumerate(color):
    histr = cv2.calcHist([img], [i], None, [256], [0, 256])
    plt.plot(histr, color=col)
    plt.xlim([0, 256])
plt.savefig("1_color_img3.png")
#plt.show()
