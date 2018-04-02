
# 基于flask实现网络共识

import hashlib      #信息安全加密
import json         #JSON格式
import datetime     #时间
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask,jsonify,request



class BlockChain:
    def __init__(self):
        self.chain = []         # 区块的列表
        self.current_trans = [] # 交易的列表
        self.nodes = set()      # 节点
        # 创建第一个区块
        self.new_block(prev_hash=1,proof=100)


    # 新建一个区块
    def new_block(self,proof, prev_hash):
        block = {
            "index" : len(self.chain)+1,            #索引
            "timestamp" : datetime.datetime.now(), #时间
            "trans" : self.current_trans,           #交易
            "proof" : proof,                        #计算力的凭证
            "prev_hash" : prev_hash or self.hash(self.chain[-1])    #上一块哈希
        }
        # 开辟新区块，交易需要被清空
        self.current_trans = []
        # 增加一个区块
        self.chain.append(block)

    # 新的交易
    def new_trans(self, sender, receiver, amount):
        self.current_trans.append({
            "sender" : sender,
            "receiver" : receiver,
            "amount" : amount
        })
        return self.last_block["index"] + 1

    # 类的静态方法
    @staticmethod
    def hash(block):
        #模块进行哈希处理，将区块处理为字符串
        block_string = json.dumps(block, sort_keys=True).encode("utf-8")
        #返回哈希值
        return hashlib.sha512(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    # 挖矿依赖于上一个模块
    # 挖矿获取工作量证明
    def proof_of_work(self, last_block):
        last_proof = last_block["proof"]    #取出计算力的凭证
        last_hash = self.hash(last_block)    #取出哈希
        proof = 0   #循环求解
        while self.valid_proof(last_proof,proof,last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof,proof):  #验证工作量正确
        guess = f'{last_proof}{proof}'.encode("utf-8") #计算的字符串编码
        guess_hash = hashlib.sha512(guess).hexdigest()  #哈希计算
        return guess_hash[:3] == "000"   #调整计算难度

    def valid_chain(self,chain):#区块校验
        last_block = chain[0] #从第一块开始校验
        current_index = 1 #索引为1

        # 循环每一个区块进行校验
        while current_index < len(chain):
            block = chain[current_index]
            if block["prev_hash"] != self.hash(last_block):
                return False

            #创建一个区块依赖算力计算，校验区块的计算算力
            if not self.valid_proof(last_block["proof"],
                                    block["proof"],
                                    last_block["prev_hash"]):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_confilicts(self):#冲突
        # 取得互联网中最长的链来替换当前的链
        neighbours = self.nodes #备份节点
        new_chain = None        #新的链表
        max_length = len(self.chain) # 最长的长度，先保存当前节点的长度

        # 刷新每个网络节点，取得最长更新
        for node in neighbours:
            # 取得其他节点的区块链
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()["length"]  #取得长度
                chain = response.json()["chain"]    #取得区块链表

                # 刷新保存最长的区块链与完成校验
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        #判断吃否为空
        if new_chain:
            self.chain = new_chain #更新成功
            return True
        else:
            return False

