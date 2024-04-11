# -*- coding: utf-8 -*-
"""Most_current_fruits.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gMaH4-yRKR6N9-HpeGa2nyF7FjSQOhb-
"""

# -*- coding: utf-8 -*-
"""(MOST CURRENT) Starfruit10.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K5uIIZ5LEBhFDVw8uMCxlxYLhWYKibyj
"""

# -*- coding: utf-8 -*-
"""starfruit.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rVY8GVc7R6sIqSwkAduDjGBT4gS6925z
"""

from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import pandas as pd

class Trader:
    starfruit_cache = []
    last_value = 0
    counter = 0
    cache_len = 8 #1 more than coef
    n = 5

    def calc_next_price_starfruit(self):

            intercept = .004
            coef = [-0.02640914, -0.07974619, -0.1503525 , -0.24380195, -0.35047668, -0.49547579, -0.70531434]
            diffs = pd.Series(self.starfruit_cache).diff(1)[1:]
            nxt_price = self.starfruit_cache[-1] + intercept

            for i, val in enumerate(diffs):
                diff =  val * coef[i]
                nxt_price += diff
            print("NEXT FAIR PRICE", nxt_price)
            return nxt_price

    def calc_next_n_price_starfruit(self, n):
        comp_cache = self.starfruit_cache.copy()
        intercept = .004
        coef = [-0.1405056 , -0.2815278 , -0.45272052, -0.68468281]
        projection = []
        for i in range(n):
            diffs = pd.Series(comp_cache).diff(1)[1:]
            nxt_price = comp_cache[-1] + intercept
            i = 0
            for val in (diffs[-4:]):
                diff =  val * coef[i]
                i += 1
                nxt_price += diff
            comp_cache.append(nxt_price)
            projection.append(nxt_price)
        # print("comp_cache", comp_cache)
        # print("PROJECTION", projection)

        return projection



    def run(self, state: TradingState):

        self.counter += 1
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        for product in state.order_depths:
          if product == 'STARFRUIT':
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            position: int = state.position.get(product, 0)
            max_buy = 20 - position
            max_sell = -20 - position
            starfruit_lb, starfruit_ub = 0,0
            pricevol = 0
            vol = 0
            print("POSITION", position)

#             if len(order_depth.sell_orders) != 0:
#                 best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]

#             if len(order_depth.buy_orders) != 0:
#                 best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]

            sells = list(order_depth.sell_orders.items())
            print('BUYS AFTER HERE')
            buys = list(order_depth.buy_orders.items())
            print(sells)
            print(buys)
            cutoff = 10
            if buys[0][1] >=cutoff or len(buys) == 1:
                best_bid = buys[0][0]
            elif buys[1][1] + buys[0][1] >= cutoff or len(buys) == 2:
                best_bid = buys[1][0]
            else:
                best_bid = buys[2][0]
            if sells[0][1] >= cutoff or len(sells) == 1:
                best_ask = sells[0][0]
            elif sells[1][1] + sells[0][1] >= cutoff or len(sells) == 2:
                best_ask = sells[1][0]
            else:
                best_ask = sells[2][0]




            mid_price = (best_ask + best_bid)/2
            self.starfruit_cache.append(mid_price)
            print("NEW MID PRICE", mid_price)
            self.last_value = mid_price


            starfruit_fair = 0

            if len(self.starfruit_cache) == self.cache_len:
                starfruit_fair = self.calc_next_price_starfruit()
                projections = self.calc_next_n_price_starfruit(self.n)
                self.starfruit_cache.pop(0)

            if self.counter >= 5:
                if len(order_depth.sell_orders) != 0:
                    for ask, amount in list(order_depth.sell_orders.items()):
                        if int(ask) < starfruit_fair - 1:
                            buy_volume = max(min(-amount, max_buy), 0)
                            print("BUY", str(-buy_volume) + "x", ask)
                            orders.append(Order(product, ask, buy_volume))
                            max_buy = max_buy - buy_volume
                            position = position + buy_volume
                        elif int(ask) <= starfruit_fair and position < 0:
                            buy_volume = max(min(-amount, -position), 0)
                            print("BUY", str(-buy_volume) + "x", ask)
                            orders.append(Order(product, ask, buy_volume))
                            max_buy = max_buy - buy_volume
                            position = position + buy_volume

                if len(order_depth.buy_orders) != 0:
                    for bid, amount in list(order_depth.buy_orders.items()):
                        if int(bid) > starfruit_fair + 1:
                            sell_volume = min(max(-amount, max_sell), 0)
                            print("SELL", str(sell_volume) + "x", bid)
                            orders.append(Order(product, bid, sell_volume))
                            max_sell = max_sell - sell_volume
                            position = position + sell_volume
                        elif int(bid) >= starfruit_fair and position > 0:
                            sell_volume = min(max(-amount, -position), 0)
                            print("SELL", str(sell_volume) + "x", bid)
                            orders.append(Order(product, bid, sell_volume))
                            max_sell = max_sell - sell_volume
                            position = position + sell_volume

            if len(order_depth.sell_orders) != 0:
              sell_threshold = list(order_depth.sell_orders.items())[-1][0]
              orders.append(Order(product, sell_threshold - 1, max_sell))
            if len(order_depth.buy_orders) != 0:
              buy_threshold = list(order_depth.buy_orders.items())[-1][0]
              orders.append(Order(product, buy_threshold + 1, max_buy))


            result[product] = orders

		    # String value holding Trader state data required.
				# It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"

				# Sample conversion request. Check more details below.
        conversions = 0

        return result, conversions, traderData