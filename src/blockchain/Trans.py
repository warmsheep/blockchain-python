import datetime

class Trans:

    # payer 付款方
    # receiver 收款方
    # money 数字货币中的数字
    def __init__(self, payer, receiver, money):
        self.payer = payer
        self.receiver = receiver
        self.money = money
        self.timestamp = datetime.datetime.now()

    def __repr__(self):
        return str(self.payer) + " pay " + str(self.receiver) + " " + str(self.money) + " " + str(self.timestamp)

if __name__ == "__main__":
    t1 = Trans("linxuan", "linxuan2", 20) # 后续需要整合密钥私钥
    t1 = Trans("linxuan2", "linxuan3", 20)
    t1 = Trans("linxuan3", "linxuan4", 20)
    print(t1)