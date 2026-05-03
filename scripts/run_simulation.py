from __future__ import annotations

import argparse

from lob_simulator.simulation import MarketSimulation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LOB simulator.")
    parser.add_argument("--steps", type=int, default=200, help="Number of simulation steps.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")
    parser.add_argument(
        "--mode",
        choices=["stochastic", "decision"],
        default="decision",
        help="Behavior mode used to generate market events.",
    )
    args = parser.parse_args()

    simulation = MarketSimulation(seed=args.seed, steps=args.steps, mode=args.mode)
    result = simulation.run()

    print("Simulation complete")
    print(f"mode: {args.mode}")
    print(f"steps: {result.steps}")
    print(f"limit_events: {result.limit_events}")
    print(f"market_events: {result.market_events}")
    print(f"cancel_events: {result.cancel_events}")
    print(f"trades_executed: {result.trades_executed}")
    for key, value in result.final_snapshot.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
