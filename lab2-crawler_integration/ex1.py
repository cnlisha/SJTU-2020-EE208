from Bitarray import Bitarray
import random
import string
bitarray_obj = Bitarray(32000)
def randomstring(slen=6):
    return ''.join(random.sample(string.ascii_letters + string.digits, slen))
strlist = [randomstring() for i in range(1000)]
testlist = [randomstring() for i in range(100000)]
celiang = []
shiji = []
def BKDRHash(seed, key):
    hash = 0
    for i in range(len(key)):
        hash = (hash * seed) + ord(key[i])
    return hash
seedlist = [13, 131, 1313, 13131, 131313, 1313131 , 13131313, 131313131 ,1313131313 , 13131313131]

for i in strlist:
    for j in seedlist:
        num = BKDRHash(j, i) % 32000
        bitarray_obj.set(num)
for i in testlist:
    l = 1
    for j in seedlist:
        num = BKDRHash(j, i) % 32000
        l = l * bitarray_obj.get(num)
    if l == 0:
        celiang.append(i)
for j in testlist:
    count = 1
    for i in strlist:
        if j == i:
            count = 0
    if count == 1:
        shiji.append(j)
print(1-(len(celiang)/len(shiji)))