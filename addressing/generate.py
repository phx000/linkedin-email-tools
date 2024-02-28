from unidecode import unidecode


def combine(f, l):
    combinations = []
    for ff in f:
        for ll in l:
            combinations.append([ff, ll])
    return combinations


def generate_addresses(first, last, format_domain):
    first = first.split()[:2]
    last = last.split()[:2]
    format_, domain = format_domain.split("@")
    combinations = combine(first, last)
    out = set()

    for comb in combinations:
        user = format_
        f, l = comb
        user = user.replace("1", f)
        user = user.replace("2", l)
        user = user.replace("3", f[0])
        user = user.replace("4", l[0])
        out.add((unidecode(user), domain))

    return out
