import os
from JackTokenizer import JackTokenizer, TokenType
from CompilationEngine import CompilationEngine, SyntaxError, NameError
from VMWriter import VMWriter

class JackCompiler:
    def __init__(self, filename):
        """
        type filename: string
        """
        self.filename = filename
        self.out_stream = open(self.getOutputFilename(self.filename), 'w')
        self.in_stream = open(self.filename, 'r')
        self.tokenizer = JackTokenizer(self.in_stream)
        self.VMWriter = VMWriter(self.out_stream)
        self.engine = CompilationEngine(self.filename, self.tokenizer,
                                        self.VMWriter)

    def __exit__(self):
        self.in_stream.close()
        self.out_stream.close()

    def process(self):
        try:
            self.engine.compileClass()
        except (SyntaxError, NameError) as e:
            print(e)
            self.in_stream.close()
            self.out_stream.close()
            #os.remove(self.out_stream.name)

    def getOutputFilename(self, filename):
        """
        Generate output filename given the input filename
        type filename: string, the inpu filename
        rtype string
        """
        return os.path.splitext(filename)[0] + ".vm"

