import re
import os

# List of instructions that can be translated
# Index: R = 0 to 26, I = 27 to 52, J = 53 to 54
instructions = [
    "add", "addu", "and",
    "div", "divu", "jalr", "jr",
    "mfhi", "mflo", "mthi", "mtlo",
    "mult", "multu", "nor", "or",
    "sll", "sllv", "slt", "sltu",
    "sra", "srav", "srl", "srlv",
    "sub", "subu", "syscall",
    "xor",

    "addi", "addiu", "andi",
    "beq", "bgez", "bgtz", "blez",
    "bltz", "bne", "lb", "lbu",
    "lh", "lhu", "lui", "lw",
    "ori", "sb", "slti", "sltiu",
    "sh", "sw", "xori",
    "lwl", "lwr", "swl", "swr",

    "j", "jal",
    ]

# List of how the instructions are formatted in assembly language
instructions_formats = [
    "add rd rs rt", "addu rd rs rt", "and rd rs rt",
    "div rs rt", "divu rs rt", "jalr rs rd", "jr rs",
    "mfhi rd", "mflo rd", "mthi rs", "mtlo rs",
    "mult rs rt ", "multu rs rt", "nor rd rs rt", "or rd rs rt",
    "sll rd rt shamt", "sllv rd rt rs", "slt rd rs rt", "sltu rd rs rt",
    "sra rd rt shamt", "srav rd rt rs",   "srl rd rt shamt", "srlv rd rt rs",
    "sub rd rs rt", "subu rd rs rt", "syscall",
    "xor rd rs rt",

    "addi rt rs imm", "addiu rt rs imm", "andi rt rs imm",
    "beq rs rt label", "bgez rs label", "bgtz rs label", "blez rs label",
    "bltz rs label", "bne rs rt label", "lb rt address", "lbu rt address",
    "lh rt address", "lhu rt address", "lui rt imm", "lw rt address",
    "ori rt rs imm", "sb rt address", "slti rt rs imm", "sltiu rt rs imm",
    "sh rt address", "sw rt address", "xori rt rs imm",
    "lwl rt address", "lwr rt address", "swl rt address", "swr rt address",

    "j target", "jal target",
    ]

# List of how to translate each instruction
# Instructions and their translations are at the same index
translations = [
    "0 rs rt rd 0 20", "0 rs rt rd 0 21", "0 rs rt rd 0 24",
    "0 rs rt 0 0 1a", "0 rs rt 0 0 1b", "0 rs 0 rd 0 9", "0 rs 0 0 0 8",
    "0 0 0 rd 0 10", "0 0 0 rd 0 12", "0 rs 0 0 0 11", "0 rs 0 0 0 13",
    "0 rs rt 0 0 18", "0 rs rt 0 0 19", "0 rs rt rd 0 27", "0 rs rt rd 0 25",
    "0 rs rt rd shamt 0", "0 rs rt rd 0 4", "0 rs rt rd 0 2a", "0 rs rt rd 0 2b",
    "0 rs rt rd shamt 3", "0 rs rt rd 0 7", "0 rs rt rd shamt 2", "0 rs rt rd 0 6",
    "0 rs rt rd 0 22", "0 rs rt rd 0 23", "0 0 0 0 0 c",
    "0 rs rt rd 0 26",

    "8 rs rt imm", "9 rs rt imm", "c rs rt imm",
    "4 rs rt labl", "1 rs 1 labl", "7 rs 0 labl", "6 rs 0 labl",
    "1 rs 0 labl", "5 rs rt labl", "20 rs rt imm", "24 rs rt imm",
    "21 rs rt imm", "25 rs rt imm", "f 0 rt imm", "23 rs rt imm",
    "d rs rt imm", "28 rs rt imm", "a rs rt imm", "b rs rt imm",
    "29 rs rt imm", "2b rs rt imm", "e rs rt imm",
    "22 rs rt imm", "26 rs rt imm", "2a rs rt imm", "2e rs rt imm",

    "2 targ", "3 targ",
    ]

# List of register names
# Index corresponds to register number
register_names = [
    "$zero", "$at", "$v0", "$v1", "$a0", "$a1",
    "$a2", "$a3", "$t0", "$t1", "$t2", "$t3",
    "$t4", "$t5", "$t6", "$t7", "$s0", "$s1",
    "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
    "$t8", "$t9", "$k0", "$k1", "$gp", "$sp",
    "$fp", "$ra",
    ]

def Parse_Instructions(tokens):
    if ':' in tokens[0] and len(tokens) == 1:
        return '0'      # Returns 0 if there is only label but no instructions
    final_list = tokens
    if ':' in tokens[0]:        # Removes label
        final_list = tokens[1:]
    for ind in range(len(instructions)):
        if instructions[ind] == final_list[0]:      # Find a match from the instructions list
            information = instructions_formats[ind].split()
            parsed_dict = {}
            for i in range(len(information)):
                if i == 0:
                    parsed_dict['index'] = ind      # Appends dictionary with the index of the instruction
                    parsed_dict['operation'] = information[i]
                else:
                    parsed_dict[information[i]] = final_list[i]
                    if information[i] == 'address':
                        # Splits address in the form of imm(rs) into imm and rs, and place them in the final dictionary
                        tem = re.split(r'(?:via|[\(\)])+', final_list[i])
                        parsed_dict['imm'] = tem[0]
                        parsed_dict['rs'] = tem[1]
            return parsed_dict
    return '0'      # Returns 0 if the operation is not found in the instructions list

