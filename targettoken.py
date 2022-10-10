import json
import requests
import time
import pandas as pd
from ta.volatility import AverageTrueRange
from ta.trend import SMAIndicator
from binance import Client
import ccxt

stablecoin = ['usdp','cusdc','usdt','usdc','busd','dai']
filename = 'data.json'
def set_file_name(name):
    global filename
    filename = name
def get_top_100():
    top100 = {}
    while len(top100)==0:
        try:
            response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=120&page=1")
            top100stream = response.json()
            topitems = 0
            for item in top100stream:
                isstable = False
                for stable in stablecoin:
                    if(item["symbol"]==stable):
                        isstable = True
                        break
                if isstable==False:
                    top100[item["symbol"].upper()] = {"symbol":item["symbol"].upper()}
                    topitems = topitems+1
                    if topitems>=100:
                        break
        except:
            print("Get error while scrap top100 tokens")
        if(len(top100) >0):
            break
        print("Failed to get top100 coins. It will run again after 60seconds.")
        time.sleep(60)
    return top100

def convert_df_candles(candles):
    open_t = []
    open_p = []
    high_p = []
    low_p = []
    close_p = []
    volume_p = []
    close_t = []
    for item in candles:
        open_t.append(float(item[0]))
        open_p.append(float(item[1]))
        high_p.append(float(item[2]))
        low_p.append(float(item[3]))
        close_p.append(float(item[4]))
        volume_p.append(float(item[5]))
    pd_data = pd.DataFrame(list(zip(open_t, open_p,high_p,low_p,close_p,volume_p)),
               columns =['open_t', 'open','high','low','close','volume'])
    return pd_data

def get_score(candles):

    prevclose = float(candles[len(candles)-8][4])
    curclose = float(candles[len(candles)-1][4])
    score = 1000+100*(curclose-prevclose)/prevclose
    return score

def get_breakoutlevel(df_candles,runmode):
    #Max(Ref(H,-1),Ref(H,-2)) + 0.25*Ref(ATR(7),-1);
    prevhigh1 = df_candles["high"].iloc[-1]
    prevhigh2 = df_candles["high"].iloc[-2]
    atrclass = AverageTrueRange(df_candles["high"],df_candles["low"],df_candles["close"],7)
    atr = atrclass.average_true_range()
    if runmode==0:
        breakoutlevel = max([prevhigh1,prevhigh2])+0.25*atr.iloc[-1]
    else:
        breakoutlevel = max([prevhigh1,prevhigh2])+0.5*atr.iloc[-1]    
    return breakoutlevel

def check_long_condition(df_candles):
    # 2. Close>MA20. 
    # 3. ROC(30)>ROC(7) 
    # 4. ROC(30)>0; 
    maclass = SMAIndicator(df_candles["close"],20)
    ma = maclass.sma_indicator()
    if df_candles["close"].iloc[-1] <= ma.iloc[-1]:
        return False
    roc30 = 100*(df_candles["close"].iloc[-1]-df_candles["close"].iloc[-31])/df_candles["close"].iloc[-31]
    roc7 = 100*(df_candles["close"].iloc[-1]-df_candles["close"].iloc[-8])/df_candles["close"].iloc[-8]

    if roc30<=0:
        return False
    if(roc30<=roc7):
        return False

    return True

def update_token_list(runmode,maxPosition,today_string,apikey,secret):
    print("Getting Universe Top 100 coins from coingeko")
    top100 = get_top_100()
    # top100 = {"BNB":{"symbol":"BNB"},"ETH":{"symbol":"ETH"},"MATIC":{"symbol":"MATIC"},"BTC":{"symbol":"BTC"}}
    #top100 = {"BNB":{"symbol":"BNB"}}
    # get market depth
    #client = Client("dPj1eZ38dnCvpfaOkGgcNxtfWgVm5PFauAx08vh1pzwukJ9lrWy1xHXOpWUZWuNX", "XigfaX6htn55xIczWYds6OOFjrG15ZfCiq5K1EQrX96LjuGBm6DXHb8B71cwx64v")
    #client = Client("", "")
    
    exchange = ccxt.binance({
        'apiKey': apikey,
        'secret': secret,
        'options': {
            'defaultType': 'future',
        },
    })

    print("Getting trend score,breakout level from binance price data")
    # prepare market data for binance
    info = exchange.load_markets()
    print("Got exchange info");
    for pair in top100:
        if(pair+"/USDT") in info:
            pairinfo = info[pair+"/USDT"]
            symbol = pairinfo["info"]["symbol"]
            print("Getting trend score for ",symbol)
            top100[pairinfo["baseId"]]["pair"] = symbol
            for filteritem in pairinfo["info"]["filters"]:
                if(filteritem["filterType"]=="PRICE_FILTER"):
                    top100[pairinfo["baseId"]]["tickSize"] = filteritem["tickSize"]
                if(filteritem["filterType"]=="MARKET_LOT_SIZE"):
                    top100[pairinfo["baseId"]]["stepSize"] = filteritem["stepSize"]

            candles = exchange.fetchOHLCV (symbol, '1d')
            del candles[-1]
            if(len(candles)>30):
                df_candles = convert_df_candles(candles)
                top100[pairinfo["baseId"]]["score"] = get_score(candles)
                print(pairinfo["baseId"],top100[pairinfo["baseId"]]["score"])
                top100[pairinfo["baseId"]]["breakoutlevel"] = get_breakoutlevel(df_candles,runmode)
                top100[pairinfo["baseId"]]["check_long_condition"] = check_long_condition(df_candles)
            else:
                top100[pairinfo["baseId"]]["nocandle"] = True

    #sorting
    selected_market = []
    for num in range(0, maxPosition):
        maxscore = 0
        selectedtoken = ""
        for token in top100:
            if (not("nocandle" in top100[token]) and  ("check_long_condition" in top100[token]) and top100[token]["check_long_condition"]  and top100[token]["score"]>maxscore):
                selectedtoken = token
                maxscore = top100[token]["score"]
        if(selectedtoken!=""):
            selected_market.append(top100[selectedtoken])
            top100.pop(selectedtoken)
        else:
            break

    print("Selected Market list")

    for selected in selected_market:
        print("Symbol:",selected["symbol"]," breakout level:",selected["breakoutlevel"]," Score:",selected["score"])

    stored_selected_market = {"mode":runmode,"date":today_string,"market":selected_market}
    update_status(stored_selected_market)

    return stored_selected_market

def update_status(stored_selected_market):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stored_selected_market, f, ensure_ascii=False, indent=4)
