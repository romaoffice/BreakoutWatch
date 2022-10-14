from targettoken import update_status
import math
import ccxt

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

def close_position(selected_market,apikey,secret):
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
					qty = format_value(position['positionAmt'],market["stepSize"])
					if(float(qty)>0):
						order = exchange.create_order(
						    symbol=market["pair"],
						    side='SELL',
						    type="MARKET",
						    amount=qty)
					orders = exchange.fetchOpenOrders(market["pair"])
					if(len(orders)>0):
						for order in orders:
							exchange.cancelOrder(order["info"]["orderId"],market["pair"])

					if "position" in selected_market["market"][i]:
						del selected_market["market"][i]["position"]
					update_status(selected_market)

def send_stoporder(market,orderamount,exchange):
	print("Trying set stop order",market["pair"])
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
			avg_price = exchange.fetchTicker(market["pair"])
			dist_percent = (market["breakoutlevel"]-float(avg_price["average"]))/market["breakoutlevel"]
			print("symbol:"+market["pair"]+"  price:"+str(avg_price["average"])+"  breakout:"+ str(market["breakoutlevel"]))
			#if dist_percent>0 and dist_percent<dist :
			order = send_stoporder(market,selected_market["amount"],exchange)
			selected_market["market"][i]["position"]=order["info"]["orderId"]
			positionlist = positionlist + " "+market["pair"]
			update_status(selected_market)
	print ("Position list")
	print (positionlist)

