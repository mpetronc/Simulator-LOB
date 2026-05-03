from __future__ import annotations

from .behavior import BehaviorConfig, BehaviorState, StochasticBehavior
from .types import Event


class RandomOrderFlow:
    def __init__(self, seed: int, reference_price: int = 100) -> None:
        config = BehaviorConfig(reference_price=reference_price)
        self.behavior = StochasticBehavior(seed=seed, config=config)

    def next_event(self, best_bid: int | None, best_ask: int | None) -> Event:
        state = BehaviorState(
            best_bid=best_bid,
            best_ask=best_ask,
            bid_depth=0,
            ask_depth=0,
            spread=None if best_bid is None or best_ask is None else best_ask - best_bid,
        )
        return self.behavior.next_event(state)
