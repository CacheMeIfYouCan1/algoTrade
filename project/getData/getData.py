from shared.sharedDict import market_data_dict, value_relations_dict, order_book_dict

import json
import sys
from decimal import Decimal
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException


class GetData:

    def value_relations(self, market_data_dict, order_book_dict, value_relations_dict):
        while True:
            try:
                with value_relations_dict['lock']:
                    best_ask = Decimal(order_book_dict['best_ask_price'])
                    best_bid = Decimal(order_book_dict['best_bid_price'])
                    base_price = Decimal(market_data_dict['base_price'])
                    
                    value_relations_dict['calculated_price'] = (best_ask + best_bid) / 2
                    value_relations_dict['oracle_calculated_price_difference'] = value_relations_dict['calculated_price'] / base_price
                    value_relations_dict['calculated_spread'] = (best_ask / best_bid) * 100 - 100

                if len(order_book_dict['asks_list']) >= 50:
                    value_relations_dict['total_size_asks'] = sum(
                        Decimal(x) for x in order_book_dict['asks_list'][:50]
                    )
                    order_book_dict['asks_list'].pop(0)

                if len(order_book_dict['bids_list']) >= 50:
                    value_relations_dict['total_size_bids'] = sum(
                        Decimal(x) for x in order_book_dict['bids_list'][:50]
                    )
                    order_book_dict['bids_list'].pop(0)

                total_asks = value_relations_dict.get('total_size_asks', 0)
                total_bids = value_relations_dict.get('total_size_bids', 0)

                if total_asks and total_bids:
                    value_relations_dict['ask_bid_size_factor'] = Decimal(total_bids) / Decimal(total_asks)

            except KeyboardInterrupt:
                sys.exit("Keyboard interrupt")
            except Exception as error:
                print(error)
                print("value relations failed, continuing...")

    def update_best_bid_ask(self, order_book_dict, bids, asks):
        if bids:
            # bids assumed to be list of [price, size]
            best_bid = max(bids, key=lambda x: x[0])
            order_book_dict['best_bid_price'] = best_bid[0]
            order_book_dict['best_bid_size'] = best_bid[1]

        if asks:
            best_ask = min(asks, key=lambda x: x[0])
            order_book_dict['best_ask_price'] = best_ask[0]
            order_book_dict['best_ask_size'] = best_ask[1]

    async def get_order_data(self, order_book_dict):
        subscription = {
            "type": "subscribe",
            "channel": "v4_orderbook",
            "id": order_book_dict['market'],
        }

        try:
            websocket_order = create_connection('wss://indexer.v4testnet.dydx.exchange/v4/ws')
            websocket_order.send(json.dumps(subscription))

            while True:
                try:
                    with order_book_dict['lock']:
                        message = websocket_order.recv()
                        data = json.loads(message)

                        if data.get('channel') != 'v4_orderbook':
                            continue

                        contents = data.get('contents', {})
                        bids = contents.get('bids', [])
                        asks = contents.get('asks', [])

                        # Process bids
                        if bids and isinstance(bids, list):
                            current_bid = bids[0]
                            if isinstance(current_bid, list) and len(current_bid) >= 2:
                                order_book_dict['current_bid_price'] = current_bid[0]
                                order_book_dict['current_bid_size'] = current_bid[1]
                                if Decimal(order_book_dict['current_bid_size']) >= 0.000001:
                                    order_book_dict['bids_list'].append(Decimal(order_book_dict['current_bid_size']))
                                    self.update_best_bid_ask(order_book_dict, bids, asks)

                        # Process asks
                        if asks and isinstance(asks, list):
                            current_ask = asks[0]
                            if isinstance(current_ask, list) and len(current_ask) >= 2:
                                order_book_dict['current_ask_price'] = current_ask[0]
                                order_book_dict['current_ask_size'] = current_ask[1]
                                if Decimal(order_book_dict['current_ask_size']) >= 0.000001:
                                    order_book_dict['asks_list'].append(Decimal(order_book_dict['current_ask_size']))
                                    self.update_best_bid_ask(order_book_dict, bids, asks)

                except KeyboardInterrupt:
                    websocket_order.close()
                    sys.exit("Keyboard interrupt")

        except WebSocketConnectionClosedException as e:
            print(e)
            print("order book socket connection failed, restarting...")
            await self.get_order_data(order_book_dict)

    async def get_market_data(self, market_data_dict):
        subscription = {
            "type": "subscribe",
            "channel": "v4_markets",
            "id": market_data_dict['market'],
        }

        try:
            websocket_market = create_connection('wss://indexer.v4testnet.dydx.exchange/v4/ws')
            websocket_market.send(json.dumps(subscription))

            for _ in range(2):  # Read 2 messages
                message = websocket_market.recv()
                data = json.loads(message)

                contents = data.get('contents')
                if not contents:
                    continue

                markets = contents.get('markets')
                if not markets:
                    continue

                market = market_data_dict['market']
                if market not in markets:
                    print(f"\nNO MATCH FOR MARKET: {market}\n")
                    continue

                oracle_price = markets[market].get('oraclePrice')
                if oracle_price is None:
                    continue

                old_price = market_data_dict.get('base_price')
                if old_price != oracle_price:
                    market_data_dict['old_price'] = old_price
                    market_data_dict['base_price'] = oracle_price

                    # avoid first initialization factor calculation
                    if old_price != Decimal('0.1'):
                        if Decimal(old_price) != 0:
                            change_factor = (Decimal(oracle_price) - Decimal(old_price)) / Decimal(old_price)
                            market_data_dict['change_factor'] = change_factor

            websocket_market.close()

        except WebSocketConnectionClosedException as e:
            print(e)
            print("market order socket connection failed, restarting...")
            await self.get_market_data(market_data_dict)

        except KeyboardInterrupt:
            websocket_market.close()
            sys.exit("Keyboard interrupt")
