q = "inc"
while q == "inc":
    n = input()
    if not "98765432" in n and len(n) == 7:
        q = "cor"
        l = list(map(int,n))
        s1 = str((l[0] + l[2]+l[4] + l[6])%2)
        s2 = str((l[1]+l[2] + l[5]+l[6]) % 2)
        s3 = str((l[3]+l[4]+l[5]+l[6]) % 2)
        S = s1+s2+s3
        if S == "100":
            l[0] = (1 + l[0])%2
            x = "r1"
        elif S == "010":
            x = "r2"
            l[1] = (1 + l[1])%2
        elif S == "110":
            x = "i1"
            l[2] = (1 + l[2])%2
        elif S == "001":
            x = "r3"
            l[3] = (1 + l[3])%2
        elif S == "101":
            x = "i2"
            l[4] = (1 + l[4])%2
        elif S == "011":
            x = "i3"
            l[5] = (1 + l[5])%2
        elif S == "111" :
            x = "i4"
            l[6] = (1 + l[6])%2
        else:
            x = "correct"
        print(x)
    else:
        print("НЕВЕРНЫЙ ВВОД")