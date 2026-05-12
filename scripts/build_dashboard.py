from __future__ import annotations

import argparse
import json
from pathlib import Path

from lob_simulator.simulation import MarketSimulation


def build_html(payload: dict[str, object]) -> str:
    data = json.dumps(payload)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>LOB Simulator Dashboard</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #020305;
        --panel: #0b0d11;
        --panel-2: #11151b;
        --line: rgba(255, 255, 255, 0.08);
        --ink: #f4f7fb;
        --muted: #7f8b9d;
        --accent: #53c7ff;
        --bid: #3ddc97;
        --ask: #ff7a7a;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, system-ui, sans-serif;
        background: #000;
        color: var(--ink);
        min-height: 100vh;
      }}
      .page {{
        min-height: 100vh;
        display: grid;
        grid-template-rows: auto 1fr auto;
      }}
      .controls {{
        position: sticky;
        top: 0;
        z-index: 10;
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 14px 18px;
        background: rgba(2, 3, 5, 0.92);
        border-bottom: 1px solid var(--line);
        backdrop-filter: blur(10px);
      }}
      button {{
        border: 1px solid var(--line);
        background: var(--panel);
        color: var(--ink);
        border-radius: 999px;
        padding: 9px 14px;
        cursor: pointer;
      }}
      .menu-toggle {{
        margin-left: auto;
      }}
      input[type="range"] {{
        flex: 1;
      }}
      .viewport {{
        position: relative;
        display: grid;
        place-items: center;
        padding: 24px;
      }}
      .chart-shell {{
        width: min(1400px, calc(100vw - 48px));
        height: min(76vh, 860px);
        background:
          linear-gradient(180deg, rgba(255,255,255,0.015), transparent 25%),
          linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
          linear-gradient(180deg, rgba(255,255,255,0.03) 1px, transparent 1px),
          #000;
        background-size: auto, 72px 72px, 72px 72px, auto;
        overflow: hidden;
      }}
      .chart-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 18px 6px;
        color: var(--muted);
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
      }}
      .chart-metrics {{
        display: flex;
        gap: 18px;
        flex-wrap: wrap;
      }}
      .metric strong {{
        display: block;
        margin-top: 6px;
        color: var(--ink);
        font-size: 1.28rem;
        letter-spacing: normal;
        text-transform: none;
      }}
      svg {{
        width: 100%;
        height: calc(100% - 74px);
        display: block;
      }}
      .drawer {{
        position: fixed;
        top: 0;
        right: 0;
        width: min(380px, 92vw);
        height: 100vh;
        background: rgba(10, 12, 16, 0.98);
        border-left: 1px solid var(--line);
        transform: translateX(100%);
        transition: transform 220ms ease;
        z-index: 20;
        padding: 20px 18px 24px;
        overflow-y: auto;
      }}
      .drawer.is-open {{
        transform: translateX(0);
      }}
      .drawer-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
      }}
      .drawer h2 {{
        margin: 0;
        font-size: 1rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
      }}
      th, td {{
        padding: 8px 6px;
        text-align: left;
        border-bottom: 1px solid var(--line);
      }}
      th {{
        color: var(--muted);
        font-size: 0.8rem;
        text-transform: uppercase;
      }}
      .bid th {{ color: var(--bid); }}
      .ask th {{ color: var(--ask); }}
      .trade-list {{
        display: grid;
        gap: 10px;
        margin-top: 12px;
      }}
      .trade-item {{
        padding: 10px 12px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.02);
      }}
      .block {{
        margin-top: 20px;
      }}
      .block:first-of-type {{
        margin-top: 0;
      }}
      .event-line {{
        display: flex;
        justify-content: space-between;
        gap: 14px;
        padding: 10px 0;
        border-top: 1px solid var(--line);
      }}
      .event-line:first-of-type {{
        border-top: 0;
        padding-top: 0;
      }}
      .label {{
        color: var(--muted);
      }}
      @media (max-width: 900px) {{
        .chart-shell {{
          width: calc(100vw - 24px);
          height: 68vh;
        }}
        .controls {{
          flex-wrap: wrap;
        }}
        .menu-toggle {{
          margin-left: 0;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="page">
      <div class="controls">
        <button id="prev">Prev</button>
        <button id="play">Play</button>
        <button id="next">Next</button>
        <input id="slider" type="range" min="1" max="{payload["steps"]}" value="1" />
        <span id="step-label">Step 1 / {payload["steps"]}</span>
        <button id="menu-toggle" class="menu-toggle">Statistics</button>
      </div>
      <div class="viewport">
        <div class="chart-shell">
          <div class="chart-head">
            <span>LOB Simulator</span>
            <div class="chart-metrics">
              <div class="metric"><span>Mode</span><strong id="mode-value">{payload["mode"]}</strong></div>
              <div class="metric"><span>Mid Price</span><strong id="mid-value">-</strong></div>
              <div class="metric"><span>Spread</span><strong id="spread-value">-</strong></div>
              <div class="metric"><span>Trades</span><strong id="trade-count-value">0</strong></div>
            </div>
          </div>
          <svg id="chart" viewBox="0 0 1400 820" preserveAspectRatio="none"></svg>
        </div>
      </div>
      <aside class="drawer" id="drawer">
        <div class="drawer-head">
          <h2>Statistics</h2>
          <button id="close-drawer">Close</button>
        </div>
        <div class="block" id="event"></div>
        <div class="block">
          <h2>Order Book</h2>
          <table class="bid">
            <thead><tr><th>Bid</th><th>Qty</th><th>Orders</th></tr></thead>
            <tbody id="bids"></tbody>
          </table>
          <table class="ask">
            <thead><tr><th>Ask</th><th>Qty</th><th>Orders</th></tr></thead>
            <tbody id="asks"></tbody>
          </table>
        </div>
        <div class="block">
          <h2>Recent Trades</h2>
          <div class="trade-list" id="trades"></div>
        </div>
      </aside>
    </div>
    <script>
      const data = {data};
      const history = data.history;
      const eventEl = document.getElementById("event");
      const bidsEl = document.getElementById("bids");
      const asksEl = document.getElementById("asks");
      const tradesEl = document.getElementById("trades");
      const slider = document.getElementById("slider");
      const stepLabel = document.getElementById("step-label");
      const chart = document.getElementById("chart");
      const prevButton = document.getElementById("prev");
      const nextButton = document.getElementById("next");
      const playButton = document.getElementById("play");
      const menuToggle = document.getElementById("menu-toggle");
      const closeDrawer = document.getElementById("close-drawer");
      const drawer = document.getElementById("drawer");
      const midValue = document.getElementById("mid-value");
      const spreadValue = document.getElementById("spread-value");
      const tradeCountValue = document.getElementById("trade-count-value");
      let currentStep = 1;
      let timer = null;

      function renderBookRows(rows, priceKey) {{
        if (!rows.length) {{
          return `<tr><td colspan="3">No levels</td></tr>`;
        }}
        return rows.map((row) => `<tr><td>${{row.price}}</td><td>${{row.quantity}}</td><td>${{row.orders}}</td></tr>`).join("");
      }}

      function renderTrades(trades) {{
        if (!trades.length) {{
          return `<div class="trade-item">No trade on this step</div>`;
        }}
        return trades.map((trade) => `
          <div class="trade-item">
            <div><span class="label">Price:</span> ${{trade.price}}</div>
            <div><span class="label">Quantity:</span> ${{trade.quantity}}</div>
            <div><span class="label">Timestamp:</span> ${{trade.timestamp}}</div>
          </div>
        `).join("");
      }}

      function renderChart(step) {{
        const visible = history.slice(0, step).map((item) => item.snapshot.mid_price).filter((v) => v !== null);
        if (!visible.length) {{
          chart.innerHTML = "";
          return;
        }}
        const min = Math.min(...visible);
        const max = Math.max(...visible);
        const range = Math.max(max - min, 1);
        const points = visible.map((value, index) => {{
          const x = 36 + (index / Math.max(visible.length - 1, 1)) * 1328;
          const y = 720 - ((value - min) / range) * 580;
          return `${{x}},${{y}}`;
        }}).join(" ");
        const guides = Array.from({{ length: 7 }}, (_, index) => {{
          const y = 90 + index * 104;
          return `<line x1="0" y1="${{y}}" x2="1400" y2="${{y}}" stroke="rgba(255,255,255,0.06)" stroke-width="1" />`;
        }}).join("");
        chart.innerHTML = `
          <rect x="0" y="0" width="1400" height="820" fill="transparent"></rect>
          ${{guides}}
          <polyline fill="none" stroke="rgba(83,199,255,0.18)" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" points="${{points}}" />
          <polyline fill="none" stroke="#53c7ff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" points="${{points}}" />
        `;
      }}

      function render(step) {{
        const item = history[step - 1];
        currentStep = step;
        slider.value = step;
        stepLabel.textContent = `Step ${{step}} / ${{data.steps}}`;
        midValue.textContent = item.snapshot.mid_price ?? "-";
        spreadValue.textContent = item.snapshot.spread ?? "-";
        tradeCountValue.textContent = item.total_trades;
        eventEl.innerHTML = `
          <div class="event-line"><span class="label">Event</span><strong>${{item.event.event_type}}</strong></div>
          <div class="event-line"><span class="label">Side</span><strong>${{item.event.side}}</strong></div>
          <div class="event-line"><span class="label">Quantity</span><strong>${{item.event.quantity}}</strong></div>
          <div class="event-line"><span class="label">Price</span><strong>${{item.event.price ?? "market/cancel"}}</strong></div>
          <div class="event-line"><span class="label">Best Bid / Ask</span><strong>${{item.snapshot.best_bid ?? "-"}} / ${{item.snapshot.best_ask ?? "-"}}</strong></div>
          <div class="event-line"><span class="label">Mid Price</span><strong>${{item.snapshot.mid_price ?? "-"}}</strong></div>
          <div class="event-line"><span class="label">Spread</span><strong>${{item.snapshot.spread ?? "-"}}</strong></div>
        `;
        bidsEl.innerHTML = renderBookRows(item.bids);
        asksEl.innerHTML = renderBookRows(item.asks);
        tradesEl.innerHTML = renderTrades(item.new_trades);
        renderChart(step);
      }}

      prevButton.addEventListener("click", () => render(Math.max(1, currentStep - 1)));
      nextButton.addEventListener("click", () => render(Math.min(data.steps, currentStep + 1)));
      slider.addEventListener("input", (event) => render(Number(event.target.value)));
      menuToggle.addEventListener("click", () => drawer.classList.add("is-open"));
      closeDrawer.addEventListener("click", () => drawer.classList.remove("is-open"));
      playButton.addEventListener("click", () => {{
        if (timer) {{
          clearInterval(timer);
          timer = null;
          playButton.textContent = "Play";
          return;
        }}
        playButton.textContent = "Pause";
        timer = setInterval(() => {{
          if (currentStep >= data.steps) {{
            clearInterval(timer);
            timer = null;
            playButton.textContent = "Play";
            return;
          }}
          render(currentStep + 1);
        }}, 700);
      }});

      render(1);
    </script>
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an HTML dashboard for the LOB simulator.")
    parser.add_argument("--steps", type=int, default=80, help="Number of simulation steps.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")
    parser.add_argument(
        "--mode",
        choices=["stochastic", "decision"],
        default="decision",
        help="Simulation mode to visualize.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dashboard/simulation_dashboard.html"),
        help="Output HTML file.",
    )
    args = parser.parse_args()

    simulation = MarketSimulation(seed=args.seed, steps=args.steps, mode=args.mode)
    result = simulation.run()

    payload = {
        "mode": args.mode,
        "seed": args.seed,
        "steps": result.steps,
        "limit_events": result.limit_events,
        "market_events": result.market_events,
        "cancel_events": result.cancel_events,
        "trades_executed": result.trades_executed,
        "final_snapshot": result.final_snapshot,
        "history": result.history,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(payload), encoding="utf-8")
    print(f"Dashboard written to {args.output}")


if __name__ == "__main__":
    main()
