import pprint


def print_primes():
    curr = 3
    dividends = [2, 3]
    while True:
        curr += 1
        limit = curr / 2
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
            if len(dividends) % 100 == 0:
                pprint.pprint(curr)
            dividends.append(curr)


if __name__ == "__main__":
    print_primes()
