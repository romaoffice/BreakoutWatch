from targettoken import update_status
from datetime import datetime
import math
import ccxt
import time

dist = 0.1

def step_size_to_precision(ss):
    return ss.find('1') - 1

def round_down(value, decimals):
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

def format_value(val, step_size_str):
	precision = step_size_to_precision(step_size_str)
	if precision > 0:
		v = round_down(float(val),int(precision))
		r = "{:0.0{}f}".format(v, precision)
		return r
	return math.trunc(int(val))	

def close_position(selected_market,apikey,secret,runmode):
	exchange = ccxt.binance({
		'apiKey': apikey,
		'secret': secret,
		'options': {
			'defaultType': 'future',
		},
	})
	print("Trying close all position")
	positions = exchange.fapiPrivateV2_get_positionrisk()
	for i,market in enumerate(selected_market["market"]):
		if "position" in selected_market["market"][i]:
			for position in positions:
				if(position["symbol"]==market["pair"]):
					print("Trying close all position from "+market["pair"])
					orders = exchange.fetchOpenOrders(market["pair"])
					if(len(orders)>0):
						print("cancel orders from ",market["pair"])
						for order in orders:
							exchange.cancelOrder(order["info"]["orderId"],market["pair"])
						time.sleep(5)

					qty = position['positionAmt']
					if(float(qty)>0):
						if (runmode==2):
							selected_market["market"][i]["date"]
							dateTimeObj = datetime.now()
							today_string = dateTimeObj.strftime("%Y_%m_%d")
							date_object1 = datetime.strptime(selected_market["date"], "%Y_%m_%d").date()
							date_object2 = datetime.strptime(today_string, "%Y_%m_%d").date()
							dayspan = date_object2-date_object1
							if dayspan.days>=2:
								order = exchange.create_order(
								    symbol=market["pair"],
								    side='SELL',
								    type="MARKET",
								    amount=qty,
								    params={"reduceOnly": True})
								del selected_market["market"][i]
						else:
							order = exchange.create_order(
							    symbol=market["pair"],
							    side='SELL',
							    type="MARKET",
							    amount=qty,
							    params={"reduceOnly": True})
							del selected_market["market"][i]
					else:
						del selected_market["market"][i]
					
		else:
			del selected_market["market"][i]
		update_status(selected_market)
	return selected_market

def send_stoporder(market,orderamount,exchange):
	print("Trying set stop order",market["pair"],market["breakoutlevel"])
	breaklevel = format_value(market["breakoutlevel"],market["tickSize"])
	qty = format_value(float(orderamount)/float(breaklevel),market["stepSize"])
	order = exchange.create_order(
	    symbol=market["pair"],
	    side='BUY',
	    type="STOP_MARKET",
	    amount=qty,
	    params = {'stopPrice':breaklevel})
	return order

def monitor(selected_market,maxPosition,apikey,secret):
	exchange = ccxt.binance({
		'apiKey': apikey,
		'secret': secret,
		'options': {
			'defaultType': 'future',
		},
	})	
	positionlist = ""
	for i,market in enumerate(selected_market["market"]):
		avg_price = exchange.fetchTicker(market["pair"])
		dist_percent = (market["breakoutlevel"]-float(avg_price["average"]))/market["breakoutlevel"]
		selected_market["market"][i]["dist_percent"]=dist_percent
		print("symbol:"+market["pair"]+"  dist_percent:"+str(dist_percent))
	for i in range(0, len(selected_market["market"])-1):
		for j in range(i+1, len(selected_market["market"])):
			if selected_market["market"][i]["dist_percent"]>selected_market["market"][j]["dist_percent"]:
				temp = selected_market["market"][i]
				selected_market["market"][i] = selected_market["market"][j]
				selected_market["market"][j] = temp
	limit_positions = 0
	for i,market in enumerate(selected_market["market"]):
		if(limit_positions<maxPosition):
			if "position" in market:
				limit_positions = limit_positions + 1
				positionlist = positionlist + " "+market["pair"]
				print("position have",market["pair"])
			else:
				dateTimeObj = datetime.now()
				today_string = dateTimeObj.strftime("%Y_%m_%d")
				order = send_stoporder(market,selected_market["amount"],exchange)
				selected_market["market"][i]["position"]=order["info"]["orderId"]
				selected_market["market"][i]["date"]=today_string
				limit_positions = limit_positions + 1
				positionlist = positionlist + " "+market["pair"]
				update_status(selected_market)
				print("position placed",market["pair"])
		else:
			if (market["dist_percent"]>0):
				try:
					orderId = selected_market["market"][i]["position"]
					del selected_market["market"][i]["position"]
					exchange.cancelOrder(orderId,market["pair"])
					update_status(selected_market)
					print("position canceled",market["pair"])

				except:
					pass
	print ("Position list")
	print (positionlist)

