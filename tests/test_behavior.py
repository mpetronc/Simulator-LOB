from lob_simulator.behavior import BehaviorState, DecisionBehavior


def test_decision_behavior_prefers_buy_pressure_when_bid_depth_dominates() -> None:
    behavior = DecisionBehavior(seed=7)
    state = BehaviorState(
        best_bid=99,
        best_ask=101,
        bid_depth=120,
        ask_depth=40,
        spread=2,
    )

    event = behavior.next_event(state)

    assert event.side == "buy"
    assert event.event_type in {"limit", "market"}
