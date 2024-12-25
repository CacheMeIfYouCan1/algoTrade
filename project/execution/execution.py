from shared.sharedDict import order_management_dict, market_data_dict, value_relations_dict, order_book_dict

import json
import re
import subprocess
import multiprocessing

json_pattern = re.compile(r'\{.*?\}', re.DOTALL)

class execution:

	def close_buy_order(order_management_dict):
		"""
			this function closes a long position of certain size, at a certain price, if certain conditions are met, content removed
		"""


	def place_buy_order(order_management_dict):
		"""
			this function opens a long position of certain size, at a certain price, if certain conditions are met, content removed
		"""

	def close_sell_order(order_management_dict):
		"""
			this function closes a short position of certain size, at a certain price, if certain conditions are met, content removed
		"""

	def place_sell_order(order_management_dict):
		"""
			this function opens a short position of certain size, at a certain price, if certain conditions are met, content removed
		"""
