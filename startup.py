
import json
from datetime import datetime
import trading
import targettoken
import time 
# runmode = 0 #medium risk
# maxPosition = 9
# runmode = 1 #conservative
# maxPosition = 10
runmode = 2 #highrisk
maxPosition = 10
try:
    while True:
        print("Run mode",runmode)
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
            date_object1 = datetime.strptime(selected_market["date"], "%Y_%m_%d").date()
            date_object2 = datetime.strptime(today_string, "%Y_%m_%d").date()
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
