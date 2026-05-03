# LOB Simulator Decision

The simulator is a first-principles project that models how a limit order book evolves through limit orders, market orders, and cancellations. This version extends the baseline engine with a separate decision-making behavior layer that can react to book state instead of relying only on stochastic event generation.

## Purpose

The goal of this project is to build intuition for how a market changes as orders interact with the book, while also introducing simple state-dependent behavior rules.

## Current Features

The current version includes a bid and ask side order book representation, support for limit orders, market orders, and cancellations, matching logic for incoming orders, a dedicated behavior layer, a decision-based event mode, a stochastic fallback mode, a basic simulation runner, end-of-run summary metrics, and starter tests for core execution behavior.

## How It Works

The simulator maintains a limit order book with resting buy and sell orders. At each step, the behavior layer generates a new event. In decision mode, the event choice depends on the current state of the book, such as spread and depth imbalance. This event may add a limit order, execute a market order against the best available liquidity, or cancel an existing order. As events are processed, the state of the book changes, which affects the spread, mid-price, book depth, and trade history.

## Running the Project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 scripts/run_simulation.py --steps 200 --mode decision
```
