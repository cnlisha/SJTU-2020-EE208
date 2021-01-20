import cv2
import numpy as np
import os
import pickle as pk

def tidu(img0):#梯度
    img = cv2.GaussianBlur(img0, ksize=(7, 7), sigmaX=1.03) * 1.0
    cannyKerX = np.array([[-3, -10, -3], [0, 0, 0], [3, 10, 3]])
    cannyKerY = np.array([[-3, 0, 3], [-10, 0, 10], [-3, 0, 3]])
    grad_x = cv2.filter2D(img, ddepth=-1, kernel=cannyKerX, anchor=(-1, -1))/16
    grad_y = cv2.filter2D(img, ddepth=-1, kernel=cannyKerY, anchor=(-1, -1))/16
    grad_norm = np.power(np.add(np.power(grad_x, 2), np.power(grad_y, 2)), 0.5)
    grad_direct = np.arctan(np.divide(grad_y, np.add(grad_x, 0.01)))
    M = grad_norm.shape[0]
    N = grad_norm.shape[1]
    for i in range(M):
        for j in range(N):
            if grad_x[i, j] < 0:
                grad_direct[i, j] = grad_direct[i, j] + np.pi
            if grad_direct[i, j] < 0:
                grad_direct[i, j] = grad_direct[i, j] + (np.pi * 2)
    tmpimg = np.array(img0)
    for i in range(0, M, 10):
        for j in range(0, N, 10):
            endx = i + int(np.cos(grad_direct[i, j]) * 5)
            endy = j + int(np.sin(grad_direct[i, j]) * 5)
            tmpimg = cv2.line(tmpimg, (j, i), (endy, endx), 255)
    return grad_norm, grad_direct

def zitu(img, direct, x, y, main_direct):#子图
    N = img.shape[0]
    M = img.shape[1]
    ret = np.zeros((16, 16))
    ret2 = np.zeros((16, 16))
    for i in range(-8, 8):
        for j in range(-8, 8):
            r = np.power((np.power(i, 2) + np.power(j, 2)), 0.5)
            theta = np.arctan(j * 1.0 / (i + 0.01))
            if i < 0:
                theta += np.pi
            if theta < 0:
                theta += (np.pi * 2)
            theta += main_direct
            if theta > (np.pi * 2):
                theta -= (np.pi * 2)
            rx = x * 1.0 + r * np.cos(theta)
            ry = y * 1.0 + r * np.sin(theta)
            rx = min(int(np.rint(rx)), N - 1)
            rx = max(rx, 0)
            ry = min(int(np.rint(ry)), M - 1)
            ry = max(ry, 0)
            ret[i + 8, j + 8] = img[rx, ry]
            ret2[i + 8, j + 8] = direct[rx, ry] - main_direct
            if ret2[i + 8, j + 8] < 0:
                ret2[i + 8, j + 8] = ret2[i + 8, j + 8] + (np.pi * 2)
    return ret, ret2

