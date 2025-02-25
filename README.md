# algoTrade


<p><strong>Please note that the financial markets are very competitional. Therefore several parts, which would give away the market edge, were removed.</strong></p>


This is a fully automated cryptotrading algorithm, a private long-term project which is currently profitably trading BTC/USD and DOGE/USD on the DYDX exchange. This project is showcased to display understanding for modular python projects, as well as websockets, asynchronous programming, multiprocessing and the usage of shared dictionaries while avoiding race conditions and deadlocks. 

This documentation is made for Debian based systems

## Setup

### Setting up the development environment

first we install virtualvenv

<code>$ pip install virtualenv </code>

create a directory for the algoTrading bot

<code>$ mkdir algoTrading</code>
 
<code>$ cd algoTrading</code>

next we need to create a virtual environment and source it

<code>$ python -m venv algoVenv</code>$
 
<code>$ source /algoVenv/bin/activate</code>$


Finally we need to install the required packages

<code> $ pip install -r requirements.txt </code>


### clone the repository 

<code> git clone https://github.com/CacheMeIfYouCan1/algoTrade/ </code>


## Documentation

### shared/sharedDict.py

This contains the dirctionaries which contains all variables that are needed within the different classes. It is structured as following:

#### market data dictionary
>market_data_dict['market']
used to determine which market is being analyzed 
>market_data_dict['oracle_price']
stores oracle price as displayed by exchange
>market_data_dict['old_price']
stores the last oracle price before the most recent price change
>market_data_dict['base_price']
stores the last oracle price fetched
>market_data_dict['change_factor']
a factor determining how much the price has changed 
>market_data_dict['acquired']
used to keep track of manual lock/release
>market_data_dict['lock']
used for locking


#### order book data dictionary
order_book_dict['market']                                         used to determine which market is being analyzed 
order_book_dict['current_ask_price']                              last fetched ask price
order_book_dict['current_ask_size']                               size of the last fetched ask order
order_book_dict['current_bid_price']                              last bid price
order_book_dict['current_bid_size']                               size of the last bid order
order_book_dict['best_ask_price']                                 best ask price of the last x orders
order_book_dict['best_ask_size']                                  size of the last best ask order
order_book_dict['best_bid_price']                                 best bid price of the last x orders
order_book_dict['best_bid_size']                                  size of the last best bid order
order_book_dict['asks_list']                                      list containing ask price and size
order_book_dict['bids_list']                                      list containing bid price and size
order_book_dict['acquired']                                       used to keep track of manual lock/release
order_book_dict['lock']                                           used for locking


#### dictionary to keep track of relations between values
value_relations_dict['total_size_asks']                           sum of the last x ask sizes
value_relations_dict['total_size_bids']                           sum of the last x bid sizes        
value_relations_dict['calculated_spread']                         calculated spread between best ask and bid
value_relations_dict['calculated_price']                          price, calculated with bids and asks 
value_relations_dict['oracle_calculated_price_difference']        difference between the calculated and the oracle price
value_relations_dict['ask_bid_size_factor']                       factor how much difference is between bids 
                                                                  and asks in relation to the price
value_relations_dict['acquired']                                  used to keep track of manual lock/release     
value_relations_dict['lock']                                      used for locking


#### dictionary for order management                  
order_management_dict['lot_size']                                 size of current lot
order_management_dict['order_id']                                 order id of current order
order_management_dict['order_side']                               side of current order
order_management_dict['order_size']                               size of current order
order_management_dict['order_price']                              execution price of current order
order_management_dict['order_status']                             status of current order
order_management_dict['close_order_id']                           id of closing order
order_management_dict['close_order_side']                         side of closing order
order_management_dict['close_order_size']                         size of closing order
order_management_dict['close_order_price']                        execution price for closing order
order_management_dict['close_order_status']                       close order status
order_management_dict['acquired']                                 used to keep track of manual lock/release
order_management_dict['lock']                                     used for locking





