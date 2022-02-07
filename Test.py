from BinanceTrade.FutureTrade import *
from BinanceTrade.Trade import ReceiveSignals

if __name__ == "__main__":
    data = {
        "ACTION" : "TPSL LONG",
        "LEV" : "50",
        "SYMBOL":"BTCUSDT",
        }
    msg = ReceiveSignals(signal_data_dict= data )

    