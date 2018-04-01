
from Block import Block
from Block import InvalidBlock
from Message import Message
from Message import InvalidMessage
from Trans import Trans

class BlockChain:
    def __init__(self):
        self.blockList = []     # 装载所有区块

    # 增加区块
    def add_block(self, block):
        # 区分第一条和后面多条
        if len(self.blockList) > 0:
            block.link(self.blockList[-1])  # 和最后一条区块进行链接
        block.seal()  # 密封
        block.validate()  # 校验
        self.blockList.append(block)

    def validate(self):
        for i, block in enumerate(self.blockList):
            try:
                block.validate()
            except InvalidBlock as e:
                raise InvalidBlockChain("区块校验错误，区块索引{}".format(i))
        return True

    def __repr__(self):
        return "BlockCoin : {}".format( len(self.blockList))

class InvalidBlockChain(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


if __name__ == "__main__":
    try:
        t1 = Trans("linxuan", "linxuan1", 10)  # 后续需要整合密钥私钥
        t2 = Trans("linxuan", "linxuan2", 20)  # 后续需要整合密钥私钥
        t3 = Trans("linxuan", "linxuan3", 30)  # 后续需要整合密钥私钥

        m1 = Message(t1)
        m2 = Message(t2)
        m3 = Message(t3)

        b1 = Block(m1, m2, m3)

        b1.seal()
        b1.validate()

        t4 = Trans("linxuan", "linxuan4", 40)  # 后续需要整合密钥私钥
        t5 = Trans("linxuan", "linxuan5", 50)  # 后续需要整合密钥私钥
        m4 = Message(t4)
        m5 = Message(t5)

        b2 = Block(m4)
        b2.seal()

        b3 = Block(m5)
        b3.seal()

        b3.messageList.append(m1)

        bc1 = BlockChain()
        bc1.add_block(b1)
        bc1.add_block(b2)
        bc1.add_block(b3)

        print(bc1.validate())

    except InvalidMessage as e:
        print(e)
    except InvalidBlock as e:
        print(e)
    except InvalidBlockChain as e:
        print(e)
