import pytest

from src import settlement


def test_two_player_settlement():
    nets = {"Alice": 10, "Bob": -10}
    transfers = settlement.compute_settlement(nets)
    assert transfers == [{"payer": "Bob", "payee": "Alice", "amount": 10.0}]


def test_multi_player_settlement():
    nets = {"A": 12, "B": 8, "C": -10, "D": -10}
    transfers = settlement.compute_settlement(nets)
    # deterministic: biggest debtor to biggest creditor first
    assert transfers[0] == {"payer": "C", "payee": "A", "amount": 10.0}
    assert transfers[1] == {"payer": "D", "payee": "A", "amount": 2.0}
    assert transfers[2] == {"payer": "D", "payee": "B", "amount": 8.0}
    assert round(sum(t["amount"] for t in transfers), 2) == 20.0


def test_imbalance_raises():
    nets = {"A": 5, "B": -4}
    with pytest.raises(ValueError):
        settlement.compute_settlement(nets)