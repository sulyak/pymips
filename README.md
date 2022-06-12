# pymips

MIPS assembler written in python. 

### Requirements
* python3

### Instalation
`$ git clone https://github.com/sulyak/pymips`

### Usage
`python3 main.py input_file [--text] -o output_file`
where `input_file` is a text file that contains mips source code.

If `--text` is especified, output_file will cointain binary data represented as text, where each line corresponds to a single  mips instruction.

`-o output_file` can be omitted, if so a file named `a.bin` or `a.txt` will be generated instead.

 
### How it works

First the program collects all labels an it's respective lines and removes all of them.
Each lined is parsed in order to get the instruction and it's arguments, for example, `add $t1, $t2, $t3` would be parsed to `add, [$t1, $t2, $t3]`. After that, a binary equivalent of the instruction is created based on it's type and written to the output file.
Each instruction is build according to the [MIPS32 Instruction Set Manual](https://www.mips.com/products/architectures/mips32-2/).



