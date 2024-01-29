# Pipelining-Visualization
A Visualization in python for Pipelining in Computer Architecture

Conversions used: 
For r-type instructions : 
1 – char 
6 bits – opcode 
3 bits each for destination, source1 and source2 registers respectively 
Example: 'r000001001010011' for  ADD R1, R2, R3 
 
For i-type instructions: 
1 – char 
2 bits – opcode 
7 bits – address 
3 bits each for destination, source1 and source2 registers respectively 
Example: 'i000011110000100' for Lw R0, 30(R4) 
 
Conversions of registers: 
         'R1':'001', 
         'R2':'010', 
         'R3':'011', 
         'R4':'100', 
         'R5':'101', 
         'R6':'110', 
         'R7':'111', 
         'R0':'000' 
 
OpCodes used: 
         'ADD':'000001', 
         'SUB':'000010', 
         'MUL':'000011', 
         'DIV':'000100', 
         'IDIV':'000101', 
         'MOD':'000110', 
         'EXP':'000111', 
         'BEQ':'001000', 
         'BNE':'001001', 
         'LW':'00', 
         'SW':'01'
