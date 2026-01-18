#из фиббоначевой в 10

inputed_number = str(input())
inputed_number = inputed_number[::-1]


arr_of_fibonachi = [1, 2]
for count in range(0, len(inputed_number)):
    arr_of_fibonachi.append(arr_of_fibonachi[count] + arr_of_fibonachi[count + 1])


final_number = 0
for index in range(len(inputed_number)):
    final_number += (int(inputed_number[index]) * arr_of_fibonachi[index])


print(final_number)