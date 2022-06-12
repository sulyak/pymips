import sys
import struct

if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} file.bin")
    sys.exit(1)

with open(sys.argv[1], "rb") as f:
    word = f.read(4)

    while word:
        word = struct.unpack("<I", word)[0]
        word = str.rjust(bin(word)[2:], 32, '0')

        print(word, len(str(word)))
        word = f.read(4)
