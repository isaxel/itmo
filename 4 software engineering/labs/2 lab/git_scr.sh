# Очистка ненужных данных и backup .git
cp -r .git .rotter
cp .gitignore .rotterignore

rm -rf .git
rm -f .gitignore
echo "- Создан бэкап .git"

find src -type f ! -name '.keep' -delete
echo "- src очищен"

git init
mkdir commits

# Начальная ревизия r0 (пользователь 1, красный)
unzip -o commits/commit0.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Initial commit (r0)"

# r1 (синий) – создание branch1 от master
git checkout -b branch1
unzip -o commits/commit1.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 1 (r1)"

# r2 (синий) – создание branch2 от branch1
git checkout -b branch2 branch1
unzip -o commits/commit2.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 2 (r2)"

# r3 (синий) – создание branch3 от branch2
git checkout -b branch3 branch2
unzip -o commits/commit3.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 3 (r3)"

# r4 (красный) – ветка branch4 от branch3
git checkout -b branch4 branch3
unzip -o commits/commit4.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 4 (r4)"

# r5 (синий) на branch3
git checkout branch3
unzip -o commits/commit5.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 5 (r5)"

# r6 (красный) – ветка branch5 от branch3
git checkout -b branch5 branch3
unzip -o commits/commit6.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 6 (r6)"

# r7 (красный) на master
git checkout master
unzip -o commits/commit7.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 7 (r7)"

# r8 (синий) на branch1
git checkout branch1
unzip -o commits/commit8.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 9 (r9)"

# r9 (синий) – branch6 от branch1, merge branch1
git checkout -b branch6 branch1
git merge --no-commit branch1
unzip -o commits/commit9.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 9 (r9)"

# r10 на master
git checkout master
unzip -o commits/commit10.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 10 (r10)"

# r11 на branch2
git checkout branch2
unzip -o commits/commit11.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 11 (r11)"

# r12 – ветка branch7 от branch2
git checkout -b branch7 branch2
unzip -o commits/commit12.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 12 (r12)"

# r13 на branch3
git checkout branch3
unzip -o commits/commit13.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 13 (r13)"

# r14 на branch7
git checkout branch7
unzip -o commits/commit14.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 14 (r14)"

# r15 – слияние branch7 в branch3
git checkout branch3
git merge --no-commit branch7
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit15.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Merge branch7 into branch3 -> r15"

# r16 – ветка branch8 от branch3
git checkout -b branch8 branch3
unzip -o commits/commit16.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 16 (r16)"

# r17 на branch5
git checkout branch5
unzip -o commits/commit17.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 17 (r17)"

# r18 на branch3
git checkout branch3
unzip -o commits/commit18.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 18 (r18)"

# r19 – ветка branch9 от branch3
git checkout -b branch9 branch3
unzip -o commits/commit19.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 19 (r19)"

# r20 на branch3
git checkout branch3
unzip -o commits/commit20.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 20 (r20)"

# r21 на branch9
git checkout branch9
unzip -o commits/commit21.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 21 (r21)"

# r22 на branch3
git checkout branch3
unzip -o commits/commit22.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 22 (r22)"

# r23 на branch3
unzip -o commits/commit23.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 23 (r23)"

# r24 – слияние branch3 в master
git checkout master
git merge --no-commit branch3
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit24.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Merge branch3 into trunk -> r24"

# r25 на branch2
git checkout branch2
unzip -o commits/commit25.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Revision 25 (r25)"

# r26 на branch9
git checkout branch9
unzip -o commits/commit26.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 26 (r26)"

# r27 на branch4
git checkout branch4
unzip -o commits/commit27.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Revision 27 (r27)"

# r28 – слияние branch4 в branch9
git checkout branch9
git merge --no-commit branch4
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit28.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Merge branch4 into branch9 -> r28"

# r29 – слияние branch9 в branch5
git checkout branch5
git merge --no-commit branch9
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit29.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Merge branch9 into branch5 -> r29"

# r30 – слияние branch5 в branch8
git checkout branch8
git merge --no-commit branch5
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit30.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Merge branch5 into branch8 -> r30"

# r31 – слияние branch8 в branch2
git checkout branch2
git merge --no-commit branch8
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit31.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Merge branch8 into branch2 -> r31"

# r32 – слияние branch2 в branch6
git checkout branch6
git merge --no-commit branch2
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit32.zip -d src
git add .
git commit --author="blue <blue@example.com>" -m "Merge branch2 into branch6 -> r32"

# r33 – финальное слияние branch6 в master
git checkout master
git merge --no-commit branch6
nano src/B.java src/H.java src/I.java src/J.java
unzip -o commits/commit33.zip -d src
git add .
git commit --author="red <red@example.com>" -m "Merge branch6 into trunk -> r33"

# Вывод графа
# git log --graph --abbrev-commit --decorate --all
git log --graph --oneline --decorate --all
