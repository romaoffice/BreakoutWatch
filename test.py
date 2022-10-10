import ccxt  # noqa: E402

a={'a':'a','bn':'b'}
if 'a' in a:
	print('ddddd')
# print('CCXT Version:', ccxt.__version__)

# exchange = ccxt.binance({
#     'apiKey': 'dPj1eZ38dnCvpfaOkGgcNxtfWgVm5PFauAx08vh1pzwukJ9lrWy1xHXOpWUZWuNX',
#     'secret': 'XigfaX6htn55xIczWYds6OOFjrG15ZfCiq5K1EQrX96LjuGBm6DXHb8B71cwx64v',
#     'options': {
#         'defaultType': 'future',
#     },
# })

# response = exchange.fetchBalance()
# print(response["USDT"]["free"])
# for item in response:
# 	print(item)
# markKlines = exchange.fetchPositions(symbols = undefined, params = {})
# print(markKlines)
# symbol = 'BTC/USDT'  # YOUR SYMBOL HERE
# market = exchange.market(symbol)