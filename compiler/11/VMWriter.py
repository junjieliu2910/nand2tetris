class VMWriter:
    def __init__(self, out_stream):
        self.out_stream = out_stream
        return

    def writePush(self, segment, index):
        pass

    def writePop(self, segment, index):
        pass

    def writeArithmetic(self, command):
        pass

    def writeLabel(self, label):
        pass

    def writeGoto(self, label):
        pass

    def writeIfGoto(self, label):
        pass

    def writeCall(self, name, argc):
        pass

    def writeFunction(self, name, n_locals):
        pass

    def writeReturn(self):
        pass

    def close():
        pass
