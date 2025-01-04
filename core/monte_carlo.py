import random


def build_one_curve(trades, win_rate, wl_ratio, fraction):
    trades = int(trades)
    win_rate = clean_value(win_rate) / 100
    wl_ratio = clean_value(wl_ratio)
    fraction = clean_value(fraction) / 100

    print(trades, win_rate, wl_ratio, fraction)

    eq_curve = [1]
    for trade in range(1, trades+1):
        if random.random() < win_rate:  # WINNER
            eq_curve.append(eq_curve[trade - 1] * (1 + fraction * wl_ratio))
        else:
            eq_curve.append(eq_curve[trade - 1] * (1 - fraction))
    return eq_curve


def clean_value(raw_val):
    """
    Extract a clean float value.

    :return: float, or as is
    """

    if raw_val:
        return float(raw_val.replace(",", "."))
    else:
        return raw_val
