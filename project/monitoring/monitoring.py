from shared.sharedDict import order_management_dict, market_data_dict, value_relations_dict, order_book_dict
from execution.execution import execution
import json
import re
import asyncio
from decimal import Decimal, getcontext
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException 

class monitoring:

	def monitoring_order(self, order_management_dict):
		"""
			this function monitors open initial orders, content removed
		"""

	def monitoring_close_order(self, order_management_dict):
		"""
			this functions monitors open take profit and stop loss orders, content removed
		"""

	def monitoring_market_flow(self, value_relations_dict, order_book_dict, order_management_dict):
		"""
			this function monitors the market flow to register specific conditions which indicated entries and exits, content removed
		"""
