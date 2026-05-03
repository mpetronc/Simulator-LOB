from __future__ import annotations

from dataclasses import dataclass

from .behavior import BehaviorState, DecisionBehavior, StochasticBehavior
from .order_book import OrderBook


@dataclass(slots=True)
class SimulationResult:
    steps: int
    final_snapshot: dict[str, float | int | None]
    trades_executed: int
    cancel_events: int
    market_events: int
    limit_events: int


class MarketSimulation:
    def __init__(self, seed: int, steps: int, mode: str = "stochastic") -> None:
        self.steps = steps
        self.order_book = OrderBook()
        self.mode = mode
        if mode == "decision":
            self.behavior = DecisionBehavior(seed=seed)
        else:
            self.behavior = StochasticBehavior(seed=seed)
        self.limit_events = 0
        self.market_events = 0
        self.cancel_events = 0

        self._seed_book()

    def run(self) -> SimulationResult:
        for _ in range(self.steps):
            event = self.behavior.next_event(self._current_state())
            if event.event_type == "limit":
                self.limit_events += 1
                assert event.price is not None
                self.order_book.submit_limit_order(event.side, event.price, event.quantity)
            elif event.event_type == "market":
                self.market_events += 1
                self.order_book.submit_market_order(event.side, event.quantity)
            else:
                self.cancel_events += 1
                self.order_book.cancel_random_order(event.side)

        return SimulationResult(
            steps=self.steps,
            final_snapshot=self.order_book.snapshot(),
            trades_executed=len(self.order_book.trades),
            cancel_events=self.cancel_events,
            market_events=self.market_events,
            limit_events=self.limit_events,
        )

    def _seed_book(self) -> None:
        for price, quantity in [(99, 12), (98, 15), (97, 20)]:
            self.order_book.submit_limit_order("buy", price, quantity)
        for price, quantity in [(101, 12), (102, 15), (103, 20)]:
            self.order_book.submit_limit_order("sell", price, quantity)

    def _current_state(self) -> BehaviorState:
        return BehaviorState(
            best_bid=self.order_book.best_bid(),
            best_ask=self.order_book.best_ask(),
            bid_depth=self.order_book.total_depth("buy"),
            ask_depth=self.order_book.total_depth("sell"),
            spread=self.order_book.spread(),
        )
