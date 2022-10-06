from binance import Client
from targettoken import update_status
from binance.enums import *
import math

apikey = "NwcCcwBGbDxflyeTLSK8NvMJZd3rvvq5e5VwchCQmGf3eP9qVphqrXAKNpcngX4O"
apisecret = "UCdgcNQqiquKP6IIC5bzv5gIB6ya3PUqoGYJntNlmWXuUCBmtgoMbFfUMdSRhl7l"

apikey = "dPj1eZ38dnCvpfaOkGgcNxtfWgVm5PFauAx08vh1pzwukJ9lrWy1xHXOpWUZWuNX"
apisecret = "XigfaX6htn55xIczWYds6OOFjrG15ZfCiq5K1EQrX96LjuGBm6DXHb8B71cwx64v"


dist = 0.1
orderamount =20
client = Client(apikey, apisecret)

def step_size_to_precision(ss):
    return ss.find('1') - 1


def format_value(val, step_size_str):
	precision = step_size_to_precision(step_size_str)
	if precision > 0:
		return "{:0.0{}f}".format(val, precision)
	return math.trunc(int(val))	

def close_position(selected_market):
	print("Trying close all position")
	balance = client.get_account()
	print(balance['balances'])
	for i,market in enumerate(selected_market["market"]):
		if "position" in selected_market["market"][i]:
			print("Trying close all position from "+market["pair"])
			orders = client.get_open_orders(symbol=market["pair"])
			if(len(orders)>0):
				orders = client._delete('openOrders', True, data={'symbol': market["pair"]})
			tokenbalance = 0
			for bal in balance['balances']:
				if bal['asset'].lower() == (market["symbol"]).lower():
					tokenbalance = float(tokenbalance["free"])   	
			qty = format_value(tokenbalance,market["stepSize"])
			if(float(qty)>0):
				order = client.create_order(
				    symbol = market["pair"], 
				    side = SIDE_SELL, 
				    type = ORDER_TYPE_MARKET, 
				    quantity = qty)
			if "position" in selected_market["market"][i]:
				del selected_market["market"][i]["position"]
			update_status(selected_market)

def send_stoporder(market):
	print("Trying set stop order",market["pair"])
	breaklevel = format_value(market["breakoutlevel"],market["tickSize"])
	qty = format_value(float(orderamount)/float(breaklevel),market["stepSize"])


	order = client.create_order(
	    symbol = market["pair"], 
	    side = SIDE_BUY, 
	    type = ORDER_TYPE_STOP_LOSS_LIMIT, 
	    timeInForce = TIME_IN_FORCE_GTC, 
	    quantity = qty, 
	    price = breaklevel, 
	    stopPrice = breaklevel)
	return order

def monitor(selected_market,maxPosition):
	limit_positions = 0
	positionlist = ""
	for market in selected_market["market"]:
		if "position" in market:
			limit_positions = limit_positions + 1
			positionlist = positionlist + " "+market["pair"]
	if(limit_positions>=maxPosition):
		print ("Position list")
		print (positionlist)
		return
	positionlist =""
	for i,market in enumerate(selected_market["market"]):
		if "position" in market:
			positionlist = positionlist + " "+market["pair"]
		else:
			avg_price = client.get_avg_price(symbol=market["pair"])
			dist_percent = (market["breakoutlevel"]-float(avg_price["price"]))/market["breakoutlevel"]
			print("symbol:"+market["pair"]+"  price:"+avg_price["price"]+"  breakout:"+ str(market["breakoutlevel"]))
			if dist_percent>0 and dist_percent<dist :
				order = send_stoporder(market)
				selected_market["market"][i]["position"]=order["orderId"]
				positionlist = positionlist + " "+market["pair"]
				update_status(selected_market)
	print ("Position list")
	print (positionlist)

