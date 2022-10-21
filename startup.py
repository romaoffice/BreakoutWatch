
import json
from datetime import datetime
import trading
import targettoken
import ccxt
import time
import sys

runmode = 0 #medium risk
# runmode = 1 #conservative
# runmode = 2 #highrisk
if len(sys.argv)>1:
    runmode = int(sys.argv[1])
maxposition =0
apikey =''
secret =''

if runmode==0:
    maxPosition = 12
    apikey = "dPj1eZ38dnCvpfaOkGgcNxtfWgVm5PFauAx08vh1pzwukJ9lrWy1xHXOpWUZWuNX"
    secret = "XigfaX6htn55xIczWYds6OOFjrG15ZfCiq5K1EQrX96LjuGBm6DXHb8B71cwx64v"
if runmode==1:
    maxPosition = 15
    apikey = "bFVG0dhVotQul7HeVDNe6fiT8H75SJxfhiW07cHcpHz5UdGrvMBXd2obAFQIwHTn"
    secret = "ONg61BSxzm3KFsNDuQoe45OfeOeYwIy2lAh6Pc1peBrba3xDCHbWduBZX4Cxdd3Y"
if runmode==2:
    maxPosition = 10
    apikey = "WVgEoTkWR9EFtCijEYXez4if654eskAhF29bvQazyDBht7uBJm8jBFL14lbOtHe3"
    secret = "aRf9pLikKJXyGY7JFVFRw5jsWn2S5N6BlPiYCHqhyEkBYXWEpaQkyMjxosyVrIgI"

print ("runmode:",runmode," maxposition:"+str(maxPosition))
try:
    while True:
        targettoken.set_file_name('data'+str(runmode)+".json")
        dateTimeObj = datetime.now()
        today_string = dateTimeObj.strftime("%Y_%m_%d")
        # Opening JSON file
        f = open(targettoken.filename)
        selected_market = json.load(f)
        f.close()
        needupdate = False
        if selected_market["mode"]!=runmode or selected_market["date"]!=today_string:
            needupdate = True
        if needupdate:
            exchange = ccxt.binance({
                'apiKey': apikey,
                'secret': secret,
                'options': {
                    'defaultType': 'future',
                },
            })
            selected_market = trading.close_position(selected_market,apikey,secret,runmode)
            balances = exchange.fetchBalance()
            usdtbalance = balances["USDT"]["free"]
            newselected_market = targettoken.update_token_list(runmode,maxPosition,today_string,apikey,secret)
            for i,market in enumerate(newselected_market["market"]):
                have = False
                for j,market_exist in enumerate(selected_market["market"]):
                    if market_exist["pair"]==market["pair"]:
                        have = True
                        break
                if have==False:
                    selected_market.append(market)
            selected_market["date"]=newselected_market["date"]
            selected_market["amount"] = usdtbalance/maxPosition
            print(selected_market)
            targettoken.update_status(selected_market)
        trading.monitor(selected_market,maxPosition,apikey,secret)
        time.sleep(60)
except KeyboardInterrupt:
    pass
