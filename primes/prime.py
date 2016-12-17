import locale
import time
from math import sqrt

locale.setlocale(locale.LC_ALL, 'en_US')


def print_primes():
    start_time = ticker = time.time()
    current_prime = 3
    all_primes = [2, 3]
    while True:
        current_prime += 1
        limit = sqrt(current_prime)
        found = True
        for div in all_primes:
            over_limit = div > limit
            if over_limit:
                break

            mod = current_prime % div
            if mod == 0:
                found = False
                break
        if found:
            all_primes.append(current_prime)
            if time.time() - ticker > 10:
                ticker = time.time()
                log_progress(ticker - start_time, len(all_primes), current_prime)


def log_progress(elapsed, count, current):
    minutes, seconds = divmod(elapsed, 60)
    hours, minutes = divmod(minutes, 60)
    print \
        "%4d:%02d:%02d" % (hours, minutes, seconds), \
        "|", \
        locale.format("%20d", count, grouping=True), \
        "|", \
        locale.format("%30d", current, grouping=True)


if __name__ == "__main__":
    print_primes()