def guanjiandian(img, MaxCorner):#关键点
    M = img.shape[0]
    N = img.shape[1]
    kp = cv2.goodFeaturesToTrack(img, maxCorners=MaxCorner, qualityLevel=0.03, minDistance=10)
    kp = kp.tolist()
    MaxCorner = len(kp)
    des = np.zeros((MaxCorner, 128))
    grad_norm, grad_direct = tidu(img)
    main_direct_list = [0.0] * MaxCorner
    for ip in range(MaxCorner):
        p = kp[ip]
        y = int(p[0][0])
        x = int(p[0][1])
        if ((x-8 < 1) or (x+8 > M-1)
                or (y-8 <1) or (y+8 > N-1)):
            continue
        sub_norm = np.array(grad_norm[x-8:x+8, y-8:y+8])
        sub_direct = np.array(grad_direct[x-8:x+8, y-8:y+8])
        main_direct_bin = np.zeros((1, 36))
        for i in range(16):
            for j in range(16):
                ind = int(sub_direct[i, j] * 18 / np.pi)
                main_direct_bin[0, ind] += sub_norm[i, j]
        main_direct = np.argmax(main_direct_bin) * (np.pi / 18) + (np.pi / 36)
        sub_norm, sub_direct = zitu(img, grad_direct, x, y, main_direct)
        main_direct_list[ip] = main_direct
        deslist = [0.0] * 128
        for i in range(16):
            for j in range(16):
                ind = (((i // 4) * 4) + (j // 4)) * 8
                ind += int(sub_direct[i, j] * 4 / np.pi)
                deslist[ind] += sub_norm[i, j]
        des[ip, :] = np.reshape(np.array(deslist), (1, 128))
    img_tmp = np.array(img)
    for ip in range(MaxCorner):
        begy = int(kp[ip][0][0])
        begx = int(kp[ip][0][1])
        endy = begy + int(30 * np.sin(main_direct_list[ip]))
        endx = begx + int(30 * np.cos(main_direct_list[ip]))
        img_tmp = cv2.line(img_tmp, (begy, begx), (endy, endx), 255, 2)
    kplist = []
    for i in range(MaxCorner):
        x = kp[i][0][0]
        y = kp[i][0][1]
        kplist.append(cv2.KeyPoint(x, y, _size=grad_norm[int(y), int(x)]))
    return kplist, np.array(des, dtype=np.float32)

def draw(img_target, kp1, des1, img_data, kpdes):#画出关键点
    kp2 = kpdes["kp"]
    des2 = kpdes["des"]
    shape2 = kpdes["gsize"]
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    nice_match = []
    for m, n in matches:
        if m.distance < 0.8 * n.distance:
            nice_match.append([m])
    M = max([img_target.shape[0], img_data.shape[0]])
    N = img_target.shape[1] + img_data.shape[1]
    img_match = np.zeros((M, N))
    kp2New = []
    ratio = shape2[0] / img_data.shape[0]
    for i in range(len(kp2)):
        x = kp2[i][0]
        y = kp2[i][1]
        s = kp2[i][2]
        kp2New.append(cv2.KeyPoint(x / ratio, y / ratio, _size=s))
    kp2 = kp2New
    img_match = cv2.drawMatchesKnn(img_target, kp1, img_data, kp2, nice_match, img_match, matchColor=[0, 0, 255], singlePointColor=[255, 0, 0])
    #cv2.imshow("SIFT", img_match)
    #cv2.waitKey(0)
    cv2.imwrite("match.png", img_match)

def jinzita(img):#金字塔
    res = [img]
    M = img.shape[0]
    N = img.shape[1]
    minMN = min(M, N)
    maxMN = max(M, N)
    while minMN >= 100:
        nxt = cv2.resize(res[-1], (0, 0), fx=0.8, fy=0.8)
        res.append(nxt)
        M = res[-1].shape[0]
        N = res[-1].shape[1]
        minMN = min(M, N)
    while maxMN <= 1000:
        nxt = cv2.resize(res[0], (0, 0), fx=1.25, fy=1.25)
        res.insert(0, nxt)
        M = res[0].shape[0]
        N = res[0].shape[1]
        maxMN = max(M, N)
    return res
#函数封装

def getname(s):
    l = []
    for c in s:
        if ((c>='0' and c<='9') or
                (c>='a' and c<='z') or (c>='A' and c<='Z')):
            l.append(c)
    return ''.join(l)

def mysift(imgName):
    img_data_color = cv2.imread(imgName, cv2.IMREAD_COLOR)
    img_data = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
    dataImgL = jinzita(img_data)
    KPDESlist = []
    for j in range(len(dataImgL)):
        img_data = dataImgL[j]
        kp2, des2 = guanjiandian(img_data, 128)
        kp2list = []
        for k in range(len(kp2)):
            kp2list.append((kp2[k].pt[0], kp2[k].pt[1], kp2[k].size))
        KPDESlist.append({"kp": kp2list, "des": des2, "gsize": img_data.shape})
    pkname = os.path.join("./dataset", getname(imgName))
    pkfile = open(pkname + ".pkl", "wb")
    ob = {"img": img_data_color, "filename": imgName, "KPDESlist": KPDESlist}
    pk.dump(ob, pkfile)
    pkfile.close()

if __name__ == "__main__":
    rootPath = "./dataset"
    for dirpath, dirnames, filenames in os.walk(rootPath):
        for filename in filenames:
            filename = os.path.join(dirpath, filename)
            mysift(filename)
#准备过程

def counting(kp1, des1, data):#数点
    res = 0
    KPDESlist = data["KPDESlist"]
    for i in range(len(KPDESlist)):
        des2 = KPDESlist[i]["des"]
        shape2 = KPDESlist[i]["gsize"]
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        nice_match = []
        for m, n in matches:
            if m.distance < 0.8 * n.distance:
                nice_match.append([m])
        if len(nice_match) > res:
            res = len(nice_match)
    #print("match:", res)
    return res

def bestmatch(img_target, kp1, des1, dataID):
    f = open(dataID, "rb")
    data = pk.load(f)
    f.close()
    img_data = data["img"]
    imgName = data["filename"]
    KPDESlist = data["KPDESlist"]
    maxNum = 0
    maxID = 0
    bf = cv2.BFMatcher()
    for i in range(len(KPDESlist)):
        des2 = KPDESlist[i]["des"]
        shape2 = KPDESlist[i]["gsize"]
        matches = bf.knnMatch(des1, des2, k=2)
        nice_match = []
        for m, n in matches:
            if m.distance < 0.8 * n.distance:
                nice_match.append([m])
        if len(nice_match) > maxNum:
            maxNum = len(nice_match)
            maxID = i
    draw(img_target, kp1, des1, img_data, KPDESlist[maxID])

if __name__ == "__main__":
    tofind = "target.jpg"
    img_target_color = cv2.imread(tofind, cv2.IMREAD_COLOR)
    img_target = cv2.imread(tofind, cv2.IMREAD_GRAYSCALE)
    kp1, des1 = guanjiandian(img_target, 128)
    dataListName = []
    rootPath = "./dataset"
    for dirpath, dirnames, filenames in os.walk(rootPath):
        for filename in filenames:
            filename = os.path.join(dirpath, filename)
            if filename.endswith("pkl"):
                dataListName.append(filename)
    maxMatch = 0
    matchID = ""
    for dataname in dataListName:
        f = open(dataname, "rb")
        data = pk.load(f)
        f.close()
        imgName = data["filename"]
        count = counting(kp1, des1, data)
        if count > maxMatch:
            maxMatch = count
            matchID = dataname
    bestmatch(img_target_color, kp1, des1, matchID)
#实现