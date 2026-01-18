import re
import json

#pattern = r'\b[бвгджзйклмнпрстфхцчшщьъ]*([ауоыиэяюёе])\1*[бвгджзйклмнпрстфхцчшщьъ]*\b'


def solve(string):
    vowels = 'аеёиоуыэюяaeiou'
    consonants = 'БВГДЖЗЙКЛМНПРСТФХЦЧШЩbcdfghjklmnpqrstvwxyz'
    pattern = r'[а-я]*([ауоыиэяюёе])[а-я]*(?=\1)[а-я]*'
    mathes = re.findall(pattern, string, re.IGNORECASE)
    return ' '.join(mathes)


print('Введите текст: ')
S = input()
#my_json = {}

my_answers = []
my_answers.append(solve(S))

print(my_answers)



'''
def solve(text):
    return [word for word in re.findall(r'\b\w+\b', text) if len(set(re.findall(r'[ауоыиэяюёе]', word))) == 1]


s = str(input())
my_answers = []

matches = sorted(solve(s))
my_answers = sorted(matches, key=len)
#print(my_answers)

#my_json = {}'''

'''my_json["answers"] = my_answers

with open('result.json', 'w', encoding="utf-8") as file:
    dumped_json = json.dumps(my_json, ensure_ascii=False)
    file.write(dumped_json)'''
