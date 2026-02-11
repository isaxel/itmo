import re

def solve(string):
    """ Возвращает количество смайликов вида [<) в строке
    466049 % 6 = 5 => Глаза: [
    466049 % 4 = 1 => Нос: <
    466049 % 8 = 1 => Рот: )
    """
    pattern = r'\[<\)'
    return len(re.findall(pattern, string))