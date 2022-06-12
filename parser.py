def parse_labels(lines):
    """
    return a dict(label_name, label_line) from a list of asm src lines
    """
    labels = {}
    for count, line in enumerate(lines):
        if ":" in line:
            label_name = line.split(":")[0]
            labels[label_name.lower()] = count
    return labels


def remove_labels(lines):
    """
    remove labels from each asm src line
    """
    result = []
    for line in lines:
        if ":" in line:
            result += [line.split(":")[1].strip()]
        else:
            result += [line]
    return result


def parse_line(line):
    """
    input: .asm src line
    output: instruction, [args]
    """
    # take the instruction
    instruction = line.split(" ")[0].lower()

    # take everything but the instruction
    args = "".join(line.split(" ")[1:])

    # get individual arguments
    args = args.strip().split(",")

    # lower everything
    args = list(map(str.lower, args))

    # separate arguments from offset
    # "-123($t)" -> "$t", "-123"
    for arg in reversed(args):
        if "(" in arg:
            offset, reg = arg.split("(")
            reg = reg.replace(")", "")
            args.remove(arg)
            args += [reg, offset]

    return instruction, args
