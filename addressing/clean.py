import unicodedata as ud
from unidecode import unidecode
from addressing import words_to_remove

latin_letters = {}


def remove_non_latin(f, l):
    def is_latin(uchr):
        try:
            return latin_letters[uchr]
        except KeyError:
            return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

    def only_roman_chars(unistr):
        return all(is_latin(uchr) for uchr in unistr if uchr.isalpha())

    if only_roman_chars(f) and only_roman_chars(l):
        return f, l
    return


def remove_non_alfa(f, l):
    f = ''.join([char if char.isalpha() else ' ' for char in f])
    l = ''.join([char if char.isalpha() else ' ' for char in l])
    return f, l


def remove_specifics(f, l, specifics):
    ff = f.split()
    ll = l.split()
    ff = [el for el in ff if unidecode(el) not in specifics]
    ll = [el for el in ll if unidecode(el) not in specifics]
    return ff, ll


def filter_by_len(fff, lll):
    def filter_by_word_len(ff, ll):
        min_, max_ = 3, 50
        ff = [el for el in ff if min_ <= len(el) <= max_]
        ll = [el for el in ll if min_ <= len(el) <= max_]
        return ff, ll

    def filter_by_word_number(ff, ll):
        d = 2
        ff = ff[:d]
        ll = ll[:d]
        return " ".join(ff), " ".join(ll)

    def filter_by_cell_len(f, l):
        min_, max_ = 3, 50
        if (min_ <= len(f) <= max_) and (min_ <= len(l) <= max_):
            return f, l
        return

    fff, lll = filter_by_word_len(fff, lll)
    f, l = filter_by_word_number(fff, lll)
    return filter_by_cell_len(f, l)


def clean_first_and_last_name(f, l):
    f = f.lower()
    l = l.lower()

    res = remove_non_latin(f, l)
    if res is None:
        return

    f, l = res
    f, l = remove_non_alfa(f, l)
    ff, ll = remove_specifics(f, l, words_to_remove.words)
    return filter_by_len(ff, ll)


def clean_first_name(f):
    f = f.lower()
    f, l = remove_non_latin(f, "a")
    f, l = remove_non_alfa(f, l)
    ff, ll = remove_specifics(f, l, words_to_remove.words)
    return " ".join(ff)
