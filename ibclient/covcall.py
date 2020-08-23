
from ibapi.contract import Contract
from datetime import datetime

class covered_call():

    def __init__(self, right: str, underlyer: Contract, strike: int, expiry: datetime):
        self.ul = underlyer
        self.strike = strike
        self.right = right
        self.expiry = expiry
        self.stkprice = 0
        self.optprice = 0

    def set_stk_price(self,price):
        self.stkprice = price

    def set_opt_price(self,price):
        self.optprice = price

    def getTimevalue(self):
        if self.stkprice > self.strike:
            #ITM
            intrinsic_val = self.stkprice - self.strike
            return self.optprice - intrinsic_val
        else:
            return self.optprice



