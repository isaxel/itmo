#!/bin/bash
rm -rf repo wc
svnadmin create repo
# REPO_URL="file://$(pwd)/repo"
REPO_URL="file:///$(cygpath -m "$(pwd)/repo")"
svn mkdir -m "project structure" "$REPO_URL/trunk" "$REPO_URL/branches"
svn checkout "$REPO_URL/trunk" wc
cd wc


# r0 (красный)
unzip -o ../commits/commit0.zip -d .
svn add * --force
svn commit -m "Initial commit (r0)" --username=red

# r1 (синий) – создание ветки branch1 от trunk
svn copy "$REPO_URL/trunk" "$REPO_URL/branches/branch1" -m "Create branch1"
svn switch "$REPO_URL/branches/branch1"
svn rm * --force
unzip -o ../commits/commit1.zip -d .
svn add * --force
svn commit -m "Revision 1 (r1)" --username=blue

# r2 (синий) – создание ветки branch2 от branch1
svn copy "$REPO_URL/branches/branch1" "$REPO_URL/branches/branch2" -m "Create branch2"
svn switch "$REPO_URL/branches/branch2"
svn rm * --force
unzip -o ../commits/commit2.zip -d .
svn add * --force
svn commit -m "Revision 2 (r2)" --username=blue

# r3 (синий) – создание ветки branch3 от branch2
svn copy "$REPO_URL/branches/branch2" "$REPO_URL/branches/branch3" -m "Create branch3"
svn switch "$REPO_URL/branches/branch3"
svn rm * --force
unzip -o ../commits/commit3.zip -d .
svn add * --force
svn commit -m "Revision 3 (r3)" --username=blue

# r4 (красный) – ветка branch4 от r3
svn copy "$REPO_URL/branches/branch3" "$REPO_URL/branches/branch4" -m "Create branch4"
svn switch "$REPO_URL/branches/branch4"
svn rm * --force
unzip -o ../commits/commit4.zip -d .
svn add * --force
svn commit -m "Revision 4 (r4)" --username=red   

# r5 (синий) на branch3
svn switch "$REPO_URL/branches/branch3"
svn rm * --force
unzip -o ../commits/commit5.zip -d .
svn add * --force
svn commit -m "Revision 5 (r5)" --username=blue

# r6 (красный) – ветка branch5 от r5
svn copy "$REPO_URL/branches/branch3" "$REPO_URL/branches/branch5" -m "Create branch5"
svn switch "$REPO_URL/branches/branch5"
svn rm * --force
unzip -o ../commits/commit6.zip -d .
svn add * --force
svn commit -m "Revision 6 (r6)" --username=red   

# r7 (красный) на trunk
svn switch "$REPO_URL/trunk"
svn rm * --force
unzip -o ../commits/commit7.zip -d .
svn add * --force
svn commit -m "Revision 7 (r7)" --username=red

# r8 (синий) на branch1
svn switch "$REPO_URL/branches/branch1"
svn rm * --force
unzip -o ../commits/commit9.zip -d .
svn add * --force
svn commit -m "Revision 9 (r9)" --username=blue

# r9 (синий) на branch6 от r8
svn copy "$REPO_URL/branches/branch1" "$REPO_URL/branches/branch6" -m "Create branch6"
svn switch "$REPO_URL/branches/branch6"
svn rm * --force

svn merge "$REPO_URL/branches/branch1"

unzip -o ../commits/commit9.zip -d .
svn add * --force
svn commit -m "Revision 9 (r9)" --username=blue

# r10 на trunk
svn switch "$REPO_URL/trunk"
svn rm * --force
unzip -o ../commits/commit10.zip -d .
svn add * --force
svn commit -m "Revision 10 (r10)" --username=red

# r11 на branch2
svn switch "$REPO_URL/branches/branch2"
svn rm * --force
unzip -o ../commits/commit11.zip -d .
svn add * --force
svn commit -m "Revision 11 (r11)" --username=blue

# r12 – ветка branch7 от r11
svn copy "$REPO_URL/branches/branch2" "$REPO_URL/branches/branch7" -m "Create branch7"
svn switch "$REPO_URL/branches/branch7"
svn rm * --force
unzip -o ../commits/commit12.zip -d .
svn add * --force
svn commit -m "Revision 12 (r12)" --username=red

# r13 на branch3
svn switch "$REPO_URL/branches/branch3"
svn rm * --force
unzip -o ../commits/commit13.zip -d .
svn add * --force
svn commit -m "Revision 13 (r13)" --username=blue

# r14 на branch7
svn switch "$REPO_URL/branches/branch7"
svn rm * --force
unzip -o ../commits/commit14.zip -d .
svn add * --force
svn commit -m "Revision 14 (r14)" --username=red

# r15 – слияние branch7 в branch3
svn switch "$REPO_URL/branches/branch3"

