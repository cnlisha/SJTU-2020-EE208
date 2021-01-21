import cv2
import time

def reset(k):
    if 0 <= k < 0.3:
        k = 0
    elif 0.3 <= k < 0.6:
        k = 1
    elif 0.6 <= k:
        k = 2
    return k

def makima(img, start1, end1, start2, end2):
    r = 0
    g = 0
    b = 0
    for i in range(start1, end1):
        for j in range(start2, end2):
            r += img[i][j][0]
            g += img[i][j][1]
            b += img[i][j][2]
    count = r + g + b
    r = round(r / count, 2)
    g = round(g / count, 2)
    b = round(b / count, 2)
    l = []
    l.append(r)
    l.append(g)
    l.append(b)
    return l

def zhunbei(img):
    H = len(img)
    W = len(img[1])
    MH = int(H / 2)
    MW = int(W / 2)
    l1 = makima(img, 0, MH, 0, MW)
    l2 = makima(img, 0, MH, MW, W)
    l3 = makima(img, MH, H, 0, MW)
    l4 = makima(img, MH, H, MW, W)
    l = []
    for i in l1:
        l.append(reset(i))
    for i in l2:
        l.append(reset(i))
    for i in l3:
        l.append(reset(i))
    for i in l4:
        l.append(reset(i))
    res = []
    for i in l:
        if i == 0:
            res.extend([0, 0])
        elif i == 1:
            res.extend([1, 0])
        elif i == 2:
            res.extend([1, 1])
    return res

def LSHSearch(vec):
    l = []
    count = 0
    list = [1,3,7,8]
    for i in list:
        l.append(vec[i])
    for i in l:
        count = count * 2 + i
    return count
import pickle as pk

def yuchuli():
    dataset = []
    for i in range(14):
        dataset.append([])
    for i in range(1, 41):
        imgname = "Dataset/{}.jpg".format(i)
        img = cv2.imread(imgname)
        vec = zhunbei(img)
        hash = LSHSearch(vec)
        dataset[hash].append(tuple([imgname, vec]))
    file = open("DataLSH.pkl", "wb")
    pk.dump(dataset, file)
    file.close()
    print("Done.")

yuchuli()

def LSHCompare():
    a = time.clock()
    img = cv2.imread("target.jpg")
    vec = zhunbei(img)
    hash = LSHSearch(vec)
    with open("DataLSH.pkl", "rb") as f:
        dataset = pk.load(f)
    aimSet = dataset[hash]
    for i in range (1, 101):
        NNSearch(vec, aimSet)
    b = time.clock()
    print("{} seconds.".format(b - a))
    cv2.waitKey(0)

def NNSearch(vec, aimSet):
    result = []
    len1 = len(aimSet)
    len2 = len(vec)
    for i in range(len1):
        for j in range(len2):
            if vec[j] != aimSet[i][1][j]:
                break
            if j == len2 - 1:
                result.append(aimSet[i][0])
    num = len(result)
    for i in range(num):
        img = cv2.imread(result[i])
        cv2.imshow("Match_LSH", img)
    if (num == 1):
        print("{} is the matched.".format(result[0]))

LSHCompare()