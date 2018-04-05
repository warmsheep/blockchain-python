
import hashlib
import  json
import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask,jsonify,request
from typing import Any,Dict,List,Optional #数据结构

class NewBlockChain:
    def __init__(self):
        self.current_trans = [] #当前的交易
        self.chain = []     #区块链管理多个区块
        self.nodes = set()  #保存网络中其他节点
        self.new_block(prev_hash="1",proof=100) #创建创世区块

    # 创建一个区块
    def new_block(self,
                  proof:int, #确定proof为int类型
                  prev_hash:Optional[str] #上一块的哈希类型
                  )->Dict[str,Any]: #创建一个区块返回一个字典类型
        block = {
            "index": len(self.chain) + 1,  # 索引
            "timestamp": time.time(),  # 时间
            "trans": self.current_trans,  # 交易路
            "proof": proof,  # 工作量的凭证
            "prev_hash": prev_hash or self.hash(self.chain[-1])  # 上一块哈希
        }
        # 开辟新区块，交易需要被清空
        self.current_trans = []
        # 区块加入区块链
        self.chain.append(block)
        return block


    # 创建一个交易
    def new_trans(self,sender:str,receiver:str,amount:int):
        # 生成交易信息，信息加入到下一个有待挖的区块
        self.current_trans.append({
            "sender": sender,       #付款方
            "receiver": receiver,   #收款方
            "amount": amount        #金额
        })
        return self.last_block["index"] + 1 #索引标记交易数量

    @property
    def last_block(self)->Dict[str,Any]:
        return self.chain[-1]

    # 哈希
    @staticmethod
    def hash(block:Dict[str,Any])->str:
        blockstring = json.dumps(block,sort_keys=True).encode("utf-8")
        return hashlib.sha512(blockstring).hexdigest() #取出哈希编码的十六进制


    # 工作量证明
    def proof_of_work(self,last_proof:int)->int:
        proof = 0  # 循环求解
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    # 验证证明,第N个区块依赖于N-1个区块
    @staticmethod
    def valid_proof(last_proof:int,proof:int)->bool:
        guess = f'{last_proof*proof}'.encode() #二进制编码
        guess_hash = hashlib.sha512(guess).hexdigest()   #取出哈希值
        return guess_hash[-4:] == "1234" #验证是否符合条件


    #加入网络的其他节点，用于更新
    def register_node(self,addr:str)->None:
        now_url = urlparse(addr)
        self.nodes.add(now_url.netloc)  #增加网络节点



    #区块链校验
    def valid_chain(self,chain:List[Dict[str,Any]])->bool: #区块链验证
        last_block = chain[0] #第一个区块
        current_index = 1 #当前的第一个索引
        while current_index < len(chain):
            block  = chain[current_index] #当前的区块
            #哈希校验
            if block["prev_hash"] != self.hash(last_block):
                return False
            #工作量校验，是否挖矿挖出来的
            if not self.valid_proof(last_block["proof"],block["proof"]):
                return False
            last_block = block # 轮询
            current_index += 1 #索引自增



    # 共识算法
    def resolve_conflicts(self)->bool:
        #网络中的多个节点，取出最长的
        neighbours = self.nodes #取得所有节点
        new_chain = None #新的区块链
        max_length = len(self.chain) #当前的区块链长度
        for node in neighbours:
            response = requests.get(f"http://{node}/chain") #访问网络节点
            if response.status_code == 200:
                length = response.json()["length"]  # 取得长度
                chain = response.json()["chain"]  # 取得区块链表

                # 刷新保存最长的区块链与完成校验
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # 判断吃否为空
        if new_chain:
            self.chain = new_chain  # 更新成功
            return True
        else:
            return False


#创建一个网络节点
my_chain = NewBlockChain()
node_id = str(uuid4()).replace("-","") #节点替换，生成密钥

print("当前节点钱包地址:",node_id)
app = Flask(__name__)

@app.route("/")
def index_page():
    return "欢迎来到哔哔系统！"

@app.route("/chain")
def index_chain():
    response = {
        "chain" : my_chain.chain,
        "length" : len(my_chain.chain)
    }
    return jsonify(response),200

@app.route("/mine") #挖矿
def index_mine():
    last_block = my_chain.last_block #取得最后一个区块
    last_proof = last_block["proof"] #取得工作量证明
    proof = my_chain.proof_of_work(last_proof) #挖矿计算

    #系统奖励,挖矿产生交易
    my_chain.new_trans(
        sender="0",     #0代表系统奖励
        receiver=node_id,   #当前钱包地址
        amount=10
    )
    #增加一个新的区块
    block = my_chain.new_block(proof,None)
    response = {
        "message" : "新的区块创建",
        "index" : block["index"],
        "trans" : last_block["trans"],
        "proof" : block["proof"],
        "prev_hash" : block["prev_hash"]
    }
    return jsonify(response),200

# 创建一个新的交易
@app.route("/new_trans",methods=["POST"])
def index_new_trans():
    # 抓取网络传输的信息
    values = request.get_json()
    required = ["sender","receiver","amount"]
    if not all(key in values for key in required):
        return "数据不完整",400
    index = my_chain.new_trans(
        values["sender"],
        values["receiver"],
        values["amount"])

    response = {
        "message" : f"交易加入到区块{index}"
    }
    return jsonify(response),200

@app.route("/new_node",methods = ["POST"])
def new_node():
    values = request.get_json()
    nodes = values.get("nodes") #获取所有的节点
    if nodes is None:
        return "没有数据节点",400
    for node in nodes:
        my_chain.register_node(node)    #增加网络节点

    response = {
        "message" : f"网络节点已经被追加",
        "nodes" : list(my_chain.nodes)     #查看所有节点
    }
    return jsonify(response),200

@app.route("/node_refresh")
def node_refresh():
    replaced = my_chain.resolve_conflicts() #共识算法进行最长替换
    if replaced:
        response = {
            "message" : "区块链已经被替换为最长",
            "new_chain" : my_chain.chain
        }

    else:
        response = {
            "message": "当前区块链已经是最长无需替换",
            "new_chain": my_chain.chain
        }
    return jsonify(response),200

if __name__ == "__main__":
    app.run("127.0.0.1",port=5000)