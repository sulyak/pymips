#!/bin/python
import sys
import struct
import parser

reg_names = ["$zero", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3", "$t0",
             "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$s0", "$s1",
             "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$t8", "$t9", "$k0",
             "$k1", "$gp", "$sp", "$fp", "$ra"]

reg = dict()
for i, reg_name in enumerate(reg_names):
    reg[reg_name] = i


def main(input_file, output_file, is_text):
    with open(input_file, "r") as f:
        lines = f.readlines()

    labels = parser.parse_labels(lines)
    lines = parser.remove_labels(lines)

    if is_text: file_mode = "w"
    else: file_mode = "wb"
    with open(output_file, file_mode) as f:
        for i, line in enumerate(lines):
            instruction, args = parser.parse_line(line)

            if instruction_type(instruction) == "r":
                result = make_r(instruction, args)
            elif instruction_type(instruction) == "i":
                result = make_i(instruction, args, i, labels)
            elif instruction_type(instruction) == "j":
                result = make_j(instruction, args, labels)
            else:
                sys.stderr.write(f"instruction {instruction} not supported\n")
                sys.exit(1)

            if is_text:
                f.write(result + "\n")
            else:
                f.write(struct.pack("<I", int(result, 2)))


def make_r(ins, args):
    funct = {
            "add": 0x20,
            "and": 0x24,
            "jr": 0x8,
            "or": 0x25,
            "sub": 0x22, "sll": 0x0,
            "srl": 0x2
            }

    # opcode is 0 for every r instruction
    result = "000000"

    if ins == 'jr':
        rs, = args
        result += int2bin(reg[rs], num_bits=5)
        result += "0" * 15

    elif ins in ['sll', 'srl']:
        rd, rt, sa = args
        result += "00000"
        result += int2bin(reg.get(rt, rt), num_bits=5)
        result += int2bin(reg.get(rd, rd), num_bits=5)
        result += int2bin(reg.get(sa, sa), num_bits=5)

    else:
        rd, rs, rt = args
        result += int2bin(reg.get(rs, rs), num_bits=5)
        result += int2bin(reg.get(rt, rt), num_bits=5)
        result += int2bin(reg.get(rd, rd), num_bits=5)
        result += "00000"

    result += int2bin(funct[ins], num_bits=6)
    return result


def make_i(ins, args, current_line, labels):
    opcode = {
            "addi": 0x8,
            "beq": 0x4,
            "bne": 0x5,
            "lw": 0x23,
            "sw": 0x2b
            }

    # get opcode
    result = int2bin(opcode[ins], num_bits=6)

    # args can be label, so get(rx, rx) is necessary
    rs, rt, imm = args
    result += int2bin(reg.get(rt, rt), num_bits=5)
    result += int2bin(reg.get(rs, rs), num_bits=5)

    if imm not in labels:
        result += twos_comp(int(imm), 16)
    else:
        origin = current_line + 1
        target = labels[imm]
        jump = target - origin

        result += twos_comp(jump, 16)

    return result


def make_j(ins, args, labels):
    opcode = {
            "j": 0x2,
            "jal": 0x3
            }
    # get opcode
    result = int2bin(opcode[ins], num_bits=6)

    # check if target argument is a label
    target, = args
    if target in labels:
        target = labels[target]

    result += int2bin(target, num_bits=26)
    return result


def instruction_type(instruction):
    if instruction in ["add", "and", "jr", "or", "sll", "srl", "sub"]:
        return 'r'
    elif instruction in ["addi", "beq", "bne", "lw", "sw"]:
        return 'i'
    elif instruction in ["j", "jal"]:
        return 'j'
    return None


def int2bin(value, num_bits):
    """
    returns a num_bits-binary number represented as a string (w/o 0b)
    """
    return bin(int(value))[2:].rjust(num_bits, "0")


def twos_comp(val: int, num_bits):
    if val < 0:
        val += 2**num_bits
    return bin(val)[2:].rjust(num_bits, "0")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write(f"usage: {sys.argv[0]} input_file [--text] -o output_file\n")
        sys.exit(1)

    is_text = "--text" in sys.argv
    input_file = sys.argv[1]
    if "-o" in sys.argv:
        output_file = sys.argv[sys.argv.index("-o") + 1]
    else:
        output_file = "a.txt" if is_text else "a.bin"
    main(input_file, output_file, is_text)
