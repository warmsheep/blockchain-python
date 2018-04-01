import datetime
import hashlib
import math
from Trans import Trans

class Message:
    # 初始化
    def __init__(self, data):
        self.hash = None                            # 自身的哈希
        self.prev_hash = None                       # 上一个信息的哈希
        self.timestamp = datetime.datetime.now()    # 交易时间
        self.data = data                            # 交易信息
        self.pay_load_hash = self._hash_payload()   # 交易后的哈希

    # 对于交易时间与交易数据进行哈希计算
    def _hash_payload(self):
        return hashlib.sha512((str(self.timestamp) + str(self.data)).encode("utf-8")).hexdigest()

    # 对于交易进行锁定
    def _hash_message(self):
        return hashlib.sha512((str(self.prev_hash) + str(self.pay_load_hash)).encode("utf-8")).hexdigest()

    # 密封
    def seal(self):
        # 对应数据锁定
        self.hash = self._hash_message()

    def validate(self):
        # 判断是否有人修改
        if self.pay_load_hash != self._hash_payload():
            raise InvalidMessage("交易数据与时间被修改" + str(self))
        if self.hash != self._hash_message():
            raise InvalidMessage("交易的哈希链被修改" + str(self))

    def __repr__(self):
        mystr = "hash: {}, prev_hash: {}, data: {}".format(self.hash, self.prev_hash, self.data)
        return mystr

    def link(self, message):
        self.prev_hash = message.hash # 链接


# 异常类
class InvalidMessage(Exception):
    def __init__(self,*args, **kwargs):
        Exception.__init__(self,*args,**kwargs)


# 单独模块测试
if __name__ == "__main__":
    try:
        t1 = Trans("linxuan", "linxuan2", 10)  # 后续需要整合密钥私钥
        t2 = Trans("linxuan", "linxuan2", 20)  # 后续需要整合密钥私钥
        t3 = Trans("linxuan", "linxuan2", 30)  # 后续需要整合密钥私钥

        m1 = Message(t1)
        m2 = Message(t2)
        m3 = Message(t3)

        m1.seal()
        m2.link(m1)
        m2.seal()
        m3.link(m2)
        m3.seal()

        print(m1)
        print(m2)
        print(m3)

        m1.validate()
        m2.validate()
        m3.validate()
    except InvalidMessage as e:
        print(e)
