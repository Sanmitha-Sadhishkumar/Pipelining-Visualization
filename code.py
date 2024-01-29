import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Rectangle

curr_type1, curr_opcode, curr_operand1, curr_operand2, curr_operand3, curr_address, prev_address, prev_type1, prev_opcode, prev_operand1, prev_operand2, prev_operand3 = 0,0,0,0,0,0,0,0,0,0,0,0
class PipelineProcessor:
        
    def __init__(self):
        self.registers = [58, 3, 4, 5, 7, 92, 2, 3]
        self.memory = [0, 7, 6, 58, 3, 4, 5, 7, 92, 2, 3, 8, 5, 68, 25, 9, 74] *8

        self.pc = 0  
        self.pipeline = [None] * 5  
        self.without_instruction_count = 0
        self.with_instruction_count = 0

        self.without_forwarding_path = []
        self.with_forwarding_path = []
        self.hazards = []  

    def fetch(self):
        instruction = self.memory[self.pc]
        self.pipeline[0] = instruction
        self.pc += 1

    def decode(self):
        instruction = self.pipeline[0]
        if instruction[0] == 'r':
            type1 = instruction[0]
            opcode = eval('0b' + instruction[1:7])
            operand1 = eval('0b' + instruction[7:10])
            operand2 = eval('0b' + instruction[10:13])
            operand3 = eval('0b' + instruction[13:16])
            self.pipeline[1] = (type1, opcode, operand1, operand2, operand3)
        if instruction[0] == 'i':
            type1 = instruction[0]
            opcode = eval('0b' + instruction[1:3])
            address = eval('0b' + instruction[3:10])
            operand1 = eval('0b' + instruction[10:13])
            operand2 = eval('0b' + instruction[13:16])
            self.pipeline[1] = (type1, opcode, address,operand1, operand2)

    def execute(self):
        type1, opcode, operand1, operand2, operand3, address, result=0,0,0,0,0,0,0
        if self.pipeline[1][0] == 'r':
            type1, opcode, operand1, operand2, operand3 = self.pipeline[1]
            if opcode == 1:  # Add
                result = self.registers[operand2] + self.registers[operand3]
            elif opcode == 2:  # Subtract
                result = self.registers[operand2] - self.registers[operand3]
            elif opcode == 3:  # Multiply
                result = self.registers[operand2] * self.registers[operand3]
            elif opcode == 4:  # Divide
                result = self.registers[operand2] / self.registers[operand3]
            elif opcode == 5:  # Integer division
                result = self.registers[operand2] // self.registers[operand3]
            elif opcode == 6:  # Mod
                result = self.registers[operand2] % self.registers[operand3]
            elif opcode == 7:  # Exponent
                result = self.registers[operand2] ** self.registers[operand3]
            elif opcode == 8:  # beq
                result = self.registers[operand2] == self.registers[operand3]
            elif opcode == 9:  # bne
                result = self.registers[operand2] != self.registers[operand3]
        if self.pipeline[1][0] == 'i':
            type1, opcode, address,  operand1, operand2=self.pipeline[1]
            if opcode == 0:  # Load
                address = self.registers[operand2]
                result = self.memory[address]
            elif opcode == 1:  # Store
                address = self.registers[operand2]
                data = self.registers[operand1]
                self.memory[address] = data
                result = data
            else:
                print(opcode)
        self.pipeline[2] = result

    def memory_access(self):
        type1, opcode, operand1, operand2, operand3, address=0,0,0,0,0,0
        result = self.pipeline[2]
        if self.pipeline[1][0] == 'r':
            type1, opcode, operand1, operand2, operand3 = self.pipeline[1]
            self.pipeline[3] = result
        elif self.pipeline[1][0] == 'i':
            type1, opcode, address,  operand1, operand2=self.pipeline[1]
            if opcode == 0: 
                self.pipeline[3] = result
            elif opcode == 1:  
                self.pipeline[3] = operand1  
            else:
                self.pipeline[3] = result

    def write_back(self):
        result = self.pipeline[3]
        type1, opcode, operand1, operand2, operand3, address=0,0,0,0,0,0
        if self.pipeline[1][0] == 'r':
            type1, opcode, operand1, operand2, operand3 = self.pipeline[1]
        elif self.pipeline[1][0] == 'i':
            type1, opcode, address,  operand1, operand2=self.pipeline[1]
        if not (opcode == 1 and type1=='i'): 
            self.registers[operand1] = result
        self.pipeline[4] = result
        self.without_instruction_count += 1
        self.with_instruction_count += 1

    def handle_data_hazard(self):
        global curr_type1, curr_opcode, curr_operand1, curr_operand2, curr_operand3, curr_address, prev_address, prev_type1, prev_opcode, prev_operand1, prev_operand2, prev_operand3
        current_instr = self.pipeline
        if current_instr[1][0]=='r':
            curr_type1, curr_opcode, curr_operand1, curr_operand2, curr_operand3 = current_instr[1]
        elif current_instr[1][0]=='i':
            curr_type1, curr_opcode, curr_address,  curr_operand1, curr_operand2=current_instr[1]
            curr_operand3 = None
        
        if self.without_instruction_count >= 2:
            if self.without_forwarding_path[self.without_instruction_count - 2] not in ['RAW','Load-store','Control'] and self.without_instruction_count >= 2:
                prev_instr = self.without_forwarding_path[self.without_instruction_count - 2]
            else:
                k=1
                while self.without_forwarding_path[self.without_instruction_count - k] in ['RAW','Load-store','Control']:
                    k+=1
                prev_instr = self.without_forwarding_path[self.without_instruction_count - k]
            if prev_instr[1][0]=='r':
                prev_type1, prev_opcode, prev_operand1, prev_operand2, prev_operand3 = prev_instr[1]
            elif prev_instr[1][0]=='i':
                prev_type1, prev_opcode, prev_address,  prev_operand1, prev_operand2=prev_instr[1]
            
            hazards = []
                
            if prev_type1=='i' and (curr_operand2 == prev_operand1 or curr_operand3 == prev_operand1):
                hazards.append('Load-Store')
                self.without_forwarding_path.extend(['Load-store'])
                self.without_forwarding_path.extend(['Load-store'])
                self.with_forwarding_path.extend(['Load-store'])
                self.without_instruction_count += 2
                self.with_instruction_count += 1

            # Control Hazard
            control_opcodes = [8, 9] 
            if prev_opcode in control_opcodes:
                hazards.append('Control')
                self.without_forwarding_path.extend(['Control'])
                self.without_forwarding_path.extend(['Control'])
                self.without_forwarding_path.extend(['Control'])
                self.with_forwarding_path.extend(['Control'])
                self.without_instruction_count += 3
                self.with_instruction_count += 1
            self.hazards.append(hazards)

            if (curr_operand2 == prev_operand1 or curr_operand3 == prev_operand1) and self.without_forwarding_path[self.without_instruction_count - 2] not in ['Load-store','Control']:
                self.without_forwarding_path.extend(['RAW'])
                hazards.append('RAW')
                self.without_instruction_count += 1
            # RAR
            if (curr_operand2 == prev_operand2 or curr_operand3 == prev_operand3 or curr_operand2 == prev_operand3 or curr_operand3 == prev_operand2):
                hazards.append('RAW')
            # WAR (Write After Read)
            if prev_type1 == 'r' and (prev_operand2 == curr_operand1 or prev_operand3 == curr_operand2):
                hazards.append('WAR')
            # WAW (Write After Write)
            if prev_type1 == 'r' and (prev_operand1 == curr_operand1):
                hazards.append('WAW')
            

    def plot_without_forwarding_path(self):
        count=0
        pipeline_stages = ['IF', 'ID', 'EX', 'MEM', 'WB']
        without_instruction_count = len(self.without_forwarding_path)
        with_instruction_count = len(self.with_forwarding_path)
        fig, ax = plt.subplots(2)
        plt.tight_layout(pad=3.0)
        ax[0].set_title('Pipelining without Forwarding Path')

        for i in range(len(pipeline_stages)):
            
            for j in range(len(self.without_forwarding_path)):
                if self.without_forwarding_path[j] not in ['RAW','Load-store','Control']:
                    box = plt.Rectangle((i+j, j), 0.4, 0.4, facecolor='lightblue', edgecolor='black')
                    ax[0].add_patch(box)
                    ax[0].text(j + i +0.2, j + 0.2, pipeline_stages[i], ha='center', va='center')
                elif self.without_forwarding_path[j]=='RAW':
                    ax[0].text(j+i+0.2, j+0.2, 'RAW Stall', ha='center', va='center', color='red')
                elif self.without_forwarding_path[j]=='Load-store':
                    ax[0].text(j+i+0.2, j+0.2, 'L-S Stall', ha='center', va='center', color='red')
                elif self.without_forwarding_path[j]=='Control':
                    ax[0].text(j+i+0.2, j+0.2, 'Control Stall', ha='center', va='center', color='red')
               

        ax[0].set_xlabel('Cycle')
        ax[0].set_ylabel('Instruction')
        ax[0].set_xticks(range(without_instruction_count+4))
        ax[0].set_yticks(range(without_instruction_count))
        ax[0].set_yticklabels(range(without_instruction_count))
        ax[0].set_xticklabels(range(without_instruction_count+4))

        ax[0].xaxis.tick_top()
        ax[0].xaxis.set_label_position('top')
        ax[0].yaxis.tick_left()

        ax[0].spines['top'].set_visible(False)
        ax[0].spines['right'].set_visible(False)
        ax[0].spines['bottom'].set_visible(False)
        ax[0].spines['left'].set_visible(False)
        ax[0].invert_yaxis()

        ax[1].set_title('Pipelining with Forwarding Path')

        for i in range(len(pipeline_stages)):
            
            for j in range(len(self.with_forwarding_path)):
                if self.with_forwarding_path[j] not in ['RAW','Load-store','Control']:
                    box = plt.Rectangle((i+j, j), 0.4, 0.4, facecolor='lightblue', edgecolor='black')
                    ax[1].add_patch(box)
                    ax[1].text(j + i +0.2, j + 0.2, pipeline_stages[i], ha='center', va='center')
                elif self.with_forwarding_path[j]=='RAW':
                    ax[1].text(j+i+0.2, j+0.2, 'RAW Stall', ha='center', va='center', color='red')
                elif self.with_forwarding_path[j]=='Load-store':
                    ax[1].text(j+i+0.2, j+0.2, 'L-S Stall', ha='center', va='center', color='red')
                elif self.with_forwarding_path[j]=='Control':
                    ax[1].text(j+i+0.2, j+0.2, 'Control Stall', ha='center', va='center', color='red')
               

        ax[1].set_xlabel('Cycle')
        ax[1].set_ylabel('Instruction')
        ax[1].set_xticks(range(with_instruction_count+4))
        ax[1].set_yticks(range(with_instruction_count))
        ax[1].set_yticklabels(range(with_instruction_count))
        ax[1].set_xticklabels(range(with_instruction_count+4))

        ax[1].xaxis.tick_top()
        ax[1].xaxis.set_label_position('top')
        ax[1].yaxis.tick_left()

        ax[1].spines['top'].set_visible(False)
        ax[1].spines['right'].set_visible(False)
        ax[1].spines['bottom'].set_visible(False)
        ax[1].spines['left'].set_visible(False)
        ax[1].invert_yaxis()
        plt.show()

    def run(self, program):
        self.memory[:len(program)] = program

        while self.pc < len(program):
            self.fetch()
            self.decode()
            self.execute()
            self.memory_access()
            self.write_back()
            self.handle_data_hazard()
            self.without_forwarding_path.append(self.pipeline.copy())
            self.with_forwarding_path.append(self.pipeline.copy())
        self.plot_without_forwarding_path()


