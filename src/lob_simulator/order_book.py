from __future__ import annotations

from collections import defaultdict, deque

from .types import Order, Side, Trade


class OrderBook:
    def __init__(self) -> None:
        self.bids: dict[int, deque[Order]] = defaultdict(deque)
        self.asks: dict[int, deque[Order]] = defaultdict(deque)
        self.order_lookup: dict[int, tuple[Side, int]] = {}
        self.next_order_id = 1
        self.timestamp = 0
        self.trades: list[Trade] = []

    def submit_limit_order(self, side: Side, price: int, quantity: int) -> int:
        self.timestamp += 1
        order = Order(
            order_id=self.next_order_id,
            side=side,
            price=price,
            quantity=quantity,
            timestamp=self.timestamp,
        )
        self.next_order_id += 1
        self._match_incoming(order)
        if order.quantity > 0:
            self._store_order(order)
        return order.order_id

    def submit_market_order(self, side: Side, quantity: int) -> None:
        self.timestamp += 1
        book_side = self.asks if side == "buy" else self.bids
        resting_side = "sell" if side == "buy" else "buy"
        remaining = quantity

        while remaining > 0 and book_side:
            best_price = min(book_side) if side == "buy" else max(book_side)
            queue = book_side[best_price]
            while queue and remaining > 0:
                resting = queue[0]
                matched = min(remaining, resting.quantity)
                remaining -= matched
                resting.quantity -= matched
                trade = Trade(
                    buy_order_id=None if side == "buy" else resting.order_id,
                    sell_order_id=resting.order_id if side == "buy" else None,
                    price=best_price,
                    quantity=matched,
                    timestamp=self.timestamp,
                )
                self.trades.append(trade)
                if resting.quantity == 0:
                    queue.popleft()
                    self.order_lookup.pop(resting.order_id, None)
            if not queue:
                del book_side[best_price]

    def cancel_random_order(self, side: Side) -> bool:
        side_book = self.bids if side == "buy" else self.asks
        if not side_book:
            return False
        target_price = max(side_book) if side == "buy" else min(side_book)
        queue = side_book[target_price]
        if not queue:
            return False
        order = queue.pop()
        self.order_lookup.pop(order.order_id, None)
        if not queue:
            del side_book[target_price]
        return True

    def best_bid(self) -> int | None:
        return max(self.bids) if self.bids else None

    def best_ask(self) -> int | None:
        return min(self.asks) if self.asks else None

    def spread(self) -> int | None:
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is None or ask is None:
            return None
        return ask - bid

    def mid_price(self) -> float | None:
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is None or ask is None:
            return None
        return (bid + ask) / 2.0

    def total_depth(self, side: Side) -> int:
        book = self.bids if side == "buy" else self.asks
        return sum(order.quantity for queue in book.values() for order in queue)

    def snapshot(self) -> dict[str, float | int | None]:
        return {
            "best_bid": self.best_bid(),
            "best_ask": self.best_ask(),
            "spread": self.spread(),
            "mid_price": self.mid_price(),
            "bid_depth": self.total_depth("buy"),
            "ask_depth": self.total_depth("sell"),
            "trade_count": len(self.trades),
        }

    def _match_incoming(self, incoming: Order) -> None:
        opposite_book = self.asks if incoming.side == "buy" else self.bids
        should_cross = (
            lambda best_price: incoming.price >= best_price
            if incoming.side == "buy"
            else incoming.price <= best_price
        )

        while incoming.quantity > 0 and opposite_book:
            best_price = min(opposite_book) if incoming.side == "buy" else max(opposite_book)
            if not should_cross(best_price):
                break

            queue = opposite_book[best_price]
            while queue and incoming.quantity > 0:
                resting = queue[0]
                matched = min(incoming.quantity, resting.quantity)
                incoming.quantity -= matched
                resting.quantity -= matched
                trade = Trade(
                    buy_order_id=incoming.order_id if incoming.side == "buy" else resting.order_id,
                    sell_order_id=resting.order_id if incoming.side == "buy" else incoming.order_id,
                    price=best_price,
                    quantity=matched,
                    timestamp=self.timestamp,
                )
                self.trades.append(trade)
                if resting.quantity == 0:
                    queue.popleft()
                    self.order_lookup.pop(resting.order_id, None)
            if not queue:
                del opposite_book[best_price]

    def _store_order(self, order: Order) -> None:
        book = self.bids if order.side == "buy" else self.asks
        book[order.price].append(order)
        self.order_lookup[order.order_id] = (order.side, order.price)

