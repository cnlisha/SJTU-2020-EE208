import cv2
import numpy
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

img = cv2.imread("images/img1.jpg", cv2.IMREAD_GRAYSCALE)
list = []
H = len(img)
W = len(img[0])
for j in range(1, H-2):
    for k in range(1, W-2):
        Ix = int(img[j][k-1])-int(img[j][k+1])
        Iy = int(img[j-1][k])-int(img[j+1][k])
        I = round((Ix**2+Iy**2)**0.5)
        list.append(I)
#print(list)
number = 360
plt.hist(list, number, density=1)
plt.legend()
plt.savefig("2_gray_gradient_img1.png")
#plt.show()
'''
img = cv2.imread("images/img2.jpg", cv2.IMREAD_GRAYSCALE)
list = []
H = len(img)
W = len(img[0])
for j in range(1, H-2):
    for k in range(1, W-2):
        Ix = int(img[j][k-1])-int(img[j][k+1])
        Iy = int(img[j-1][k])-int(img[j+1][k])
        I = round((Ix**2+Iy**2)**0.5)
        list.append(I)
#print(list)
number = 360
plt.hist(list, number, density=1)
plt.legend()
plt.savefig("2_gray_gradient_img2.png")
#plt.show()

img = cv2.imread("images/img3.jpg", cv2.IMREAD_GRAYSCALE)
list = []
H = len(img)
W = len(img[0])
for j in range(1, H-2):
    for k in range(1, W-2):
        Ix = int(img[j][k-1])-int(img[j][k+1])
        Iy = int(img[j-1][k])-int(img[j+1][k])
        I = round((Ix**2+Iy**2)**0.5)
        list.append(I)
#print(list)
number = 360
plt.hist(list, number, density=1)
plt.legend()
plt.savefig("2_gray_gradient_img3.png")
#plt.show()
'''