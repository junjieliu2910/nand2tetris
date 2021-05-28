from enum import Enum

class Segment(Enum):
    CONST = 0
    ARG = 1
    LOCAL = 2
    STATIC = 3
    THIS = 4
    THAT = 5
    POINTER = 6
    TEMP = 7

class Arithmetic(Enum):
    ADD = 0
    SUB = 1
    NEG = 2
    EQ = 3
    GT = 4
    LT = 5
    AND = 6
    OR = 7
    NOT = 8

class VMWriter:
    __segment_map_dict = {
        Segment.CONST: "const",
        Segment.ARG: "ARG",
        Segment.LOCAL: "local",
        Segment.STATIC: "static",
        Segment.THIS: "this",
        Segment.THAT: "that",
        Segment.POINTER: "pointer",
        Segment.TEMP: "temp"
    }

    __arithmetic_map_dict = {
        Arithmetic.ADD: "add",
        Arithmetic.SUB: "sub",
        Arithmetic.NEG: "neg",
        Arithmetic.EQ: "eq",
        Arithmetic.GT: "gt",
        Arithmetic.LT: "lt",
        Arithmetic.AND: "and",
        Arithmetic.OR: "or",
        Arithmetic.NOT: "nor"
    }

    def __init__(self, out_stream):
        self.out_stream = out_stream
        return

    def writePush(self, segment, index):
        line = "push " + self.__segment_map_dict[segment] + " " + index + "\n"
        self.out_stream.writelines(line)
        return

    def writePop(self, segment, index):
        line = "pop" + self.__segment_map_dict[segment] + " " + index + "\n"
        self.out_stream.writelines(line)
        return

    def writeArithmetic(self, command):
        line = self.__arithmetic_map_dict[command] + "\n"
        self.out_stream.writelines(line)
        return

    def writeLabel(self, label):
        line = "label " + label + "\n"
        self.out_stream.writelines(line)
        return

    def writeGoto(self, label):
        line = "goto " + label + "\n"
        self.out_stream.writelines(line)
        return

    def writeIfGoto(self, label):
        line = "if-goto " + label + "\n"
        self.out_stream.writelines(line)
        return

    def writeCall(self, name, argc):
        line = "call " + name + " " + argc + "\n"
        self.out_stream.writelines(line)
        return

    def writeFunction(self, name, n_locals):
        line = "function " + name + " " + n_locals + "\n"
        self.out_stream.writelines(line)
        return

    def writeReturn(self):
        self.out_stream.writelines("return\n")
        return
