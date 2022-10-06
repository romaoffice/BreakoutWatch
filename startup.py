
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

        if selected_market["runmode"]!=runmode or (("date" in selected_market) and selected_market["date"]!=today_string):
            trading.close_position(selected_market)
            selected_market = targettoken.update_token_list(runmode,maxPosition,today_string)
        trading.monitor(selected_market,maxPosition)
        time.sleep(300)
except KeyboardInterrupt:
    pass
