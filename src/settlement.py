from typing import Dict, List


def compute_settlement(net_by_player: Dict[str, float], tol: float = 1e-6) -> List[Dict[str, float]]:
    """
    Compute minimal-ish settlement transfers from per-player net results.

    net_by_player: mapping of player -> net (positive = should receive, negative = should pay).
    Returns a list of dicts: {payer, payee, amount}
    """
    # Filter near-zero nets
    cleaned = {p: n for p, n in net_by_player.items() if abs(n) > tol}
    if not cleaned:
        return []

    total = sum(cleaned.values())
    if abs(total) > tol:
        raise ValueError(f"Nets do not sum to zero (imbalance {total:.4f}).")

    creditors = sorted([(p, n) for p, n in cleaned.items() if n > tol], key=lambda x: x[1], reverse=True)
    debtors = sorted([(p, -n) for p, n in cleaned.items() if n < -tol], key=lambda x: x[1], reverse=True)

    transfers: List[Dict[str, float]] = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, owe = debtors[i]
        creditor, receive = creditors[j]
        amt = min(owe, receive)
        transfers.append({"payer": debtor, "payee": creditor, "amount": round(amt, 2)})

        owe -= amt
        receive -= amt

        if owe <= tol:
            i += 1
        else:
            debtors[i] = (debtor, owe)
        if receive <= tol:
            j += 1
        else:
            creditors[j] = (creditor, receive)

    return transfers


def format_transfers_text(transfers: List[Dict[str, float]], currency_symbol: str = "£") -> str:
    """Format transfers as newline-separated text like 'Alice -> Bob: £12.50'."""
    lines = [f"{t['payer']} -> {t['payee']}: {currency_symbol}{t['amount']:.2f}" for t in transfers]
    return "\n".join(lines)
