from shared.sharedDict import order_management_dict, market_data_dict, value_relations_dict, order_book_dict
from monitoring.monitoring import monitoring

import json
import re
import asyncio
import multiprocessing
from decimal import Decimal, getcontext


from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException 

class get_data:

	def value_relations(self, market_data_dict, order_book_dict, value_relations_dict):
		while True:
			try:
				#only locking value_relations_dict to avoid deadlocks, is fine since order_book_dict is readonly
				with value_relations_dict['lock']:
					value_relations_dict['calculated_price'] = (Decimal(order_book_dict['best_ask_price'])+Decimal(order_book_dict['best_bid_price']))/2
					value_relations_dict['oracle_calculated_price_difference'] = Decimal(value_relations_dict['calculated_price'])/Decimal(market_data_dict['base_price'])
					value_relations_dict['calculated_spread']= (Decimal(order_book_dict['best_ask_price'])/Decimal(order_book_dict['best_bid_price']))*100-100

				
				if len(order_book_dict['asks_list']) >= 50:
					value_relations_dict['total_size_asks'] = sum(Decimal(order_book_dict['asks_list'][i]) for i in range(min(len(order_book_dict['asks_list']), 50)))
					order_book_dict['asks_list'].pop(0)
					
				if len(order_book_dict['bids_list']) >= 50:
					value_relations_dict['total_size_bids'] = sum(Decimal(order_book_dict['bids_list'][i]) for i in range(min(len(order_book_dict['bids_list']), 50)))
					order_book_dict['bids_list'].pop(0)
				
				if value_relations_dict['total_size_asks'] != 0 and value_relations_dict['total_size_bids'] != 0:
					value_relations_dict['ask_bid_size_factor'] = Decimal(value_relations_dict['total_size_bids'])/Decimal(value_relations_dict['total_size_asks'])
						
			except KeyboardInterrupt:
				sys.exit("Keyboard interrupt")

			except Exception as error:
				print(error)
				print("value relations failed, continuing...")
				value_relations(self, market_data_dict, order_book_dict, value_relations_dict)
	def update_best_bid_ask(self, order_book_dict, bids, asks):
		
		if bids:
			best_bid = max(bids, key=lambda x: [0])
			order_book_dict['best_bid_price'] = best_bid[0]
			order_book_dict['best_bid_size'] = best_bid[1]

		if asks:
			best_ask = min(asks, key=lambda x: x[0])
			order_book_dict['best_ask_price'] = best_ask[0]
			order_book_dict['best_ask_size'] = best_ask[1]


	async def get_order_data(self, order_book_dict):

		api_data_asks_bids = {
		"type": "subscribe",
		"channel": "v4_orderbook",
		"id": order_book_dict['market'],
		}

		try:
			websocket_order = create_connection('wss://indexer.v4testnet.dydx.exchange/v4/ws')
			websocket_order.send(json.dumps(api_data_asks_bids))
		
			while True:
				try:
					with order_book_dict['lock']:

						api_data_asks_bids = websocket_order.recv()
						api_data_asks_bids = json.loads(api_data_asks_bids)

						if api_data_asks_bids.get('channel') == 'v4_orderbook':
							contents = api_data_asks_bids.get('contents', {})
							bids = contents.get('bids', [])
							asks = contents.get('asks', [])

							if 'price' in bids:
								print(bids)

							if bids:
								for bid in bids:
									if isinstance(bid, list) and len(bid) >= 2: 
										current_bid = bids[0]
										order_book_dict['current_bid_price'] = current_bid[0]
										order_book_dict['current_bid_size'] = current_bid[1]
										if Decimal(order_book_dict['current_bid_size']) >= 0.000001:
											order_book_dict['bids_list'].append(Decimal(order_book_dict['current_bid_size']))
										self.update_best_bid_ask(order_book_dict, bids, asks)
													
							if 'price' in asks:
									print(asks)
									#break

							if asks:
								for ask in asks:
									if isinstance(ask, list) and len(ask) >= 2: 
										current_ask = asks[0]
										order_book_dict['current_ask_price'] = current_ask[0]
										order_book_dict['current_ask_size'] = current_ask[1]
										if Decimal(order_book_dict['current_ask_size']) >= 0.000001:
											order_book_dict['asks_list'].append(Decimal(order_book_dict['current_ask_size']))
										self.update_best_bid_ask(order_book_dict, bids, asks)

				except KeyboardInterrupt:
					websocket_order.close()			
					sys.exit("Keyboard interrupt")

		except WebSocketConnectionClosedException as socket_err:
			print(socket_err)
			print("order book socket connection failed, restarting...")
			await self.get_order_data(order_book_dict)

	async def get_market_data(self, market_data_dict):

		while True:
			try:
				with market_data_dict['lock']:
					api_data_market = {
					"type": "subscribe",
					"channel": "v4_markets",
					"id": market_data_dict['market'],
					}

					websocket_market = create_connection('wss://indexer.v4testnet.dydx.exchange/v4/ws')
					websocket_market.send(json.dumps(api_data_market))
					
					# need to iterate throughh both responses or only one will be fetched
					for i in range(0, 2):
						api_data_market = websocket_market.recv()
						api_data_market = json.loads(api_data_market)
						
						if 'contents' in api_data_market:
							if 'markets' in api_data_market['contents']:
								market = order_book_dict['market']
								if market in api_data_market['contents']['markets']:						
									market_data_dict['oracle_price'] = api_data_market['contents']['markets'][market]['oraclePrice']

									price_changed = False
									
									if market_data_dict['base_price'] != market_data_dict['oracle_price']:	
											market_data_dict['old_price'] = market_data_dict['base_price']
											market_data_dict['base_price'] = market_data_dict['oracle_price']									

											if market_data_dict['old_price'] != Decimal(0.1):
												price_changed = True

									Decimal(market_data_dict['change_factor'])
									if price_changed == True:
										if Decimal(market_data_dict['old_price']) < Decimal(market_data_dict['base_price']):
											market_data_dict['change_factor'] = (Decimal(market_data_dict['base_price'])-Decimal(market_data_dict['old_price']))/Decimal(market_data_dict['old_price'])
											
										if Decimal(market_data_dict['old_price']) > Decimal(market_data_dict['base_price']):
											market_data_dict['change_factor'] = (Decimal(market_data_dict['base_price'])-Decimal(market_data_dict['old_price']))/Decimal(market_data_dict['old_price'])

								else:
									print(" ")
									print("NO MATCH FOR MARKET: ", market)
									print(" ")

				websocket_market.close()

			except WebSocketConnectionClosedException as socket_err:
				print(socket_err)
				print("market order socket connection failed, restarting...")
				await self.get_market_data(market_data_dict)
					
			except KeyboardInterrupt:
				websocket_market.close()	
				sys.exit("Keyboard interrupt")
