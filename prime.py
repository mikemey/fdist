import locale

from math import sqrt

locale.setlocale(locale.LC_ALL, 'en_US')


def print_primes():
    curr = 3
    dividends = [2, 3]
    while True:
        curr += 1
        limit = sqrt(curr)
        found = True
        for div in dividends:
            over_half = div > limit
            if over_half:
                break

            mod = curr % div
            if mod == 0:
                found = False
                break
        if found:
            dividends.append(curr)
            div_count = len(dividends)
            if div_count % 1000 == 0:
                print locale.format("%40d", curr, grouping=True)


if __name__ == "__main__":
    print_primes()
