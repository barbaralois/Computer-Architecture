"""CPU functionality."""
HLT  = 0b00000001
LDI  = 0b10000010
PRN  = 0b01000111
ADD  = 0b10100000
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
SP   = 0b00000111
CALL = 0b01010000
RET  = 0b00010001
CMP  = 0b10100111
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Step 1: Constructor
        self.reg = [0] * 8 # R0 - R7
        self.ram = [0] * 256 #  256 bites memory
        self.pc = 0
        self.fl = 0b00000000 # 00000LGE (less than, greater than, equal)
        self.running = False

        self.branchtable = {
            HLT: self.hlt_instruction,
            LDI: self.ldi_instruction,
            PRN: self.prn_instruction,
            ADD: self.add_instruction,
            MUL: self.mul_instruction,
            PUSH: self.push_instruction,
            POP: self.pop_instruction,
            CALL: self.call_instruction,
            RET: self.ret_instruction,
            CMP: self.cmp_instruction,
            JMP: self.jmp_instruction,
            JEQ: self.jeq_instruction,
            JNE: self.jne_instruction
        }

        # STEP 10 -- stack pointer
        self.reg[SP] = 0xF4

    # Step 2: RAM methods (ram_read & ram_write)
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)
        
        try:
            address = 0
            # open the file (2nd arg)
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    instruction = t[0].strip()
                    # ignore the blank lines
                    if instruction == "":
                        continue
                    
                    try:
                        instruction = int(instruction, 2)
                    except ValueError:
                        print(f"Invalid number '{instruction}")
                        sys.exit(1)

                    self.ram[address] = instruction
                    address += 1
                
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # Step 8: MUL -- multiply
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        # Sprint: CMP -- compare
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            else:
                self.fl = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def add_instruction(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu("ADD", reg_a, reg_b)

        self.pc += 3

    # STEP 8: MUL instruction

    def mul_instruction(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu("MUL", reg_a, reg_b)

        self.pc += 3

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc] # Instruction Register, copy of the currently-executing instruction

            if ir in self.branchtable:
                self.branchtable[ir]()
            else:
                print(f"Unknown instruction {ir}")
                sys.exit(3)

    # Step 4: HLT instruction handler
    def hlt_instruction(self):
        self.running = False

    # Step 5: LDI instruction
    def ldi_instruction(self):
        operand_a = self.ram[self.pc+1]
        operand_b = self.ram[self.pc+2]

        self.reg[operand_a] = operand_b

        self.pc += 3

    # Step 6: PRN instruction
    def prn_instruction(self):
        operand_a = self.ram[self.pc+1]
        print(self.reg[operand_a])
        self.pc += 2 

    def add_instruction(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu("ADD", reg_a, reg_b)

        self.pc += 3

    # STEP 8: MUL instruction

    def mul_instruction(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        self.alu("MUL", reg_a, reg_b)

        self.pc += 3

    # STEP 10: Stack System

    def push_instruction(self):
        # Decrement SP
        self.reg[SP] -= 1

        # Get the reg num to push
        operand_a = self.ram[self.pc + 1]

        # Get the value to push
        operand_b = self.reg[operand_a]

        # Copy the value to the SP address
        top_of_stack_addr = self.reg[SP]
        self.ram[top_of_stack_addr] = operand_b

        self.pc += 2

    def pop_instruction(self):
        # Get reg to pop into
        operand_a = self.ram[self.pc + 1]

        # Get the top of stack addr
        top_of_stack_addr = self.reg[SP]

        # Get the value at the top of the stack
        operand_b = self.ram[top_of_stack_addr]

        # Store the value in the register
        self.reg[operand_a] = operand_b

        # Increment SP
        self.reg[SP] += 1

        self.pc += 2

    # STEP 11: CALL and RET

    def call_instruction(self):
        # Compute return addr
        return_addr = self.pc + 2

        # Push return addr on stack:
        # Decrement SP
        self.reg[SP] -= 1

        # Copy the value to the SP address
        top_of_stack_addr = self.reg[SP]
        self.ram[top_of_stack_addr] = return_addr

        # Get the value from the operand reg
        operand_a = self.ram[self.pc + 1]
        operand_b = self.reg[operand_a]

        # Set the self.pc to that value 
        self.pc = operand_b


    def ret_instruction(self):
        # Compute return addr 
        # Get the top of stack addr
        top_of_stack_addr = self.reg[SP]

        # Get the value at the top of the stack
        value = self.ram[top_of_stack_addr]

        # Increment the SP
        self.reg[SP] += 1

        # and set it to pc
        self.pc = value
    
    # Sprint Tasks
    def cmp_instruction(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3

    def jmp_instruction(self):
        reg_address = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_address]

    def jeq_instruction(self):
        if self.fl == 1:
            self.jmp_instruction()
        else:
            self.pc += 2

    def jne_instruction(self):
        if self.fl != 1:
            self.jmp_instruction()
        else:
            self.pc += 2