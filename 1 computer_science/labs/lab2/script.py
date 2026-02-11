def hamming_code_7_4(inp_mes):
    s1 = int(inp_mes[0]) + int(inp_mes[2]) + int(inp_mes[4]) + int(inp_mes[6])
    s2 = int(inp_mes[1]) + int(inp_mes[2]) + int(inp_mes[5]) + int(inp_mes[6])
    s3 = int(inp_mes[3]) + int(inp_mes[5]) + int(inp_mes[4]) + int(inp_mes[6])

    s = str(s1 % 2) + str(s2 % 2) + str(s3 % 2)

    data1 = ['no mistakes', 'r3', 'r2', 'i3', 'r1', 'i2', 'i1', 'i4']
    for i in range(8):
        if int(s, 2) == i:
            mist = data1[i]

    data2 = ['0', 'r1', 'r2', 'i1', 'r3', 'i2', 'i3', 'i4']
    for k in range(len(data2)):
        if mist == data2[k]:
            if inp_mes[k] == '0':
                inp_mes = inp_mes[:(k - 1)] + '1' + inp_mes[k:]
            else:
                inp_mes = inp_mes[:(k - 1)] + '0' + inp_mes[k:]

    print(f'There is a mistake in the {mist} symbol\nThe correct message was {int(inp_mes)}')


a = str(input())
if len(a) == 7:
    hamming_code_7_4(a)

