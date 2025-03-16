# algoTrade



## Table of Contents

1. [Introduction](#Introduction)
2. [Setup](#Setup)
3. [Documentation](#Documentation)
   1. [Dictionaries](#dictionaries)
   2. [Scripts](#Scripts)
4. [Usage](#Usage)
5. [License](#license)

## Introduction

<p><strong>Please note that this project is not a complete trading bot! The provided scripts are only a base foundation, which gathers all necessary data, 
 to build a profitable trading bot. The strategy which was built on top of this foundation will not be disclosed.</strong></p>

 

This documentation is made for Debian based systems




## Setup

### Setting up the development environment

first we install virtualvenv

<code>$ pip install virtualenv </code>

create a directory for the algoTrading bot

<code>$ mkdir algoTrading</code>
 
<code>$ cd algoTrading</code>

next we need to create a virtual environment and source it

<code>$ python3 -m venv algoVenv</code>
 
<code>$ source algoVenv/bin/activate</code>

clone the repository and install the required components

<code> $ git clone https://github.com/CacheMeIfYouCan1/algoTrade/ </code>

<code> $ cd algoTrade</code>

<code> $ cd project </code>

<code> $ pip install -r requirements.txt </code>

now the project is set up 

## Documentation

### Dictionaries

### shared/sharedDict.py:

This contains the dirctionaries which contains all variables that are needed within the different classes. It is structured as following:

#### market data dictionary :
| Variable | Description |
|----------------------------|-----------------------|
| market_data_dict['market'] | used to determine which market is being analyzed |
| market_data_dict['oracle_price'] | stores oracle price as displayed by exchange |
| market_data_dict['old_price'] | stores the last oracle price before the most recent price change |
| market_data_dict['base_price'] | stores the last oracle price fetched |
| market_data_dict['change_factor'] | factor determining how much the price has changed |
| market_data_dict['acquired'] | used to keep track of manual lock/release |
| market_data_dict['lock'] | used for locking |


#### order book data dictionary:
| variable | Description |
|----------|-------------|
| order_book_dict['market'] | used to determine which market is being analyzed | 
| order_book_dict['current_ask_price'] | last fetched ask price |
| order_book_dict['current_ask_size'] | size of the last fetched ask order |
| order_book_dict['current_bid_price'] | last bid price | 
| order_book_dict['current_bid_size'] | size of the last bid order |
| order_book_dict['best_ask_price'] | best ask price of the last x orders |
| order_book_dict['best_ask_size'] | size of the last best ask order |
| order_book_dict['best_bid_price'] | best bid price of the last x orders |
| order_book_dict['best_bid_size'] | size of the last best bid order |
| order_book_dict['asks_list'] | list containing ask price and size |
| order_book_dict['bids_list'] | list containing bid price and size |
| order_book_dict['acquired'] | used to keep track of manual lock/release |
| order_book_dict['lock'] | used for locking |


#### dictionary to keep track of relations between values:
| variable | Description |
|----------|-------------|
| value_relations_dict['total_size_asks'] | sum of the last x ask sizes |
| value_relations_dict['total_size_bids] | sum of the last x bid sizes |        
| value_relations_dict['calculated_spread'] | calculated spread between best ask and bid |
| value_relations_dict['calculated_price'] | price, calculated with bids and asks | 
| value_relations_dict['oracle_calculated_price_difference'] | difference between the calculated and the oracle price |
| value_relations_dict['ask_bid_size_factor'] | factor how much difference is between bids and asks sizes  |
| value_relations_dict['acquired'] | used to keep track of manual lock/release |     
| value_relations_dict['lock'] | used for locking |


------------------------------------------------------------------------------------------------

### Scripts

### getData/getData.py:

This class contains all functions which retrieve data and determine the relations between the retrieved data.
Most functions are running within an infinite loop and a recursion is implemented in case of error, through a try-catch block.
This is to ensure that the processes are always running.


#### <ins>value_relations():</ins>

this function takes the folllowing three arguments:

 1. market_data_dict
 2. order_book_dict
 3. value_relations_dict

and determines the relation between the fetched data, to store it in the value_relations_dict. Therefore 
market_data_dict and order_book_dict are accessed read-only and not written to. Both dictionaries should not be locked, 
because the contained data is simultaneously fetched and written in getData.py while being read by value_relations.py. 
Locking these dictionaries will therefore cause deadlocks. 

This has one minor flaw: the data which is used to calculate the relations between the values can lag behind. This
flaw an be neglected, because the relations express speculative tendencies instead of absolute states, since the 
fetched data is also speculative and will fluctuated based on the exchange used as a data source.

value_relations executes three tasks:

##### estimating the relations of fetched data:

In the first part of the function, we estimate the oracle_calculated_price_difference, calculated_spread and 
the calculated_price and propagate the corresponding variables in the dictionary, while it is locked, to avoid deadlocks.

the values are estimated as following:

| value | estimation |
|-------|------------|
| oracle_calculated_price_difference | calculated_price / base_price |
| calculated_spread | best_ask_price / best_bid_price * 100 - 100 |
| calculated_price | best_ask_price + best_bid_price / 2 |


##### estimating total size of asks and bids:

the task which is done, is simply to iterate through all content of our asks_list and bids_list at the size
dimension and summing the values up. This is limited to the last 50 entries, since we only store 50 value pairs in the given 
lists.

##### estimating the relations between asks and bids:

finally we estimate the relation between the ask sizes and the bid sizes by dividing them. This will give us an overview
if there are generally more aks or bid orders open in the orderbook, and how big this difference is. 

#### <ins>update_best_bid_ask():</ins>

The function takes three arguments:

 1. order_book_dict
 2. bids
 3. asks

It propagates order_book_dict with the highes bid and the lowest ask, together with their corresponding size. It is not 
necessary to lock the dictionary, because these variables are set nowhere else. Locking the dictionary at this point 
without checking if its locked already could cause deadlocks.

#### <ins>get_order_data():</ins>

get_order_data takes only the order_book_dict as an argument. The function is designed to fetch the order book data from
the exchange and propagate the dictionary with all relevant data, while cutting out the noise. 

##### key considerations:

Its important to consider that the data is fetched as a stream, which is why the socket connection needs to be established 
before the infinite while loop. This is to ensure that there is only one socket connection open, which fetches
the data stream. Its also important to lock the order_book_dict at this point, to avoid race-conditions.

The data is fetched in json format and the relevant fields are stored as a two dimensional array, which consists of the bid/ask value 
and the corresponding size of the order. Datasets can be either ask or bid data, every dataset represents one open order. 

Unfortunately the fetched data seems to be corrupted sometimes, We can validate that by checking if the dataset contains 'price'.

All fetched orders are open at the time when they are fetched. Some orders contain the size '0', they are filtered out
as they would interfere with the estimation of the value relations.

##### functionality:
the logic is simple and can be summarized as following:

If a bid or ask order is present, the values are stored in the the dictionary. If their size is bigger than 0,
their value will be appended to the corresponding list and the best bid/ask price is updated.

##### limitations:

The fetched orders are open at the time when they are received, we do not know when they get filled, cancelled or when they 
do expire. 

Orders which are immediately filled, do not appear in the orderbook.

#### <ins>get_market_data()</ins>

get_market_data takes only the market_data_dict as an argument. This function is built to fetch the market data from the 
exchange and propagate the dictionary with all relevant data, while cutting out the noise. 

##### key_considerations: 

unlike the order book data, the market data is not fetched as a stream. This is why we want to open and close the websocket 
within the infinite while-loop. It is important to lock the market data, to avoid race conditions. 

The market data is fetched in json format. For the currently used trading style, the only relevant field within the market data
is the oracle price. 

Unfortunately the fetched data seems to be corrupted sometimes, We can validate that by checking if all necessary party are present 
in the json. The fetched data comes in two responses and its necessary to iterate through both.

##### functionality:

The logical functionality consists of three tasks:

1. store the oracle price in the dictionary
2. determine if the price has changed and
3. estimate the factor of the recent price change

##### limitations:

See definition of Oracle price in context of crypto-trading. 


------------------------------------------------------------------------------------------------


### /algoTrade.py

this script is used to start the algoTraging program and contains following functions:

#### <ins>run_async_task():</ins>

run_async_task takes the task and the corresponding dictionary as arguments. It is used to start asynchronous tasks within a process. 
This is to merge and asynchronous approach with multiprocessing.

#### <ins>algo_trade():</ins>

Core function, this is used to start the programm. This is done by defining the processes and starting them, then afterwards 
running an output which prints the necessary data from the different dictionaries inside an infinite loop. The processes
are also gracefully shut down in case of error and keyboard interrupt. 

In case of error, a recursion is implemented after the graceful shutdown. This is to restart all processes and avoid 
zombies eating up all resources. 

-----------------------------------------------------------------------------------------------

## Usage:

run this script within the previously created virtual environment with the following command:

<code>python3 algoTrade.py <MARKET_TICKER></code>

example: 

<code>python3 algoTrade.py BTC-USD</code>


-----------------------------------------------------------------------------------------------

## Addendum:

### what is missing? 

As previously mentioned this is not a complete trading-bot. This is because its never a good idea to give away 
working trading strategies by making them publicly available. So what would be needed to make it a complete trading-bot?

On the technical side there could be many approaches. Personally I have added following functionality:

### monitoring market and orders 

two monitoring systems:

one cosystem exists to monitor the given market conditions and screen them for certain patterns. 
As soon as the patterns are present, orders are opened.

the other monitors the open orders and adjusts or cancels them if necessary.
This is getting signals from the market monitoring system

### execution of orders:

there are 2 key functionalities when it comes to execution of orders, opening and cancelling. But to be trading succesfully an algorithm
needs to be a little more versatile on how to open or close orders. Key questions have been for me:

 - what type of order am I opening (Maker, Taker, Fill or Kill) in which situations?
 - how long should the order stay open?
 - what should the closing value be?
 - in which cases does the closing value needs to be altered? (trailing stop)
 - how should my stop loss strategy be?

All these functions need to be implemented in the execution part of the trading-bot.

 








