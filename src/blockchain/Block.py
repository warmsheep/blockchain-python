import datetime
import hashlib
from Message import Message
from Message import InvalidMessage
from Trans import Trans

class Block:
    # 初始化
    def __init__(self, *args):
        self.messageList = []   # 存储多个交易记录
        self.timestamp = None   # 存储多个记录的最终锁定时间
        self.hash = None        # 当前区块的哈希
        self.prev_hash = None   # 上一个区块的哈希
        if args:
            for arg in args:
                self.add_message(arg)

    # 增加交易信息
    def add_message(self, message):
        # 区分第一条和后面多条
        if len(self.messageList) > 0:
            message.link(self.messageList[-1]) # 和最后一条消息进行链接
        message.seal()      #密封
        message.validate()  #校验
        self.messageList.append(message)

    # 区块链链接起来
    def link(self, block):
        self.prev_hash = block.hash

    # 密封
    def seal(self):
        self.timestamp = datetime.datetime.now()
        self.hash = self._hash_block()              #密封当前哈希

    # 整块数据做一个哈希
    def _hash_block(self):
        # 密封上一块哈希，时间线，交易记录最后一个的哈希
        return hashlib.sha512((
            str(self.prev_hash) + \
            str(self.timestamp) + \
            str(self.messageList[-1].hash)).encode("utf-8") \
            ).hexdigest()

    # 验证
    def validate(self):
        # 每个交易记录校验一下
        for i,message in enumerate(self.messageList):
            message.validate()
            if i > 0 and message.prev_hash != self.messageList[i - 1].hash:
                raise InvalidBlock("无效的Block，交易记录被修改，在第{}条记录被修改".format(i))
                return False
        return True

    # 类的对象描述
    def __repr__(self):
        return "money block = hash: {}, prevHash: {}, len: {}, time:{} ".format(
            self.hash,self.prev_hash, len(self.messageList), self.timestamp
        )


class InvalidBlock(Exception):
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

        # 加入交易记录
        b1 = Block(m1, m2, m3)

        b1.seal()
        print("验证区块" + str(b1.validate()))

        print(b1)
        m2.hash = "111"
        print("验证修改后的区块" + str(b1.validate()))
    except InvalidMessage as e:
        print(e)
    except InvalidBlock as e:
        print(e)
