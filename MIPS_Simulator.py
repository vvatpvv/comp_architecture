import random
import re
import os
import argparse

# List of instructions in assembly language
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

# Format of instructions in machine code
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


# General functions -------------------------------------------------------------------------------

def bitstring_to_bytes(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def ascii_to_bin(a):
    m = add_bin_length(str(int(bin(ord(a))[2:])), 8)
    return m

def bin_to_int(binary):
    sum = 0
    for i in range(len(binary)):
        if i == 0:
            sum -= 2 ** (len(binary) - i - 1) * int(binary[i])
        else:
            sum += 2 ** (len(binary) - i - 1) * int(binary[i])
    return sum

def int_to_bin(number, length):
    try:
        decimal = int(number)
    except:
        decimal = number
    if "-" in str(decimal):
        binary = str(bin(decimal))[3:]
    else:
        binary = str(bin(decimal))[2:]
    real_length = len(binary)
    if real_length <= length:
        difference = length - real_length
        i = 0
        while i < difference:
            binary = "0" + binary
            i += 1
    else:
        print("Overflow")
    if "-" in str(decimal):
        res = find_comp(binary)
        return res
    else:
        return binary

def find_comp(binary):
    bin_len = len(binary)
    res_st = ""
    for i in range(bin_len):
        if binary[i] == "0":
            res_st += "1"
        elif binary[i] == "1":
            res_st += "0"
    for j in range(bin_len - 1, -1, -1):
        if res_st[j] == "1":
            res_st = res_st[:j] + "0" + res_st[j + 1:]
        elif res_st[j] == "0":
            res_st = res_st[:j] + "1" + res_st[j + 1:]
            break
    return res_st

def add_bin_length(binary_string, length, signed=0):
    if len(binary_string) < length:
        if signed == 0:
            while len(binary_string) < length:
                binary_string = "0" + binary_string
        else:
            binary_string = int_to_bin(bin_to_int(binary_string), length)
    return binary_string

def binary_add(val1, val2, overflow_check, signed=1):
    if len(val1) <= len(val2):
        val1 = add_bin_length(val1, len(val2), signed)
    else:
        val2 = add_bin_length(val2, len(val1), signed)
    res = ""
    carry = "0"
    for i in range(len(val1) - 1, -1, -1):
        temp = [val1[i], val2[i], carry].count("1")
        if temp == 0 or temp == 1:
            carry = "0"
        else:
            carry = "1"
        if temp == 0 or temp == 2:
            res = "0" + res
        else:
            res = "1" + res
    if overflow_check == 1 and val1[0] == val2[0] and res[0] != val1[0]:
        print("Overflow")
    else:
        return res


# Register and memory simulation preparation --------------------------------------------------------------

# Simulates registers
PC = int(hex(0x400000), 16)  # start of text segment
Lo = "0" * 32
Hi = "0" * 32
General_Purpose = []
for i in range(28):
    General_Purpose.append("0" * 32)
General_Purpose.append(int_to_bin(int(hex(0x508000), 16), 32))      # gp
General_Purpose.append(int_to_bin(int(hex(0xA00000), 16), 32))      # sp
General_Purpose.append(int_to_bin(int(hex(0xA00000), 16), 32))      # fp
General_Purpose.append(int_to_bin(int(hex(0x000000), 16), 32))      # ra

# Simulates memory with size 6MB, 1MB for text segments (2^20 bytes)
total_memory_size = 6 * (2 ** 20)
text_memory_size = 2 ** 20  # 1MB for text segments (2^20 bytes)
empty = 4 * (2 ** 20)
memory = []
for i in range(empty + total_memory_size):
    memory.append("")

# Contains line in .in file
inputs = []
current_input_index = 0

# For sbrk
end_of_heap = int(hex(0x400000), 16)


# MIPS functions --------------------------------------------------------------------------------------

def add_function(content):
    General_Purpose[int(content['rd'], 2)] = binary_add(General_Purpose[int(content['rs'], 2)],
                                                        General_Purpose[int(content['rt'], 2)], 1)

def addu_function(content):
    General_Purpose[int(content['rd'], 2)] = binary_add(General_Purpose[int(content['rs'], 2)],
                                                        General_Purpose[int(content['rt'], 2)], 0)

def and_function(content):
    binary_reg1 = ""
    binary_reg2 = General_Purpose[int(content['rs'], 2)]
    binary_reg3 = General_Purpose[int(content['rt'], 2)]
    for i in range(len(binary_reg3)):
        if binary_reg2[i] == "1" and binary_reg3[i] == "1":
            binary_reg1 += "1"
        else:
            binary_reg1 += "0"
    General_Purpose[int(content['rd'], 2)] = binary_reg1

def div_function(content):
    global Hi, Lo
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    divisor = bin_to_int(General_Purpose[int(content['rt'], 2)])
    if divisor == 0:
        print("Zero divisor")
    if (temp1 >= 0 and divisor > 0) or (temp1 <= 0 and divisor < 0):
        quotient = temp1 // divisor
    elif temp1 > 0 and divisor < 0:
        quotient = -(temp1 // (-divisor))
    elif temp1 < 0 and divisor > 0:
        quotient = -((-temp1) // divisor)
    remainder = temp1 - divisor * quotient
    Lo = int_to_bin(quotient, 32)
    Hi = int_to_bin(remainder, 32)

def divu_function(content):
    global Hi, Lo
    temp1 = int(General_Purpose[int(content['rs'], 2)], 2)
    divisor = int(General_Purpose[int(content['rt'], 2)], 2)
    if divisor == 0:
        print("Zero divisor")
    quotient = temp1 // divisor
    remainder = temp1 % divisor
    Lo = int_to_bin(quotient, 32)
    Hi = int_to_bin(remainder, 32)

def jalr_function(content):
    global PC
    General_Purpose[int(content['rd'], 2)] = int_to_bin(PC, 32)
    PC = int(General_Purpose[int(content['rs'], 2)], 2)

def jr_function(content):
    global PC
    PC = int(General_Purpose[int(content['rs'], 2)], 2)

def mult_function(content):
    global Hi, Lo
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    prod = temp1 * temp2
    Hi = int_to_bin(prod, 64)[0:32]
    Lo = int_to_bin(prod, 64)[32:64]

def multu_function(content):
    global Hi, Lo
    temp1 = int(General_Purpose[int(content['rs'], 2)], 2)
    temp2 = int(General_Purpose[int(content['rt'], 2)], 2)
    prod = temp1 * temp2
    Hi = int_to_bin(prod, 64)[0:32]
    Lo = int_to_bin(prod, 64)[32:64]

def mfhi_function(content):
    General_Purpose[int(content['rd'], 2)] = Hi

def mflo_function(content):
    General_Purpose[int(content['rd'], 2)] = Lo

def mthi_function(content):
    global Hi
    Hi = General_Purpose[int(content['rs'], 2)]

def mtlo_function(content):
    global Lo
    Lo = General_Purpose[int(content['rs'], 2)]

def nor_function(content):
    binary_reg1 = ""
    binary_reg2 = General_Purpose[int(content['rs'], 2)]
    binary_reg3 = General_Purpose[int(content['rt'], 2)]
    for i in range(len(binary_reg3)):
        if binary_reg2[i] == "0" and binary_reg3[i] == "0":
            binary_reg1 += "1"
        else:
            binary_reg1 += "0"
    General_Purpose[int(content['rd'], 2)] = binary_reg1

def or_function(content):
    binary_reg1 = ""
    binary_reg2 = General_Purpose[int(content['rs'], 2)]
    binary_reg3 = General_Purpose[int(content['rt'], 2)]
    for i in range(len(binary_reg3)):
        if binary_reg2[i] == "1" or binary_reg3[i] == "1":
            binary_reg1 += "1"
        else:
            binary_reg1 += "0"
    General_Purpose[int(content['rd'], 2)] = binary_reg1

def sll_function(content):
    pos = int(content['shamt'], 2)
    binary_reg = General_Purpose[int(content['rt'], 2)]
    i = 0
    while i < pos:
        binary_reg = binary_reg[1:] + "0"
        i += 1
    General_Purpose[int(content['rd'], 2)] = binary_reg

def sllv_function(content):
    temp = General_Purpose[int(content['rs'], 2)]
    pos = int(temp, 2)
    binary_reg = General_Purpose[int(content['rt'], 2)]
    i = 0
    while i < pos:
        binary_reg = binary_reg[1:] + "0"
        i += 1
    General_Purpose[int(content['rd'], 2)] = binary_reg

def slt_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(General_Purpose[int(content['rt'], 2)])
    if temp1 < temp2:
        General_Purpose[int(content['rd'], 2)] = int_to_bin(1, 32)
    else:
        General_Purpose[int(content['rd'], 2)] = int_to_bin(0, 32)

def sltu_function(content):
    temp1 = int(General_Purpose[int(content['rs'], 2)], 2)
    temp2 = int(General_Purpose[int(content['rt'], 2)], 2)
    if temp1 < temp2:
        General_Purpose[int(content['rd'], 2)] = int_to_bin(1, 32)
    else:
        General_Purpose[int(content['rd'], 2)] = int_to_bin(0, 32)

def sra_function(content):
    pos = int(content['shamt'], 2)
    binary_reg = General_Purpose[int(content['rt'], 2)]
    i = 0
    while i < pos:
        binary_reg = binary_reg[0] + binary_reg[:-1]
        i += 1
    General_Purpose[int(content['rd'], 2)] = binary_reg

def srav_function(content):
    temp = General_Purpose[int(content['rs'], 2)]
    pos = int(temp, 2)
    binary_reg = General_Purpose[int(content['rt'], 2)]
    i = 0
    while i < pos:
        binary_reg = binary_reg[0] + binary_reg[:-1]
        i += 1
    General_Purpose[int(content['rd'], 2)] = binary_reg

def srl_function(content):
    pos = int(content['shamt'], 2)
    binary_reg = General_Purpose[int(content['rt'], 2)]
    i = 0
    while i < pos:
        binary_reg = "0" + binary_reg[:-1]
        i += 1
    General_Purpose[int(content['rd'], 2)] = binary_reg

def srlv_function(content):
    temp = General_Purpose[int(content['rs'], 2)]
    pos = int(temp, 2)
    binary_reg = General_Purpose[int(content['rt'], 2)]
    i = 0
    while i < pos:
        binary_reg = "0" + binary_reg[:-1]
        i += 1
    General_Purpose[int(content['rd'], 2)] = binary_reg

def sub_function(content):
    General_Purpose[int(content['rd'], 2)] = binary_add(General_Purpose[int(content['rs'], 2)],
                                                        find_comp(General_Purpose[int(content['rt'], 2)]), 1)

def subu_function(content):
    General_Purpose[int(content['rd'], 2)] = binary_add(General_Purpose[int(content['rs'], 2)],
                                                        find_comp(General_Purpose[int(content['rt'], 2)]), 0)

def xor_function(content):
    binary_reg1 = ""
    binary_reg2 = General_Purpose[int(content['rs'], 2)]
    binary_reg3 = General_Purpose[int(content['rt'], 2)]
    for i in range(len(binary_reg3)):
        if binary_reg2[i] != binary_reg3[i]:
            binary_reg1 += "1"
        else:
            binary_reg1 += "0"
    General_Purpose[int(content['rd'], 2)] = binary_reg1

def addi_function(content):
    General_Purpose[int(content['rt'], 2)] = binary_add(General_Purpose[int(content['rs'], 2)],
                                                        add_bin_length(content['imm'], 32, 1), 1)

def addiu_function(content):
    General_Purpose[int(content['rt'], 2)] = binary_add(General_Purpose[int(content['rs'], 2)],
                                                        add_bin_length(content['imm'], 32, 1), 0)

def andi_function(content):
    binary_reg1 = ""
    binary_reg2 = General_Purpose[int(content['rs'], 2)]
    binary_imm = add_bin_length(content['imm'], 32)
    for i in range(len(binary_imm)):
        if binary_imm[i] == "1" and binary_reg2[i] == "1":
            binary_reg1 += "1"
        else:
            binary_reg1 += "0"
    General_Purpose[int(content['rt'], 2)] = binary_reg1

def beq_function(content):
    global PC
    if General_Purpose[int(content['rs'], 2)] == General_Purpose[int(content['rt'], 2)]:
        PC += bin_to_int(content['labl']) * 4

def bgez_function(content):
    global PC
    if bin_to_int(General_Purpose[int(content['rs'], 2)]) >= 0:
        PC += bin_to_int(content['labl']) * 4

def bgtz_function(content):
    global PC
    if bin_to_int(General_Purpose[int(content['rs'], 2)]) > 0:
        PC += bin_to_int(content['labl']) * 4

def blez_function(content):
    global PC
    if bin_to_int(General_Purpose[int(content['rs'], 2)]) <= 0:
        PC += bin_to_int(content['labl']) * 4

def bltz_function(content):
    global PC
    if bin_to_int(General_Purpose[int(content['rs'], 2)]) < 0:
        PC += bin_to_int(content['labl']) * 4

def bne_function(content):
    global PC
    if General_Purpose[int(content['rs'], 2)] != General_Purpose[int(content['rt'], 2)]:
        PC += bin_to_int(content['labl']) * 4

def lb_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    General_Purpose[int(content['rt'], 2)] = add_bin_length(memory[address], 32, 1)

def lbu_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    General_Purpose[int(content['rt'], 2)] = add_bin_length(memory[address], 32, 0)

def lh_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    General_Purpose[int(content['rt'], 2)] = add_bin_length((memory[address + 1] + memory[address]), 32, 1)

def lhu_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    General_Purpose[int(content['rt'], 2)] = add_bin_length((memory[address + 1] + memory[address]), 32, 0)

def lui_function(content):
    General_Purpose[int(content['rt'], 2)] = content['imm'] + "0" * 16

def lw_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    General_Purpose[int(content['rt'], 2)] = memory[address + 3] + memory[address + 2] + memory[
        address + 1] + memory[address]

def lwl_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    res_string = ""
    res_string += (General_Purpose[int(content['rt'], 2)][0:8 * ((4 - temp2) - 1)])
    for n in range(temp2 + 1):
        res_string += (memory[temp1 + n])
    General_Purpose[int(content['rt'], 2)] = res_string

def lwr_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    res_string = ""
    added = 0
    for n in range((temp2 // 4) * 4, temp2 + 1):
        res_string += (memory[temp1 + n])
        added += 1
    res_string += (General_Purpose[int(content['rt'], 2)][(8 * added):])
    General_Purpose[int(content['rt'], 2)] = res_string

def swl_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    i = 4 - temp2 - 1
    for j in range(temp2, ((temp2 // 4) + 1) * 4):
        memory[temp1 + i] = General_Purpose[int(content['rt'], 2)][8 * j:8 * (j + 1)]
        i += 1

def swr_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    i = temp2
    for j in range(0, temp2 + 1):
        memory[temp1 + i] = General_Purpose[int(content['rt'], 2)][8 * j:8 * (j + 1)]
        i -= 1

def ori_function(content):
    binary_reg1 = ""
    binary_reg2 = General_Purpose[int(content['rs'], 2)]
    binary_imm = add_bin_length(content['imm'], 32)
    for i in range(len(binary_imm)):
        if binary_imm[i] == "1" or binary_reg2[i] == "1":
            binary_reg1 += "1"
        else:
            binary_reg1 += "0"
    General_Purpose[int(content['rt'], 2)] = binary_reg1

def sb_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    memory[address] = General_Purpose[int(content['rt'], 2)][24:32]

def slti_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    if temp1 < temp2:
        General_Purpose[int(content['rt'], 2)] = int_to_bin(1, 32)
    else:
        General_Purpose[int(content['rt'], 2)] = int_to_bin(0, 32)

def sltiu_function(content):
    temp1 = int(General_Purpose[int(content['rs'], 2)], 2)
    temp2 = int(content['imm'], 2)
    if temp1 < temp2:
        General_Purpose[int(content['rt'], 2)] = int_to_bin(1, 32)
    else:
        General_Purpose[int(content['rt'], 2)] = int_to_bin(0, 32)

def sh_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    memory[address + 1] = General_Purpose[int(content['rt'], 2)][16:24]
    memory[address] = General_Purpose[int(content['rt'], 2)][24:32]

def sw_function(content):
    temp1 = bin_to_int(General_Purpose[int(content['rs'], 2)])
    temp2 = bin_to_int(content['imm'])
    address = temp1 + temp2
    memory[address + 3] = General_Purpose[int(content['rt'], 2)][0:8]
    memory[address + 2] = General_Purpose[int(content['rt'], 2)][8:16]
    memory[address + 1] = General_Purpose[int(content['rt'], 2)][16:24]
    memory[address] = General_Purpose[int(content['rt'], 2)][24:32]

def xori_function(content):
    binary_reg1 = ""
    binary_reg2 = General_Purpose[int(content['rs'], 2)]
    binary_imm = add_bin_length(content['imm'], 32)
    for i in range(len(binary_imm)):
        if binary_imm[i] != binary_reg2[i]:
            binary_reg1 += "1"
        else:
            binary_reg1 += "0"
    General_Purpose[int(content['rt'], 2)] = binary_reg1

def j_function(content):
    global PC
    PC = int(content['targ'], 2) * 4

def jal_function(content):
    global PC
    General_Purpose[31] = int_to_bin(PC, 32)
    PC = int(content['targ'], 2) * 4

def syscall_function():
    global PC
    global inputs, current_input_index
    global out_file
    v0 = int(General_Purpose[2], 2)
    if v0 == 1:
        print(bin_to_int(General_Purpose[4]), end='', flush=True)  # print integer stored in a0 register
        print(bin_to_int(General_Purpose[4]), file=out_file, end='', flush=True)
    elif v0 == 4:
        address = int(General_Purpose[4], 2)
        while memory[address] != "" and memory[address] != "00000000":
            binary_int = int(memory[address], 2)
            print(chr(binary_int), end='', flush=True)
            print(chr(binary_int), file=out_file, end='', flush=True)
            address += 1
    elif v0 == 5:
        integer = inputs[current_input_index]  # input integer from .in file
        current_input_index += 1
        General_Purpose[2] = int_to_bin(integer, 32)  # store in v0 register
    elif v0 == 8:
        string = inputs[current_input_index]  # input string from .in file
        current_input_index += 1
        length = int(General_Purpose[5], 2)
        address = int(General_Purpose[4], 2)
        for i in range(length):
            if i < length - 1:
                if i < len(string):
                    memory[address + i] = int_to_bin(ord(string[i]), 8)  # store the characters to memory
                else:
                    memory[address + i] = ascii_to_bin('\0')
            elif i == length - 1:
                memory[address + i] = ascii_to_bin('\0')
    elif v0 == 9:
        size = int(General_Purpose[4], 2)
        allocate = [1]
        check = [0]
        while check != allocate:
            allocate = []
            check = []
            address = random.randint(9 * (2 ** 20), len(memory) - size)
            for i in range(size):
                check.append("")
                allocate.append(memory[address + i])
        General_Purpose[2] = int_to_bin(address, 32)
    elif v0 == 10:
        out_file.close()
        os._exit(0)  # terminate the program
    elif v0 == 11:
        asc = bin_to_int(General_Purpose[4])
        character = chr(asc)
        print(character, end='', flush=True)  # print character stored in a0 register
        print(character, file=out_file, end='', flush=True)
    elif v0 == 12:
        character = inputs[current_input_index]  # character from .in file
        current_input_index += 1
        asc = ord(character)
        General_Purpose[2] = int_to_bin(asc, 32)
    elif v0 == 13:
        address = int(General_Purpose[4], 2)
        f_name = ""
        while memory[address] != "" and memory[address] != "00000000":
            binary_int = int(memory[address], 2)
            f_name += chr(binary_int)
            address += 1
        if os.path.isfile(f_name[1:]):
            a = 1
        else:
            temp = os.open(f_name[1:], os.O_CREAT)
            os.close(temp)
        fd = os.open(f_name[1:], os.O_RDWR)
        General_Purpose[4] = int_to_bin(fd, 32)
    elif v0 == 14:
        fd = int(General_Purpose[4], 2)
        buffer = int(General_Purpose[5], 2)
        length = int(General_Purpose[6], 2)
        cont = os.read(fd, length)
        for de in cont:
            memory[buffer] = int_to_bin(de, 8)
            buffer += 1
        General_Purpose[4] = int_to_bin(length, 32)
    elif v0 == 15:
        fd = int(General_Purpose[4], 2)
        buffer = int(General_Purpose[5], 2)
        length = int(General_Purpose[6], 2)
        char_count = 0
        for i in range(buffer, buffer + length):
            part = memory[i]
            if part == "" or part == "00000000":
                val = (bytes('\0', 'utf-8'))
                os.write(fd, val)
                char_count += 1
            else:
                val = bitstring_to_bytes(part)
                os.write(fd, val)
                char_count += 1
        General_Purpose[4] = int_to_bin(char_count, 32)
    elif v0 == 16:
        fd = int(General_Purpose[4], 2)
        os.close(fd)
    elif v0 == 17:
        out_file.close()
        os._exit(0)  # terminate the program


# Parse command, get inputs from .in file and get checkpoints -----------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument(dest='MIPS_filename', type=str)
parser.add_argument(dest='filename', type=str)
parser.add_argument(dest='Checkpoint_filename', type=str)
parser.add_argument(dest='In_filename', type=str)
parser.add_argument(dest='Out_filename', type=str)
args = parser.parse_args()
MIPS_file = open(args.MIPS_filename, 'r')
binary_file = open(args.filename, 'r')
checkpoint_file = open(args.Checkpoint_filename, 'r')
in_file = open(args.In_filename, 'r')
out_file = open(args.Out_filename, 'w')

for lin in in_file:
    lin = lin.replace("\n", "")
    inputs.append(lin)

checkpoints = []
for line in checkpoint_file:
    line = line.replace("\n", "").replace("\t", "").replace(" ", "")
    checkpoints.append(int(line))
checkpoints.sort()


# Append static data segment ------------------------------------------------------------------

loc = int(hex(0x500000), 16)  # location (hex(0x500000), 16) is start of static data
text_segment = 0
dump = []

for line in MIPS_file:
    line = line.split('#')[0]  # Removes comments
    content = ""
    if line == "":
        continue
    if '.text' in line:
        text_segment = 1
    if text_segment == 0:
        if "asciiz" in line:
            content = re.findall('"([^"]*)"', line)[0].replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
            content += "\0"
            parts = len(content) // 4
            remainder = len(content) % 4
            if remainder != 0:
                parts += 1
                content += '\0' * (4 - remainder)
            for part in range(parts):
                memory[loc] = ascii_to_bin(content[4 * part])
                memory[loc + 1] = ascii_to_bin(content[(4 * part) + 1])
                memory[loc + 2] = ascii_to_bin(content[(4 * part) + 2])
                memory[loc + 3] = ascii_to_bin(content[(4 * part) + 3])
                loc += 4
        elif "ascii" in line:
            content = re.findall('"([^"]*)"', line)[0].replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
            parts = len(content) // 4
            remainder = len(content) % 4
            if remainder != 0:
                parts += 1
                content += '\0' * (4 - remainder)
            for part in range(parts):
                memory[loc] = ascii_to_bin(content[4 * part])
                memory[loc + 1] = ascii_to_bin(content[(4 * part) + 1])
                memory[loc + 2] = ascii_to_bin(content[(4 * part) + 2])
                memory[loc + 3] = ascii_to_bin(content[(4 * part) + 3])
                loc += 4
        elif "word" in line:
            temp = line.split()
            con = []
            for i in range(len(temp)):
                if temp[i] == ".word":
                    s = ''
                    i += 1
                    while i != len(temp):
                        s += temp[i].replace(" ", "")
                        i += 1
                    con = s.split(',')
            for w in range(len(con)):
                append_count = 0
                comp = int_to_bin(con[w], 8)
                par = (len(comp) // 8) + 1
                rem = len(comp) % 8
                for i in range(par):
                    if i == par - 1:
                        if rem != 0:
                            memory[loc] = add_bin_length(comp[:rem], 8)
                            loc += 1
                            append_count += 1
                    else:
                        memory[loc] = comp[(len(comp)-8*i-8):(len(comp)-8*i)]
                        loc += 1
                        append_count += 1
                while append_count != 4:
                    memory[loc] = ascii_to_bin('\0')
                    loc += 1
                    append_count += 1
        elif "byte" in line:
            temp = line.split()
            con = []
            for i in range(len(temp)):
                if temp[i] == ".byte":
                    s = ''
                    i += 1
                    while i != len(temp):
                        s += temp[i].replace(" ", "")
                        i += 1
                    con = s.split(',')
            for i in range(len(con)):
                memory[loc] = int_to_bin(con[i], 8)
                loc += 1
            rem = len(con) % 4
            if rem != 0:
                ap = 4 - rem
                for i in range(ap):
                    memory[loc] = ascii_to_bin('\0')
                    loc += 1
        elif "half" in line:
            temp = line.split()
            con = []
            for i in range(len(temp)):
                if temp[i] == ".half":
                    s = ''
                    i += 1
                    while i != len(temp):
                        s += temp[i].replace(" ", "")
                        i += 1
                    con = s.split(',')
            for i in range(len(con)):
                b = int_to_bin(con[i], 8)
                memory[loc] = b[len(b) - 8:len(b)]
                if len(b) > 8:
                    memory[loc + 1] = add_bin_length(int_to_bin(con[i], 8)[:len(b) - 8], 8)
                else:
                    memory[loc + 1] = ascii_to_bin('\0')
                loc += 2
            rem = len(con) % 4
            if rem == 1:
                memory[loc] = ascii_to_bin('\0')
                memory[loc + 1] = ascii_to_bin('\0')
                loc += 2


# Append text data segment ------------------------------------------------------------------

location = int(hex(0x400000), 16)  # Equivalent location to int(hex(0x400000), 16), start of text segment
for line in binary_file:
    line = line.replace("\n", "").replace("\t", "").replace(" ", "")
    if line == "":
        continue
    elif len(line) != 32:
        print('Line is not binary of length 32')
        break
    else:
        for i in range(4):
            memory[location + i] = line[(8 * i):(8 * (i + 1))]
    location += 4


# Simulate instructions and create checkpoints files -------------------------------------------------------

current_loop_count = 0
while True:
    if current_loop_count in checkpoints:
        f = open('memory_' + str(current_loop_count) + '.bin', 'wb')
        start = int(hex(0x400000), 16)
        stop = len(memory)
        for i in range(start, stop, 4):
            if i < int(hex(0x500000), 16):
                temp = [memory[i + 3], memory[i + 2], memory[i + 1], memory[i]]
            else:
                temp = [memory[i], memory[i + 1], memory[i + 2], memory[i + 3]]
            for part in temp:
                if part == "" or part == "00000000":
                    f.write(bytes('\0', 'utf-8'))
                else:
                    value = bitstring_to_bytes(part)
                    f.write(value)
        f.close()

        reg_checkpt = open('register_' + str(current_loop_count) + '.bin', 'wb')
        for reg in General_Purpose:
            for j in range(4):
                i = 3 - j
                v = reg[8 * i: 8 * (i + 1)]
                if v == "" or v == "00000000":
                    reg_checkpt.write(bytes('\0', 'utf-8'))
                else:
                    value = bitstring_to_bytes(v)
                    reg_checkpt.write(value)
        temp_num = PC
        temp_PC = int_to_bin(temp_num, 32)
        for j in range(4):
            i = 3 - j
            v = temp_PC[8 * i: 8 * (i + 1)]
            if v == "" or v == "00000000":
                reg_checkpt.write(bytes('\0', 'utf-8'))
            else:
                value = bitstring_to_bytes(v)
                reg_checkpt.write(value)
        for j in range(4):
            i = 3 - j
            v = Hi[8 * i: 8 * (i + 1)]
            if v == "" or v == "00000000":
                reg_checkpt.write(bytes('\0', 'utf-8'))
            else:
                value = bitstring_to_bytes(v)
                reg_checkpt.write(value)
        for j in range(4):
            i = 3 - j
            v = Lo[8 * i: 8 * (i + 1)]
            if v == "" or v == "00000000":
                reg_checkpt.write(bytes('\0', 'utf-8'))
            else:
                value = bitstring_to_bytes(v)
                reg_checkpt.write(value)
        reg_checkpt.close()

    if memory[PC] == "":
        break
    memory_line = memory[PC] + memory[PC + 1] + memory[PC + 2] + memory[PC + 3]
    content = {}
    opcode = memory_line[0:6]
    opcode_hex = hex(int(opcode, 2))[2:]  # convert the opcode to hex
    if opcode_hex == '0':  # if opcode is 0, instructions is R-type
        function = memory_line[26:33]
        function_hex = hex(int(function, 2))[2:]
        for i in range(0, 27):  # use function (6 last bit) to determine the instruction
            function_opcode = translations[i].split(" ")[-1]
            if function_opcode == function_hex:
                content['instruction'] = instructions[i]  # the corresponding R-type instruction
                trans_list = translations[i].split(" ")
                for ind in range(len(trans_list)):
                    if trans_list[ind] == "rs" or trans_list[ind] == "rt" or \
                            trans_list[ind] == "rd" or trans_list[ind] == "shamt":
                        content[trans_list[ind]] = memory_line[(ind * 5) + 1:(ind * 5) + 6]
    else:
        for i in range(27, len(translations)):  # use opcode to find the instruction (I or J-type)
            trans_opcode = translations[i].split(" ")[0]
            if trans_opcode == opcode_hex:
                content['instruction'] = instructions[i]  # the corresponding I or J-type instruction
                trans_list = translations[i].split(" ")
                if (i >= 27) and (i <= 52):
                    for ind in range(len(trans_list)):
                        if trans_list[ind] == "rs" or trans_list[ind] == "rt":
                            content[trans_list[ind]] = memory_line[(ind * 5) + 1:(ind * 5) + 6]
                        elif trans_list[ind] == "labl" or trans_list[ind] == "imm":
                            content[trans_list[ind]] = memory_line[16:32]
                elif (i >= 53) and (i <= 54):
                    for ind in range(len(trans_list)):
                        if trans_list[ind] == "targ":
                            content[trans_list[ind]] = memory_line[6:32]
    PC += 4

    if content['instruction'] == 'add':
        add_function(content)
    elif content['instruction'] == 'addu':
        addu_function(content)
    elif content['instruction'] == 'and':
        and_function(content)
    elif content['instruction'] == 'div':
        div_function(content)
    elif content['instruction'] == 'divu':
        divu_function(content)
    elif content['instruction'] == 'jalr':
        jalr_function(content)
    elif content['instruction'] == 'jr':
        jr_function(content)
    elif content['instruction'] == 'mfhi':
        mfhi_function(content)
    elif content['instruction'] == 'mflo':
        mflo_function(content)
    elif content['instruction'] == 'mthi':
        mthi_function(content)
    elif content['instruction'] == 'mtlo':
        mtlo_function(content)
    elif content['instruction'] == 'mult':
        mult_function(content)
    elif content['instruction'] == 'multu':
        multu_function(content)
    elif content['instruction'] == 'nor':
        nor_function(content)
    elif content['instruction'] == 'or':
        or_function(content)
    elif content['instruction'] == 'sll':
        sll_function(content)
    elif content['instruction'] == 'sllv':
        sllv_function(content)
    elif content['instruction'] == 'slt':
        slt_function(content)
    elif content['instruction'] == 'sltu':
        sltu_function(content)
    elif content['instruction'] == 'sra':
        sra_function(content)
    elif content['instruction'] == 'srav':
        srav_function(content)
    elif content['instruction'] == 'srl':
        srl_function(content)
    elif content['instruction'] == 'srlv':
        srlv_function(content)
    elif content['instruction'] == 'sub':
        sub_function(content)
    elif content['instruction'] == 'subu':
        subu_function(content)
    elif content['instruction'] == 'syscall':
        syscall_function()
    elif content['instruction'] == 'xor':
        xor_function(content)

    elif content['instruction'] == 'addi':
        addi_function(content)
    elif content['instruction'] == 'addiu':
        addiu_function(content)
    elif content['instruction'] == 'andi':
        andi_function(content)
    elif content['instruction'] == 'beq':
        beq_function(content)
    elif content['instruction'] == 'bgez':
        bgez_function(content)
    elif content['instruction'] == 'bgtz':
        bgtz_function(content)
    elif content['instruction'] == 'blez':
        blez_function(content)
    elif content['instruction'] == 'bltz':
        bltz_function(content)
    elif content['instruction'] == 'bne':
        bne_function(content)
    elif content['instruction'] == 'lb':
        lb_function(content)
    elif content['instruction'] == 'lbu':
        lbu_function(content)
    elif content['instruction'] == 'lh':
        lh_function(content)
    elif content['instruction'] == 'lhu':
        lhu_function(content)
    elif content['instruction'] == 'lui':
        lui_function(content)
    elif content['instruction'] == 'lw':
        lw_function(content)
    elif content['instruction'] == 'ori':
        ori_function(content)
    elif content['instruction'] == 'sb':
        sb_function(content)
    elif content['instruction'] == 'slti':
        slti_function(content)
    elif content['instruction'] == 'sltiu':
        sltiu_function(content)
    elif content['instruction'] == 'sh':
        sh_function(content)
    elif content['instruction'] == 'sw':
        sw_function(content)
    elif content['instruction'] == 'xori':
        xori_function(content)
    elif content['instruction'] == 'lwl':
        lwl_function(content)
    elif content['instruction'] == 'lwr':
        lwr_function(content)
    elif content['instruction'] == 'swl':
        swl_function(content)
    elif content['instruction'] == 'swr':
        swr_function(content)

    elif content['instruction'] == 'j':
        j_function(content)
    elif content['instruction'] == 'jal':
        jal_function(content)

    current_loop_count += 1

# End of Assignment 2 (118010502 Agnes Valencia)