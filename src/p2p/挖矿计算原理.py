
#通过计算哈希来挖掘区块

from hashlib import sha512 #加密算
x=11
y=1
# x*y的哈希值以0结尾
# f'{x*y}'把x*y的结果转换为字符串
# -3 是控制难度的一个方式，通过哈希来控制难度
while sha512(f'{x*y}'.encode()).hexdigest()[-3:] != "000":
    y += 1
    print(y)
print("y={}时刻，y求解".format(y))