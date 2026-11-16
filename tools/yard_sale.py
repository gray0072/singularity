"""The game of matches of article 49 ("The Yard Sale, or Why Money Goes to Money"), played on a computer.

Standard library only; the seed is fixed, so every run gives the same games.

    python tools/yard_sale.py hand     # the game for two at the fire: 20 matches each, toss by toss
    python tools/yard_sale.py curve    # a thousand players, a thousand rounds: the series of the figure
    python tools/yard_sale.py long     # the same table left to play for 5,000 rounds
    python tools/yard_sale.py fixed    # the same table with a stake of one match, 40,000 rounds
    python tools/yard_sale.py levy     # the same table with a levy into a common pot

Rules. Two players toss a fair coin. In the yard-sale game the stake is a fifth of what the poorer of the two
has (at the fire: rounded down, at least one match). In the plain game the stake is always one match, and a
player with no matches loses nothing and can still win. A round is 500 games between pairs drawn at random
from the thousand players, so each player plays once a round on average. With a levy, after every round each
player puts the same small share of the heap into a pot, and the pot is divided equally.

The numbers of the figures `matches-go-to-one` and `a-brake-in-the-game` in tools/figures.py were copied from
the output of this script.
"""

import random
import sys

SEED = 49


def hand_game(seed=SEED, start=20):
    """Oleg and Andrey; heads means Oleg wins. Returns (toss, Oleg's matches, stake, 'H' or 'T') per toss."""
    rng = random.Random(seed)
    oleg, andrey = start, start
    history = []
    toss = 0
    while oleg > 0 and andrey > 0:
        toss += 1
        stake = max(1, min(oleg, andrey) // 5)
        heads = rng.random() < 0.5
        oleg += stake if heads else -stake
        andrey -= stake if heads else -stake
        history.append((toss, oleg, stake, "H" if heads else "T"))
    return history


def shares(heaps):
    """Shares of the richest hundredth, the richest tenth and the poorer half; the median heap."""
    s = sorted(heaps, reverse=True)
    n, total = len(s), sum(s)
    return dict(top1=sum(s[:n // 100]) / total, top10=sum(s[:n // 10]) / total,
                bottom50=sum(s[n // 2:]) / total, median=(s[n // 2] + s[n // 2 - 1]) / 2,
                richest=s[0] / total)


def table(rounds, marks, mode="share", levy=0.0, n=1000, start=100.0, fraction=0.2, seed=SEED):
    """Play `rounds` rounds and return {round: shares} for the rounds listed in `marks`."""
    rng = random.Random(seed)
    heaps = [start] * n
    marks = set(marks)
    out = {0: shares(heaps)} if 0 in marks else {}
    for r in range(1, rounds + 1):
        for _ in range(n // 2):
            i = rng.randrange(n)
            j = rng.randrange(n - 1)
            if j >= i:
                j += 1
            stake = fraction * min(heaps[i], heaps[j]) if mode == "share" else 1.0
            if rng.random() < 0.5:
                i, j = j, i
            if mode == "fixed" and heaps[j] < 1.0:
                continue  # the loser has nothing to lose
            heaps[i] += stake
            heaps[j] -= stake
        if levy:
            pot = sum(heaps) * levy
            heaps = [h * (1 - levy) + pot / n for h in heaps]
        if r in marks:
            out[r] = shares(heaps)
    return out


def show(result):
    for r in sorted(result):
        print(r, " ".join(f"{k}={v:.4f}" for k, v in result[r].items()))


def main(what):
    if what == "hand":
        history = hand_game()
        heads = sum(1 for h in history if h[3] == "H")
        print(f"tosses: {len(history)}; heads (Oleg wins): {heads}; tails: {len(history) - heads}")
        print(" ".join(f"{t}:{o}" for t, o, _, _ in history))
    elif what == "curve":
        marks = [0, 10, 20, 30, 50, 75] + list(range(100, 1001, 50))
        print("# stake: a fifth of the poorer heap")
        show(table(1000, marks))
        print("# stake: one match")
        show(table(1000, marks, mode="fixed"))
    elif what == "long":
        show(table(5000, [1000, 2000, 3000, 5000]))
    elif what == "fixed":
        show(table(40000, [1000, 5000, 10000, 20000, 40000], mode="fixed"))
    elif what == "levy":
        for levy in (0.0005, 0.001, 0.005, 0.01):
            print(f"# levy {levy}")
            show(table(6000, [3000, 4000, 5000, 6000], levy=levy))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
