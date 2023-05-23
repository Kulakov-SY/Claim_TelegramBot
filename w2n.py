tokens_config = {
    'ноль': {'num': 0, 'type': 'self', 'level': 1},
    'один': {'num': 1, 'type': 'final', 'level': 1},
    'одна': {'num': 1, 'type': 'final', 'level': 1},
    'два': {'num': 2, 'type': 'final', 'level': 1},
    'две': {'num': 2, 'type': 'final', 'level': 1},
    'три': {'num': 3, 'type': 'final', 'level': 1},
    'четыре': {'num': 4, 'type': 'final', 'level': 1},
    'пять': {'num': 5, 'type': 'final', 'level': 1},
    'шесть': {'num': 6, 'type': 'final', 'level': 1},
    'семь': {'num': 7, 'type': 'final', 'level': 1},
    'восемь': {'num': 8, 'type': 'final', 'level': 1},
    'девять': {'num': 9, 'type': 'final', 'level': 1},
    "десять": {'num': 10, 'type': 'final', 'level': 1},
    "одиннадцать": {'num': 11, 'type': 'final', 'level': 1},
    "двенадцать": {'num': 12, 'type': 'final', 'level': 1},
    "тринадцать": {'num': 13, 'type': 'final', 'level': 1},
    "четырнадцать": {'num': 14, 'type': 'final', 'level': 1},
    "пятнадцать": {'num': 15, 'type': 'final', 'level': 1},
    "шестнадцать": {'num': 16, 'type': 'final', 'level': 1},
    "семнадцать": {'num': 17, 'type': 'final', 'level': 1},
    "восемнадцать": {'num': 18, 'type': 'final', 'level': 1},
    "девятнадцать": {'num': 19, 'type': 'final', 'level': 1},
    "двадцать": {'num': 20, 'type': 'degree', 'level': 2},
    "тридцать": {'num': 30, 'type': 'degree', 'level': 2},
    "сорок": {'num': 40, 'type': 'degree', 'level': 2},
    "пятьдесят": {'num': 50, 'type': 'degree', 'level': 2},
    "шестьдесят": {'num': 60, 'type': 'degree', 'level': 2},
    "семьдесят": {'num': 70, 'type': 'degree', 'level': 2},
    "восемьдесят": {'num': 80, 'type': 'degree', 'level': 2},
    "девяносто": {'num': 90, 'type': 'degree', 'level': 2},
    "сто": {'num': 100, 'type': 'degree', 'level': 3},
    "двести": {'num': 200, 'type': 'degree', 'level': 3},
    "триста": {'num': 300, 'type': 'degree', 'level': 3},
    "четыреста": {'num': 400, 'type': 'degree', 'level': 3},
    "пятьсот": {'num': 500, 'type': 'degree', 'level': 3},
    "шестьсот": {'num': 600, 'type': 'degree', 'level': 3},
    "семьсот": {'num': 700, 'type': 'degree', 'level': 3},
    "восемьсот": {'num': 800, 'type': 'degree', 'level': 3},
    "девятьсот": {'num': 900, 'type': 'degree', 'level': 3},
    "тысяча": {'num': 1000, 'type': 'degree', 'level': 4},
    "одна тысяча": {'num': 1000, 'type': 'degree', 'level': 4},
    "две тысячи": {'num': 2000, 'type': 'degree', 'level': 4},
    "три тысячи": {'num': 3000, 'type': 'degree', 'level': 4},
    "четыре тысячи": {'num': 4000, 'type': 'degree', 'level': 4},
    "пять тысяч": {'num': 5000, 'type': 'degree', 'level': 4},
    "шесть тысяч": {'num': 6000, 'type': 'degree', 'level': 4},
    "семь тысяч": {'num': 7000, 'type': 'degree', 'level': 4},
    "восемь тысяч": {'num': 8000, 'type': 'degree', 'level': 4},
    "девять тысяч": {'num': 9000, 'type': 'degree', 'level': 4},
    'два ноля': {'num': '00', 'type': 'self', 'level': 1},
    'два нуля': {'num': '00', 'type': 'self', 'level': 1},
    'три ноля': {'num': '000', 'type': 'self', 'level': 1},
    'три нуля': {'num': '000', 'type': 'self', 'level': 1},
    'две единицы': {'num': '11', 'type': 'self', 'level': 1},
    'три единицы': {'num': '111', 'type': 'self', 'level': 1}
}


def make_num(text):
    words = text.split()
    tokens = filter_tokens(weave_double_complex_tokens(words))
    numbers = []
    while tokens:
        token = tokens_config[tokens[0]]
        num, tokens = make_num_greedy(tokens) if token['type'] != 'self' else (token['num'], tokens[1:])
        numbers.append(num)

    return ''.join([str(num) for num in numbers])


def make_num_x(text):
    words = text.split()
    tokens = weave_double_complex_tokens(words)
    numbers = []
    while tokens:
        if tokens[0] not in tokens_config:
            numbers.append('x')
            tokens = tokens[1:]
        else:
            token = tokens_config[tokens[0]]
            num, tokens = make_num_greedy(tokens) if token['type'] != 'self' else (token['num'], tokens[1:])
            numbers.append(num)

    return ''.join([str(num) for num in numbers])


# TODO: add limitation by length or prefix condition
def make_num_versions(text):
    words = text.split()
    tokens = filter_tokens(weave_double_complex_tokens(words))
    versions = make_num_versions_internal(tokens)
    return [''.join([str(num) for num in numbers]) for numbers in versions]


def filter_tokens(words):
    return [w for w in words if w in tokens_config]


def weave_double_complex_tokens(words):
    if not words:
        return words

    words_with_next = [((w, next_w), f"{w} {next_w}" in tokens_config) for (w, next_w) in zip(words, words[1:] + [""])]
    w_is_complex = [is_complex for (_, is_complex) in words_with_next]
    words_filtered = [words_with_next[0]] + \
                     [w_with_next for (w_with_next, previous_is_complex) in zip(words_with_next[1:], w_is_complex)
                      if not previous_is_complex]

    return [w if not is_complex else f"{w} {w_next}" for ((w, w_next), is_complex) in words_filtered]


def make_num_versions_internal(words):
    if not words:
        return [[]]

    num_token = tokens_config[words[0]]
    if num_token['type'] == 'self':
        num = num_token['num']
        return [[num] + v for v in make_num_versions_internal(words[1:])]

    num_versions = set()
    versions = []
    for d in range(num_token['level'], 0, -1):
        num, rest = make_num_one_greedy(words, num_token['level'], d)
        if num not in num_versions:
            num_versions.add(num)
            versions.extend([[num] + v for v in make_num_versions_internal(rest)])
    return versions


def make_num_greedy(words):
    level = tokens_config[words[0]]['level']
    return make_num_one_greedy(words, level, level)


def make_num_one_greedy(words, level, depth):
    if not words or depth == 0 or level == 0:
        return 0, words
    num_token = tokens_config[words[0]]
    if num_token['level'] > level or num_token['type'] == 'self':
        return 0, words

    if num_token['type'] == 'final':
        return num_token['num'], words[1:]

    acc, rest = make_num_one_greedy(words[1:], num_token['level'] - 1, depth - 1)
    return acc + num_token['num'], rest
