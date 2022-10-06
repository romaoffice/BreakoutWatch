
import json
from datetime import datetime
import trading
import targettoken
import time 
maxPosition = 5
runmode = 0 #medium risk
# runmode = 1 #Conservative
# runmode = 2 #high risk
try:
    while True:
        dateTimeObj = datetime.now()
        today_string = dateTimeObj.strftime("%Y_%m_%d")

        # Opening JSON file
        f = open('data.json')
        selected_market = json.load(f)
        f.close()
        needupdate = False
        if selected_market["mode"]!=runmode :
            needupdate = True
        if (runmode==2):
            date_object1 = datetime.datetime.strptime(selected_market["date"], "%Y_%m_%d").date()
            date_object2 = datetime.datetime.strptime(today_string, "%Y_%m_%d").date()
            dayspan = date_object2-date_object1
            if dayspan.days>1:
                needupdate = True
        else:
            if selected_market["date"]!=today_string:
                needupdate = True
        if needupdate:
            trading.close_position(selected_market)
            selected_market = targettoken.update_token_list(runmode,maxPosition,today_string)
        trading.monitor(selected_market,maxPosition)
        time.sleep(300)
except KeyboardInterrupt:
    pass