def Assemble(index, final_string):
    binary_string = ''
    if (index >= 0) and (index <= 26):  # R-type instructions
        bin_length = [6, 5, 5, 5, 5, 6]
        for elem in range(len(final_string)):
            if (elem == 0) or (elem == 5):  # Hexadecimal to binary for the opcode, function
                scale = 16
                num_of_bits = bin_length[elem]
                binary_string += bin(int(final_string[elem], scale))[2:].zfill(num_of_bits)
            else:  # Decimal to binary for the rs, rt, rd, sa
                num_of_bits = bin_length[elem]
                binary_string += bin(int(final_string[elem], 10))[2:].zfill(num_of_bits)
    elif (index >= 27) and (index <= 52):  # I-type instructions
        bin_length = [6, 5, 5, 16]
        for elem in range(len(final_string)):
            if elem == 0:  # Hexadecimal to binary for the opcode(6)
                binary_string += bin(int(final_string[elem], 16))[2:].zfill(6)
            else:  # Decimal to binary for the rs, rt, imm
                scale = 10
                num_of_bits = bin_length[elem]
                if '-' in final_string[elem]:  # Find the complement for negative integers
                    val = final_string[elem][1:]
                    initial = bin(int(final_string[elem], scale) + 1)[2:].zfill(num_of_bits)
                    complement = ''
                    for dig in initial:
                        if dig == '1':
                            complement += '0'
                        else:
                            complement += '1'
                    binary_string += complement
                else:
                    binary_string += bin(int(final_string[elem], scale))[2:].zfill(num_of_bits)
    elif (index >= 53) and (index <= 54):  # J-type instructions
        for elem in range(len(final_string)):
            if elem == 0:  # Hexadecimal to binary for the opcode(6)
                binary_string += bin(int(final_string[elem], 16))[2:].zfill(6)
            elif elem == 1:  # Decimal to binary for the target(26)
                binary_string += bin(int(final_string[elem], 10))[2:].zfill(26)
    return binary_string


# Phase 1 (Parse instructions, Get labels) -----------------------------------------------------------

filename = input('Enter assembly text file name (Must be in same folder): ')
while not os.path.exists(filename):
    filename=input("Your input is wrong, please enter the correct name: ")
assembly_file = open(filename, 'r')

Labels = {}         # Stores address of labels
All_Lines = []
Text_Lines = []     # Stores MIPS code under .text
text_segment = 0
Memory = []         # Stores dictionary of parsed instructions

line_address = int(hex(0x400000), 16)
for line in assembly_file:
    line = line.replace("\n", "").replace("\t", "")
    if line == "":
        continue
    final_line = line.split('#')[0]      # Removes comments
    All_Lines.append(final_line)
    if text_segment == 1:
        Text_Lines.append(line)
        tokens = re.split(r'(?:via|[ ,])+', final_line)     # Splits line by spaces and commas
        final_tokens = []
        for string in tokens:
            if string != '':    # Removes empty string from list
                final_tokens.append(string)
        parsed_line = Parse_Instructions(final_tokens)      # Parse the instructions
        if ':' in line:
            label = line.split(':')[0]
            label_index = line_address
            Labels[label] = label_index     # Stores index of labels
        if parsed_line != '0':
            Memory.append(parsed_line)      # Stores parsed instructions to a list
            line_address += 4
    if '.text' in line:
        text_segment = 1


# Phase 2 (Assemble to machine code) ------------------------------------------------------------------

output_name = input('Enter output file name (eg: my_output.txt): ')
output_file = open(output_name, 'w', encoding="utf-8")
PC = int(hex(0x400000), 16)     # Initial address is set to 0x40000
for dic in Memory:
    if dic == {}:
        continue
    else:
        PC += 4
        index = dic['index']
        wanted_string = translations[index].split()
        final_string = []
        for comp in wanted_string:
            if comp == 'rs' or comp == 'rt' or comp == 'rd':
                for name_index in range(len(register_names)):
                    if register_names[name_index] == dic[comp]:
                        final_string.append(str(name_index))        # Covert to register number (index at register list)
            elif comp == 'shamt' or comp == 'imm':
                final_string.append(dic[comp])
            elif comp == 'labl':
                # Take the signed difference between the address of the following instruction and target label
                # Drop the two low order bits
                difference = (Labels[dic['label']] - PC) / 4
                final_string.append(str(int(difference)))
            elif comp == 'targ':
                adr = str(Labels[dic['target']])
                adr = bin(int(adr, 10))[2:].zfill(32)
                adr = adr[4:]
                adr = int(adr, 2)
                adr = int(adr / 4)
                final_string.append(str(adr))
            else:
                final_string.append(comp)

        binary_string = Assemble(index, final_string)
        print(binary_string, file=output_file)

output_file.close()