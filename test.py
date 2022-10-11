import ccxt

apikey = "dPj1eZ38dnCvpfaOkGgcNxtfWgVm5PFauAx08vh1pzwukJ9lrWy1xHXOpWUZWuNX"
secret = "XigfaX6htn55xIczWYds6OOFjrG15ZfCiq5K1EQrX96LjuGBm6DXHb8B71cwx64v"

exchange = ccxt.binance({
    'apiKey': apikey,
    'secret': secret,
    'options': {
        'defaultType': 'future',
    },
})  


orders = exchange.fetchOpenOrders("XRPUSDT")
print(orders)
# response = exchange.fetchBalance()
# print(response)
# print(response["USDT"]["free"])
# for item in response:
# 	print(item)
# markKlines = exchange.fetchPositions(symbols = undefined, params = {})
# print(markKlines)
# symbol = 'BTC/USDT'  # YOUR SYMBOL HERE
# market = exchange.market(symbol)