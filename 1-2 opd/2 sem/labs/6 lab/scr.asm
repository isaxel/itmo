		ORG 	0x0
v0: 	WORD 	$default, 	0x180
v1: 	WORD 	$default,   0x180
v2: 	WORD 	$int2,    	0x180
v3: 	WORD 	$int3, 		0x180
v4: 	WORD 	$default, 	0x180
v5: 	WORD 	$default, 	0x180
v6: 	WORD 	$default, 	0x180
v7: 	WORD 	$default, 	0x180

ORG 0x024
X: WORD ?

max: WORD 0x0020 		; 32, максимальное значение Х
min: WORD 0xFFE0 		; -31, минимальное значение Х

default:    IRET 		; Обработка прерывания по умолчанию

START:  	DI
    		CLA
    		OUT 0x1 	; Запрет прерываний для неиспользуемых ВУ
   			OUT 0x3
    		OUT 0xB
    		OUT 0xD
    		OUT 0x11
    		OUT 0x15
    		OUT 0x19
    		OUT 0x1D
    		
			LD #0xA 	; Загрузка в аккумулятор MR (1000|0010=1010)
    		OUT 5 		; Разрешение прерываний для 2 ВУ
    		LD #0xB  	; Загрузка в аккумулятор MR (1000|0011=1011)
    		OUT 7 		; Разрешение прерываний для 3 ВУ
    		EI
    		
main:   	DI 		   	; Запрет прерываний чтобы обеспечить атомарность операции
			NOP
   			LD X
    		INC
			INC
   			CALL check
    		ST X
    		ei
    		JUMP main

int2:					; Обработка прерывания на ВУ-2
    		LD X
    		NOP
    		IN 4
    		ADD X
    		call check
    		ST X
   			NOP
    		IRET

int3: 					; Обработка прерывания на ВУ-3
  			LD X
			NOP
    		ASL
			ASL
    		SUB #2
    		OUT 6
    		NOP
    		IRET

check:  					; Проверка принадлежности X к ОДЗ
check_min:	CMP min 		; Если x > min переход на проверку верхней границы
    		BPL check_max   
   			JUMP ld_min 	; Иначе загрузка min в аккумулятор
check_max: 	CMP max 		; Проверка пересечения верхней границы X
    		BMI return  	; Если x < max переход
ld_min:		LD min  		; Загрузка минимального значения в X 
return:		RET  			; Метка возврата из проверки на ОДЗ  