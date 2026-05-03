from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Side = Literal["buy", "sell"]
EventType = Literal["limit", "market", "cancel"]


@dataclass(slots=True)
class Order:
    order_id: int
    side: Side
    price: int
    quantity: int
    timestamp: int


@dataclass(slots=True)
class Trade:
    buy_order_id: int | None
    sell_order_id: int | None
    price: int
    quantity: int
    timestamp: int


@dataclass(slots=True)
class Event:
    event_type: EventType
    side: Side
    quantity: int
    price: int | None = None

