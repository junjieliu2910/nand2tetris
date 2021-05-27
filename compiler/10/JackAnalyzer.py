import os
from JackTokenizer import JackTokenizer, TokenType
from CompilationEngine import CompilationEngine

class JackAnalyzer:
    def __init__(self, filename):
        """
        type filename: string
        """
        self.filename = filename
        self.out_stream = open(self.getOutputFilename(self.filename), 'w')
        self.in_stream = open(self.filename, 'r')
        self.engine = CompilationEngine(self.filename, self.in_stream, self.out_stream)
        return

    def __exit__(self):
        self.int_stream.close()
        self.out_stream.close()
        return

    def process(self):
        self.engine.compileClass()

    def getOutputFilename(self, filename):
        """
        Generate output filename given the input filename
        type filename: string, the inpu filename
        rtype string
        """
        return os.path.splitext(filename)[0] + ".xml"

