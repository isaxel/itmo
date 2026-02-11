        ORG     0x300          ; Начало программы

START:  CLA                     ; Очистка аккумулятора
        LD      (BUF_START)     ; Адрес начала буфера
        ST      PTR            ; Инициализируем указатель

; Ввод символов с клавиатуры
READ:   IN      0x019          ; Опрос флага ввода (SR)
        AND     #0x40
        BEQ     READ           ; Ждём символ
        IN      0x018          ; Чтение символа из клавиатуры (DR)
        ST      TEMP           ; Сохраняем во временную переменную
        
        LD      TEMP           ; Загружаем символ
        ST      (PTR)+         ; Записываем в буфер, Инкрементируем указатель
        CMP     #0x2E          ; Проверка: это точка?
        BEQ     PROCESS        ; Если точка, то переходим к обработке
        JUMP    READ           ; Цикл чтения

PROCESS: 
        LD     (BUF_START)    ; Обработка строки c начала
        ST     PTR            ; Снова ставим указатель в начало

QUICK_LOOP:    
        LD     (PTR)
        ST     TEMP           ; Сохраняем символ

        CMP    #0x2E          ; Стоп-символ?
        BEQ    STOP          ; Переход к печати

        LD     TEMP
        CMP    compare_a
        BEQ    UPPER

        LD     TEMP
        CMP    compare_ye
        BEQ    UPPER

        LD     TEMP
        CMP    compare_i
        BEQ    UPPER

        LD     TEMP
        CMP    compare_o
        BEQ    UPPER

        LD     TEMP
        CMP    compare_y
        BEQ    UPPER

        LD     TEMP
        CMP    compare_u
        BEQ    UPPER

        LD     TEMP
        CMP    compare_e
        BEQ    UPPER

        LD     TEMP
        CMP    compare_yu
        BEQ    UPPER

        LD     TEMP
        CMP    compare_ya
        BEQ    UPPER
        
        LD     TEMP
        OUT    0x0C 

        LD     (PTR)+
        JUMP   QUICK_LOOP           ; Не гласная — пропускаем
STOP:   HLT 

UPPER:        
        LD     TEMP
        SUB    #32
        ST     (PTR)+          ; Записываем преобразованный символ
        OUT    0x0C 
        JUMP   QUICK_LOOP

; Данные
BUF_START:   WORD 0x200     ; Начало буфера (память под строку)
TEMP:        WORD ?     ; Временное хранилище символа
PTR:         WORD ?     ; Указатель на текущий символ

;нерасширение знака
compare_o: word 0x00ee
compare_a: word 0x00e0
compare_ye: word 0x00e5
compare_i: word 0x00e8
compare_y: word 0x00f3
compare_u: word 0x00fb
compare_e: word 0x00fd
compare_yu: word 0x00fe
compare_ya: word 0x00ff