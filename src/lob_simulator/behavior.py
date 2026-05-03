from __future__ import annotations

import random
from dataclasses import dataclass

from .types import Event, Side


@dataclass(slots=True)
class BehaviorState:
    best_bid: int | None
    best_ask: int | None
    bid_depth: int
    ask_depth: int
    spread: int | None


@dataclass(slots=True)
class BehaviorConfig:
    reference_price: int = 100
    limit_order_probability: float = 0.55
    market_order_probability: float = 0.30
    min_quantity: int = 1
    max_quantity: int = 10
    min_price_offset: int = 1
    max_price_offset: int = 4


class StochasticBehavior:
    def __init__(self, seed: int, config: BehaviorConfig | None = None) -> None:
        self.rng = random.Random(seed)
        self.config = config or BehaviorConfig()

    def next_event(self, state: BehaviorState) -> Event:
        roll = self.rng.random()
        side = self._sample_side()
        quantity = self._sample_quantity()

        limit_cutoff = self.config.limit_order_probability
        market_cutoff = limit_cutoff + self.config.market_order_probability

        if roll < limit_cutoff:
            price = self._sample_limit_price(side, state.best_bid, state.best_ask)
            return Event(event_type="limit", side=side, quantity=quantity, price=price)
        if roll < market_cutoff:
            return Event(event_type="market", side=side, quantity=quantity)
        return Event(event_type="cancel", side=side, quantity=0)

    def _sample_side(self) -> Side:
        return "buy" if self.rng.random() < 0.5 else "sell"

    def _sample_quantity(self) -> int:
        return self.rng.randint(self.config.min_quantity, self.config.max_quantity)

    def _sample_limit_price(
        self,
        side: Side,
        best_bid: int | None,
        best_ask: int | None,
    ) -> int:
        center = self.config.reference_price
        if best_bid is not None and best_ask is not None:
            center = int((best_bid + best_ask) / 2)

        offset = self.rng.randint(self.config.min_price_offset, self.config.max_price_offset)
        if side == "buy":
            return center - offset
        return center + offset


@dataclass(slots=True)
class DecisionBehaviorConfig:
    reference_price: int = 100
    imbalance_threshold: float = 0.20
    market_order_bias_threshold: int = 3
    min_quantity: int = 1
    max_quantity: int = 8


class DecisionBehavior:
    def __init__(self, seed: int, config: DecisionBehaviorConfig | None = None) -> None:
        self.rng = random.Random(seed)
        self.config = config or DecisionBehaviorConfig()

    def next_event(self, state: BehaviorState) -> Event:
        if state.best_bid is None or state.best_ask is None or state.spread is None:
            return self._fallback_limit_order()

        imbalance = self._imbalance(state.bid_depth, state.ask_depth)
        dominant_side = self._dominant_side(imbalance)

        if state.spread >= self.config.market_order_bias_threshold:
            return self._quote_inside_book(state, dominant_side)

        if dominant_side is not None and abs(imbalance) >= self.config.imbalance_threshold:
            if self.rng.random() < 0.60:
                return Event(
                    event_type="market",
                    side=dominant_side,
                    quantity=self._sample_quantity(),
                )
            return self._quote_with_bias(state, dominant_side)

        if self.rng.random() < 0.20:
            cancel_side: Side = "buy" if state.bid_depth > state.ask_depth else "sell"
            return Event(event_type="cancel", side=cancel_side, quantity=0)

        return self._quote_inside_book(state, None)

    def _imbalance(self, bid_depth: int, ask_depth: int) -> float:
        total_depth = bid_depth + ask_depth
        if total_depth == 0:
            return 0.0
        return (bid_depth - ask_depth) / total_depth

    def _dominant_side(self, imbalance: float) -> Side | None:
        if imbalance >= self.config.imbalance_threshold:
            return "buy"
        if imbalance <= -self.config.imbalance_threshold:
            return "sell"
        return None

    def _quote_inside_book(self, state: BehaviorState, side: Side | None) -> Event:
        chosen_side = side or ("buy" if self.rng.random() < 0.5 else "sell")
        if chosen_side == "buy":
            price = max((state.best_bid or self.config.reference_price) + 1, 1)
            if state.best_ask is not None:
                price = min(price, state.best_ask)
        else:
            price = max((state.best_ask or self.config.reference_price) - 1, 1)
            if state.best_bid is not None:
                price = max(price, state.best_bid)
        return Event(event_type="limit", side=chosen_side, quantity=self._sample_quantity(), price=price)

    def _quote_with_bias(self, state: BehaviorState, side: Side) -> Event:
        if side == "buy":
            price = state.best_bid or self.config.reference_price
        else:
            price = state.best_ask or self.config.reference_price
        return Event(event_type="limit", side=side, quantity=self._sample_quantity(), price=price)

    def _fallback_limit_order(self) -> Event:
        side: Side = "buy" if self.rng.random() < 0.5 else "sell"
        anchor = self.config.reference_price
        price = anchor - 1 if side == "buy" else anchor + 1
        return Event(event_type="limit", side=side, quantity=self._sample_quantity(), price=price)

    def _sample_quantity(self) -> int:
        return self.rng.randint(self.config.min_quantity, self.config.max_quantity)
