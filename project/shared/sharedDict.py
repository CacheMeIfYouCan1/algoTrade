import multiprocessing
from collections import deque
from decimal import Decimal, getcontext


manager = multiprocessing.Manager()

market_data_dict = manager.dict()
order_book_dict = manager.dict()
value_relations_dict = manager.dict()



#dict for market data

market_data_dict['market'] = 'NONE'
market_data_dict['oracle_price'] = 0.1
market_data_dict['old_price'] = Decimal(0.1)
market_data_dict['base_price'] = 0.1
market_data_dict['change_factor'] = 0
market_data_dict['acquired'] = False
market_data_dict['lock'] = manager.Lock()

#dict for order book

order_book_dict['market'] = 'NONE'
order_book_dict['current_ask_price'] = 0.1
order_book_dict['current_ask_size'] = 0.1
order_book_dict['current_bid_price'] = 0.1
order_book_dict['current_bid_size'] = 0.1
order_book_dict['best_ask_price'] = 0.1
order_book_dict['best_ask_size'] = 0.1
order_book_dict['best_bid_price'] = 0.1
order_book_dict['best_bid_size'] = 0.1
order_book_dict['asks_list'] = manager.list(deque(maxlen=50))
order_book_dict['bids_list'] = manager.list(deque(maxlen=50))
order_book_dict['acquired'] = False
order_book_dict['lock'] = manager.Lock()

#dict for relations between different values

value_relations_dict['total_size_asks'] = Decimal(0)
value_relations_dict['total_size_bids'] = Decimal(0)
value_relations_dict['calculated_spread'] = 0.1
value_relations_dict['calculated_price'] = 0.1
value_relations_dict['oracle_calculated_price_difference'] = 0
value_relations_dict['ask_bid_size_factor'] = 0
value_relations_dict['acquired'] = False
value_relations_dict['lock'] = manager.Lock()