svn merge "$REPO_URL/branches/branch7"
# разрешение конфликта
nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit15.zip -d .
svn add * --force

svn commit -m "Merge branch7 into branch3 -> r15" --username=blue

# r16 – ветка branch8 от r15
svn copy "$REPO_URL/branches/branch3" "$REPO_URL/branches/branch8" -m "Create branch8"
svn switch "$REPO_URL/branches/branch8"
svn rm * --force
unzip -o ../commits/commit16.zip -d .
svn add * --force
svn commit -m "Revision 16 (r16)" --username=red

# r17 на branch5
svn switch "$REPO_URL/branches/branch5"
svn rm * --force
unzip -o ../commits/commit17.zip -d .
svn add * --force
svn commit -m "Revision 17 (r17)" --username=red

# r18 – на branch3
svn switch "$REPO_URL/branches/branch3"
svn rm * --force
unzip -o ../commits/commit18.zip -d .
svn add * --force
svn commit -m "Revision 18 (r18)" --username=blue

# r19 – ветка branch9 от r18
svn copy "$REPO_URL/branches/branch3" "$REPO_URL/branches/branch9" -m "Create branch9"
svn switch "$REPO_URL/branches/branch9"
svn rm * --force
unzip -o ../commits/commit19.zip -d .
svn add * --force
svn commit -m "Revision 19 (r19)" --username=red

# r20 на branch3
svn switch "$REPO_URL/branches/branch3"
svn rm * --force
unzip -o ../commits/commit20.zip -d .
svn add * --force
svn commit -m "Revision 20 (r20)" --username=blue

# r21 на branch9
svn switch "$REPO_URL/branches/branch9"
svn rm * --force
unzip -o ../commits/commit21.zip -d .
svn add * --force
svn commit -m "Revision 21 (r21)" --username=red

# r22 на branch3
svn switch "$REPO_URL/branches/branch3"
svn rm * --force
unzip -o ../commits/commit22.zip -d .
svn add * --force
svn commit -m "Revision 22 (r22)" --username=blue

# r23 на branch3
svn rm * --force
unzip -o ../commits/commit23.zip -d .
svn add * --force
svn commit -m "Revision 23 (r23)" --username=blue

# r24 – слияние branch3 в trunk
svn switch "$REPO_URL/trunk"
svn merge "$REPO_URL/branches/branch3"

nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit24.zip -d .
svn add * --force

svn commit -m "Merge branch3 into trunk -> r24" --username=red

# r25 на branch2
svn switch "$REPO_URL/branches/branch2"
svn rm * --force
unzip -o ../commits/commit25.zip -d .
svn add * --force
svn commit -m "Revision 25 (r25)" --username=blue

# r26 на branch9
svn switch "$REPO_URL/branches/branch9"
svn rm * --force
unzip -o ../commits/commit26.zip -d .
svn add * --force
svn commit -m "Revision 26 (r26)" --username=red

# r27 на branch4
svn switch "$REPO_URL/branches/branch4"
svn rm * --force
unzip -o ../commits/commit27.zip -d .
svn add * --force
svn commit -m "Revision 27 (r27)" --username=red

# r28 – слияние branch4 в branch9
svn switch "$REPO_URL/branches/branch9"
svn merge "$REPO_URL/branches/branch4"

nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit28.zip -d .
svn add * --force

svn commit -m "Merge branch4 into branch9 -> r28" --username=red

# r29 – слияние branch9 в branch5
svn switch "$REPO_URL/branches/branch5"
svn merge "$REPO_URL/branches/branch9"

nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit29.zip -d .
svn add * --force

svn commit -m "Merge branch9 into branch5 -> r29" --username=red

# r30 – слияние branch5 в branch8
svn switch "$REPO_URL/branches/branch8"
svn merge "$REPO_URL/branches/branch5"

nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit30.zip -d .
svn add * --force

svn commit -m "Merge branch5 into branch8 -> r30" --username=red

# r31 – слияние branch8 в branch2
svn switch "$REPO_URL/branches/branch2"
svn merge "$REPO_URL/branches/branch8"

nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit31.zip -d .
svn add * --force

svn commit -m "Merge branch8 into branch2 -> r31" --username=blue

# r32 – слияние branch2 в branch6
svn switch "$REPO_URL/branches/branch6"
svn merge "$REPO_URL/branches/branch2"

nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit32.zip -d .
svn add * --force

svn commit -m "Merge branch2 into branch6 -> r32" --username=blue

# r33 – финальное слияние branch6 в trunk
svn switch "$REPO_URL/trunk"
svn merge "$REPO_URL/branches/branch6"

nano B.java H.java I.java J.java
svn resolved B.java H.java I.java J.java

svn rm * --force
unzip -o ../commits/commit33.zip -d .
svn add * --force

svn commit -m "Merge branch6 into trunk -> r33" --username=red

svn update