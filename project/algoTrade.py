import json
import sys
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException 
import asyncio
import subprocess
from decimal import Decimal, getcontext
import json
import re
import time
from collections import deque
import multiprocessing

from getData.getData import get_data
from shared.sharedDict import market_data_dict, value_relations_dict, order_book_dict

getcontext().prec = 20

market = sys.argv[1]


def run_async_task(async_func, shared_dict):
	
	loop = asyncio.get_event_loop()
	loop.run_until_complete(async_func(shared_dict))

def algoTrade(market_data_dict, order_book_dict, value_relations_dict):

	get_data_instance = get_data()
	
	process_get_market_data = multiprocessing.Process(target=run_async_task, args=(get_data_instance.get_market_data, market_data_dict))
	process_get_order_data = multiprocessing.Process(target=run_async_task, args=(get_data_instance.get_order_data, order_book_dict))
	process_value_relations = multiprocessing.Process(target=get_data_instance.value_relations, args=(market_data_dict, order_book_dict, value_relations_dict))
	
	process_get_market_data.start()
	process_get_order_data.start()
	process_value_relations.start()
	
	while True:	
		try:	
			print(" ")
			print(" ")
			print("#####################")
			print("#    new Dataset    #")
			print("#####################")

			print("current ask price:", order_book_dict['current_ask_price'])
			print("current ask size", order_book_dict['current_ask_size'])

			print("current bid price:", order_book_dict['current_bid_price'])
			print("current bid size", order_book_dict['current_bid_size'])

			print("Best bid price:", order_book_dict['best_bid_price'], "Best bid size:", order_book_dict['best_bid_size'])
			print("Best ask price:", order_book_dict['best_ask_price'], "Best ask size:", order_book_dict['best_ask_size'])

			print("base price: ", market_data_dict['base_price'])
			print("last change factor: ", market_data_dict['change_factor'])

			print("calculated price: ", value_relations_dict['calculated_price'])
			print("calculated spread: ", value_relations_dict['calculated_spread'])

			print("sum of bids: ", value_relations_dict['total_size_bids'] )
			print("sum of asks: ", value_relations_dict['total_size_asks'] )

			print("difference between oracle and calculated price: ", value_relations_dict['oracle_calculated_price_difference'])
			print("difference between ask and bid sizes: ", value_relations_dict['ask_bid_size_factor'])

			print("order side: ", order_management_dict['order_side'])
			print("order price: ", order_management_dict['order_price'])
			print("order size: ", order_management_dict['order_size'])
			print("order status: ", order_management_dict['order_status'])
			print("order id: ", order_management_dict['order_id'])

			print("close order side: ", order_management_dict['close_order_side'])
			print("close order price: ", order_management_dict['close_order_price'])
			print("close order size: ", order_management_dict['close_order_size'])
			print("close order status: ", order_management_dict['close_order_status'])
			print("close order id: ", order_management_dict['close_order_id'])

			time.sleep(2.5) # sleep 2.5 secs for better readability of output
			

		except KeyboardInterrupt:
			websocket_order.close()
			websocket_market.close()
			
			process_get_market_data.terminate()
			process_get_order_data.terminate()
			process_value_relations.terminate()

			process_get_market_data.join()
			process_get_order_data.join()	
			process_value_relations.join()

			sys.exit("Keyboard interrupt")

					
		except Exception as error:
			websocket_order.close()
			websocket_market.close()
			
			process_get_market_data.terminate()
			process_get_order_data.terminate()
			process_value_relations.terminate()

			process_get_market_data.join()
			process_get_order_data.join()	
			process_value_relations.join()

			print("error: ", error)
			print("continuing")
			algoTrade(market_data_dict, order_book_dict, value_relations_dict, order_management_dict)

def main():

	market_data_dict['market'] = market
	order_book_dict['market'] = market
	order_management_dict['lot_size'] = lot_size
	algoTrade(market_data_dict, order_book_dict, value_relations_dict)

if __name__ == "__main__":
	main()
