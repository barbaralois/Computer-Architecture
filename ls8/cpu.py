"""CPU functionality."""
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Step 1: Constructor
        self.reg = [0] * 8 # R0 - R7
        self.ram = [0] * 256 #  256 bites memory
        self.pc = 0

        self.running = False

        self.branchtable = {}
        self.branchtable[HLT] = self.hlt_instruction
        self.branchtable[LDI] = self.ldi_instruction
        self.branchtable[PRN] = self.prn_instruction
        self.branchtable[ADD] = self.add_instruction
        self.branchtable[MUL] = self.mul_instruction

    # Step 2: RAM methods (ram_read & ram_write)
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    # def load(self):
    #     """Load a program into memory."""

    #     address = 0

    #     # For now, we've just hardcoded a program:

    #     program = [
    #         # From print8.ls8
    #         0b10000010, # LDI R0,8
    #         0b00000000,
    #         0b00001000,
    #         0b01000111, # PRN R0
    #         0b00000000,
    #         0b00000001, # HLT
    #     ]

    #     for instruction in program:
    #         self.ram[address] = instruction
    #         address += 1

    def load(self):
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)
        
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    instruction = t[0].strip()
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
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
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

    # Step 3: run() method
    # def run(self):
    #     """Run the CPU."""
    #     self.running = True

    #     while self.running:
    #         ir = self.ram[self.pc] # Instruction Register, copy of the currently-executing instruction

    #         if ir == 0b00000001: # HLT - Halt
    #             self.hlt_instruction()

    #         elif ir == 0b10000010: # SAVE_REG - Adding
    #             operand_a = self.ram[self.pc+1]
    #             operand_b = self.ram[self.pc+2]
    #             self.reg[operand_a] = operand_b
    #             # print(self.reg)
    #             self.pc += 3

    #         elif ir == 0b01000111: # PRINT_REG
    #             operand_a = self.ram[self.pc+1]
    #             print(self.reg[operand_a])
    #             self.pc += 2

    #         else:
    #             print(f"Unknown instrution {ir}")

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc] # Instruction Register, copy of the currently-executing intruction

            if ir in self.branchtable:
                self.branchtable[ir]()
            else:
                print(f"Unknown instrution {ir}")

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
