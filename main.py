#!/bin/python
import sys
import struct

output_file = "a.bin"

reg_names = ["$zero", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3", "$t0",
             "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$s0", "$s1",
             "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$t8", "$t9", "$k0",
             "$k1", "$gp", "$sp", "$fp", "$ra"]

reg = dict()
for i, reg_name in enumerate(reg_names):
    reg[reg_name] = i


def main():
    with open("exemplo.asm", "r") as f:
        lines = f.readlines()

    labels = parse_labels(lines)
    lines = remove_labels(lines)

    with open(output_file, "wb") as f:
        for i, line in enumerate(lines):
            instruction, args = parse_line(line)
            print(instruction, args)

            if instruction_type(instruction) == "r":
                result = make_r(instruction, args)
            elif instruction_type(instruction) == "i":
                result = make_i(instruction, args, i, labels)
            elif instruction_type(instruction) == "j":
                result = make_j(instruction, args, labels)
            else:
                sys.stderr.write(f"instruction {instruction} not supported\n")
                sys.exit(1)

            if result:
                f.write(struct.pack("<I", int(result, 2)))
            print(result)
            print()

    print(labels)


def make_r(ins, args):
    result = "000000"
    args = list(map(lambda x: x if x in reg.keys() else int(x), args))

    if ins == 'jr':
        rs, = args
        result += bin(reg[rs])[2:].rjust(5, '0')
        result += "0" * 15
        result += "001000"
        return result

    if ins in ['sll', 'srl']:
        rd, rs, sa = args
        result += "00000"
        result += bin(reg.get(rs, rs))[2:].rjust(5, '0')
        result += bin(reg.get(rd, rd))[2:].rjust(5, '0')
        result += bin(reg.get(sa, sa))[2:].rjust(5, '0')

        funct = {'sll': 0x0, 'srl': 0x2}
        result += bin(funct[ins])[2:].rjust(6, '0')
        return result

    rd, rs, rt = args
    result += bin(reg.get(rs, rs))[2:].rjust(5, '0')
    result += bin(reg.get(rt, rt))[2:].rjust(5, '0')
    result += bin(reg.get(rd, rd))[2:].rjust(5, '0')
    result += "00000"

    funct = {
            "add": 0x20,
            "and": 0x24,
            "jr": 0x8,
            "or": 0x25,
            "sub": 0x22,
            "sll": 0x0,
            "srl": 0x2
            }

    result += bin(funct[ins])[2:].rjust(6, '0')
    return result


def make_i(ins, args, current_line, labels):
    opcode = {
            "addi": 0x8,
            "beq": 0x4,
            "bne": 0x5,
            "lw": 0x23,
            "sw": 0x2b
            }
    result = ""
    result += bin(opcode[ins])[2:].rjust(6, '0')

    rs, rt, imm = args
    result += bin(reg.get(rt, rt))[2:].rjust(5, '0')
    result += bin(reg.get(rs, rs))[2:].rjust(5, '0')

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
    result = bin(opcode[ins])[2:].rjust(6, "0")
    target, = args
    if target in labels:
        target = labels[target]
    result += bin(target)[2:].rjust(26, "0")
    return result


def parse_labels(lines):
    labels = {}
    for count, line in enumerate(lines):
        if ":" in line:
            label_name = line.split(":")[0]
            labels[label_name.lower()] = count
    return labels


def remove_labels(lines):
    result = []
    for line in lines:
        if ":" in line:
            result += [line.split(":")[1].strip()]
        else:
            result += [line]
    return result


def parse_line(line):
    instruction = line.split(" ")[0].lower()
    args = ''.join(line.split(" ")[1:])
    args = args.strip().split(",")
    args = list(map(str.lower, args))
    for arg in reversed(args):
        if "(" in arg:
            offset, reg = arg.split("(")
            reg = reg.replace(")", "")
            args.remove(arg)
            args += [reg, offset]

    return instruction, args


def instruction_type(instruction):
    if instruction in ["add", "and", "jr", "or", "sll", "srl", "sub"]:
        return 'r'
    elif instruction in ["addi", "beq", "bne", "lw", "sw"]:
        return 'i'
    elif instruction in ["j", "jal"]:
        return 'j'
    return None


def twos_comp(val: int, bits):
    if val < 0:
        val += 2**bits
    return bin(val)[2:].rjust(bits, "0")


if __name__ == "__main__":
    main()
