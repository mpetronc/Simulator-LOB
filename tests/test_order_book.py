from lob_simulator.order_book import OrderBook


def test_crossing_limit_order_executes_trade() -> None:
    book = OrderBook()
    book.submit_limit_order("sell", 101, 5)
    book.submit_limit_order("buy", 101, 3)

    assert len(book.trades) == 1
    assert book.trades[0].quantity == 3
    assert book.best_ask() == 101


def test_market_buy_consumes_best_ask() -> None:
    book = OrderBook()
    book.submit_limit_order("sell", 101, 5)
    book.submit_limit_order("sell", 102, 5)
    book.submit_market_order("buy", 6)

    assert len(book.trades) == 2
    assert book.best_ask() == 102
