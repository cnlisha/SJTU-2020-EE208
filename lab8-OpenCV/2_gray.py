import numpy
import cv2
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

img = cv2.imread("images/img1.jpg", cv2.IMREAD_GRAYSCALE)
list = numpy.array(img).flatten()
#print(list)
number = 255
plt.hist(list, number, density=1)
plt.legend()
plt.savefig("2_gray_img1.png")
#plt.show()
'''
img = cv2.imread("images/img2.jpg", cv2.IMREAD_GRAYSCALE)
list = numpy.array(img).flatten()
#print(list)
number = 255
plt.hist(list, number, density=1)
plt.legend()
plt.savefig("2_gray_img2.png")
#plt.show()

img = cv2.imread("images/img3.jpg", cv2.IMREAD_GRAYSCALE)
list = numpy.array(img).flatten()
#print(list)
number = 255
plt.hist(list, number, density=1)
plt.legend()
plt.savefig("2_gray_img3.png")
#plt.show()
'''