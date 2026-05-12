# LOB Simulator

It is a limit order book simulator for exploring how market
microstructure changes as orders arrive, match, and cancel.

## What It Does

The simulator maintains a bid side and an ask side, then advances the market one
event at a time. Each event can place a limit order, send a market order, or
cancel resting liquidity. As the book evolves, the simulator tracks trades,
best bid and ask, spread, mid-price, aggregate bid/ask depth, etc.

There are two event modes:

- `decision`: state-dependent behavior that reacts to book conditions such as
  spread and depth imbalance.
- `stochastic`: random event flow for a simpler baseline simulation.

## How To Run

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 scripts/run_simulation.py --steps 200 --mode decision
```

You can also change the seed or use stochastic mode:

```bash
python3 scripts/run_simulation.py --steps 200 --mode stochastic --seed 11
```

## Example Output

```text
Simulation complete
mode: decision
steps: 10
limit_events: 8
market_events: 0
cancel_events: 2
trades_executed: 4
best_bid: 100
best_ask: 101
spread: 1
mid_price: 100.5
bid_depth: 50
ask_depth: 41
trade_count: 4
```

## Dashboard

Build an interactive HTML dashboard:

```bash
python3 scripts/build_dashboard.py --steps 80 --mode decision --output dashboard/simulation_dashboard.html
```

Then open:

```text
dashboard/simulation_dashboard.html
```

The dashboard lets you step through the simulation, play events over time, view
the mid-price path, inspect the current book, and see recent trades.

## Project Layout

```text
src/lob_simulator/
  order_book.py      Core order book and matching logic
  simulation.py      Simulation loop and result summaries
  behavior.py        Decision-based event behavior
  random_flow.py     Stochastic event generation
  types.py           Shared data types

scripts/
  run_simulation.py  CLI script for text output
  build_dashboard.py HTML dashboard generator

tests/
  test_order_book.py
  test_behavior.py
```

## Tests

```bash
pytest
```
