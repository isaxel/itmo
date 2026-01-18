import re
#import json

def solve(string):
    vowels = 'аеёиоуыэюяaeiou'
    consonants = 'БВГДЖЗЙКЛМНПРСТФХЦЧШЩbcdfghjklmnpqrstvwxyz'
    pattern = rf'\S*[{vowels}][{vowels}]\S*\b(?! \S*[{consonants}]\S*[{consonants}]\S*[{consonants}]\S*[{consonants}]\S*)'
    mathes = re.findall(pattern, string, re.IGNORECASE)
    return ' '.join(mathes)


print('Введите текст: ')
S = input()
#my_json = {}

my_answers = []
my_answers.append(solve(S))

print(my_answers)

'''my_json["answers"] = my_answers

with open('result.json', 'w', encoding="utf-8") as file:
    dumped_json = json.dumps(my_json, ensure_ascii=False)
    file.write(dumped_json)'''