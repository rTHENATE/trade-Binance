from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *

import math #< แก้ไข 6-27-2021

try:
    from config_dev import API_BINANCE_KEY , API_BINANCE_SECRET
except:
    from config_prod import API_BINANCE_KEY , API_BINANCE_SECRET

request_client = RequestClient(api_key=API_BINANCE_KEY,secret_key=API_BINANCE_SECRET)

size_precision = {
    "BTC" : 3,
    "BNB": 2,
    "SOL": 0
}

def round_down(num,digits): #< แก้ไข เพิ่ม function 6-27-2021
    factor = 10.0 ** digits
    return math.floor(num * factor) / factor

def calForPosition(price,tp,sl,side,amount_usdt): #< แก้ไข เพิ่ม function 6-27-2021

    tp_price = ""
    sl_price = ""
    cal_amount = ""

    count_digit = len(str(price).split(".")[1])
    
    
    cal_tp_price = 0
    cal_sl_price = 0
        
    if side == "LONG":
        cal_tp_price = float(price) * (1 + tp/100)
        cal_sl_price = float(price) * (1 - sl/100)

    elif side == "SHORT":
        cal_tp_price = float(price) * (1 - tp/100)
        cal_sl_price = float(price) * (1 + sl/100)

    # order format compare to price
    tp_price = str(round_down(cal_tp_price,count_digit))
    sl_price = str(round_down(cal_sl_price,count_digit-2))

    # size cal
    size = amount_usdt/float(price)
    if float(price) > 1000:
        size = round_down(size,3)
    elif 200 < float(price) < 1000:
        size = round_down(size,2)
    elif 50 < float(price) < 200:
        size = round_down(size,1)
    elif 0 < float(price) <= 50:
        size = int(size)
        
    return tp_price , sl_price , size


def get_market_data_by_symbol(symbol):
    result = request_client.get_mark_price(symbol=symbol)
    return result.__dict__


def change_leverage(symbol,lev):
    result = request_client.change_initial_leverage(symbol,lev)
    return result.__dict__

def CancelAllOrder(symbol):
    result = request_client.cancel_all_orders(symbol)
    return result.__dict__

def getAssetUSDT():
    result = request_client.get_balance()
    return int(result[1].balance)

# เพิ่ม function 01-27-2022
def PlaceOrderAtMarket(position,symbol,amount,act_price_percent=2,cb=3,stoploss_Percent = 5,lev=10):


    CancelAllOrder(symbol = symbol)
    current_price = float(get_market_data_by_symbol(symbol)["markPrice"])
    amount = amount * lev
    change_leverage(symbol=symbol,lev=lev)
    if position == "LONG":

        act_price_LONG , sl , size = calForPosition(price=current_price,
                                                    tp=act_price_percent,
                                                    sl=stoploss_Percent,
                                                    side="LONG",
                                                    amount_usdt=amount
                                                )

        
        #  position
        try:
            result = request_client.post_order(
                symbol = symbol ,
                side = OrderSide.BUY ,
                positionSide = "BOTH" ,
                ordertype=OrderType.MARKET ,
                quantity = str(size) # 0.02 --> 0.019999999
            )
        except Exception as e:
            print(e.error_message)
    
    elif position == "SHORT":

        act_price_SHORT , sl , size = calForPosition(price=current_price,
                                                    tp=act_price_percent,
                                                    sl=stoploss_Percent,
                                                    side="SHORT",
                                                    amount_usdt=amount
                                                )
        
        try:
            result = request_client.post_order(
                symbol = symbol ,
                side = OrderSide.SELL ,
                positionSide = "BOTH" ,
                ordertype=OrderType.MARKET ,
                quantity = str(size) # 0.02 --> 0.019999999
            )
        except Exception as e:
            print(e.error_message)

def getPositionbySymbol(Symbol):
    result = request_client.get_position_v2()
    for i in result:
        if i.symbol == Symbol:
            return i.__dict__

def ClosePositionAtMarket(symbol,positionSide):

    amount = getPositionbySymbol(symbol)['positionAmt']

    if positionSide == "LONG":
        result = request_client.post_order(
            symbol=symbol,
            side=OrderSide.SELL,
            ordertype=OrderType.MARKET,
            positionSide="BOTH",
            quantity=str(abs(float(amount))),
            reduceOnly=True
        )
    
    elif positionSide == "SHORT":
        result = request_client.post_order(
            symbol=symbol,
            side=OrderSide.BUY,
            ordertype=OrderType.MARKET,
            positionSide="BOTH",
            quantity=str(abs(float(amount))),
            reduceOnly=True
        )