'''program = ['r000001001010011',  # ADD R1, R2, R3
           'r000010100001011',  # SUB R4, R1, R3
           'i000011110000100',  # Lw R0, 30(R4)
           'i001001010000101',  # Sw R0, 10(R5)
           'r001000000001111',  # BEQ R0,R1,R7
           'r001000000001111']  # BNE R0,R1,R7'''

codes={'ADD':'000001',
         'SUB':'000010',
         'MUL':'000011',
         'DIV':'000100',
         'IDIV':'000101',
         'MOD':'000110',
         'EXP':'000111',
         'BEQ':'001000',
         'BNE':'001001',
         'LW':'00',
         'SW':'01',
         'R1':'001',
         'R2':'010',
         'R3':'011',
         'R4':'100',
         'R5':'101',
         'R6':'110',
         'R7':'111',
         'R0':'000',}


n=int(input("Enter number of istructions : "))

prog=[]

for i in range(n):
    ins_str= ''
    ins=input("Instruction "+str(i+1)+" : ").upper().split(',')
    ins[:1]=ins[0].split()
    if '(' in ins[2]:
        ins[2:3]=ins[2].split('(')
        ins[3]=ins[3][:-1]
        ins[1],ins[2]=ins[2],ins[1]
    ins_str=''.join([codes[j.strip()] if j.strip() in codes else str(bin(int(j.strip())))[-7:] for j in ins ]).replace('b','0')

    if ins[0] in ['LW','SW']:
        ins_str='i'+ins_str
    else:
        ins_str='r'+ins_str
    print(ins_str,ins)
    prog.append(ins_str)
         
processor = PipelineProcessor()
processor.run(prog)
