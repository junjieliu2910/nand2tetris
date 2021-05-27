import sys
from enum import Enum
import re


class TokenType(Enum):
    ERROR = 0
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5

class JackTokenizer:
    _int_reg = re.compile("\d+");
    _word_reg = re.compile("^[a-zA-Z_]\w*")
    _empty_reg = re.compile("^\s+")

    def __init__(self, file_stream):
        """
        type: file_stream: A opened file to read from
        """
        self.keyword_set = set([
            "class", "constructor", "function", "method", "field", "static",
            "var", "int", "char", "boolean", "void", "true", "false", "null",
            "this", "let", "do", "if", "else", "while", "return"
        ])
        self.symbol_set = set([
            "{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
            "&", "|", "<", ">", "=", "~"
        ])
        self.line_number = 0
        self.file_stream = file_stream
        self.current_line = ""
        self.char_index = 0
        self.current_token = ""
        self.token_type = TokenType.ERROR
        return

    def __exit__(self, *args):
        self.file_stream.close()

    def hasMoreTokens(self):
        """
        Check whether more lines are available
        rtype: bool
        """
        empty_match = self._empty_reg.search(self.current_line[self.char_index:])
        if empty_match:
            self.char_index += empty_match.span()[1]

        if self.char_index < len(self.current_line):
            return True
        else:
            self.readNextLine()
            self.removeComment()
        if not self.current_line:
            return False

        return True

    def advance(self):
        """
        Process the current line
        """
        if self.current_line[self.char_index] in self.symbol_set:
            self.symbol()
            return
        elif self.current_line[self.char_index].isdigit():
            self.intVal()
            return
        elif self.current_line[self.char_index] == "\"":
            self.stringVal()
            return
        else:
            match = self._word_reg.search(self.current_line[self.char_index:])
            end_index = match.span()[1]
            self.current_token = self.current_line[self.char_index:self.char_index+end_index]
            self.char_index = self.char_index + end_index
            if self.current_token in self.keyword_set:
                self.keyword()
            else:
                self.identifier()
            return

    def tokenType(self):
        """
        Return the token type of current token
        """
        return self.token_type

    def keyword(self):
        """
        Return the type of the keyward
        """
        self.token_type = TokenType.KEYWORD
        return

    def symbol(self):
        """
        Processing symbol token
        rtype: char
        """
        self.current_token = self.current_line[self.char_index]
        self.char_index += 1
        self.token_type = TokenType.SYMBOL
        return

    def identifier(self):
        """
        Processing identifier
        rtype: string
        """
        self.token_type = TokenType.IDENTIFIER
        return

    def intVal(self):
        """
        Processing int constant
        rtype: int
        """
        match = self._int_reg.search(self.current_line[self.char_index:])
        length = match.span()[1]
        self.current_token = self.current_line[self.char_index: self.char_index+length]
        self.char_index += length
        self.token_type = TokenType.INT_CONST
        return

    def stringVal(self):
        """
        Processing string constant
        rtype: string
        """
        end_index = self.current_line[self.char_index+1:].find("\"")
        self.current_token = self.current_line[self.char_index+1:self.char_index+1+end_index]
        self.char_index = self.char_index+end_index+2
        self.token_type = TokenType.STRING_CONST
        return

    def readNextLine(self):
        self.current_line = self.file_stream.readline()
        self.line_number += 1
        return

    def removeComment(self):
        """
        Helper function to remove the comment
        """
        comment_re = re.compile("\s*/\\*")
        comment_re2 = re.compile("^\s*//")
        empty_re = re.compile("^\s*$")
        while True:
            match = comment_re.search(self.current_line)
            if match:
                if match.span()[0] != 0:
                    print("Line {:d}: Wrong comment format".format(self.line_number))
                    sys.exit()
                comment_end = re.compile("\\*/\s*$")
                while True:
                    if(comment_end.search(self.current_line)):
                        self.readNextLine()
                        break
                    self.readNextLine()
                    if not self.current_line:
                        print("Line {:d}: Comment not closed".format(self.line_number))
                        sys.exit()

            match = comment_re2.search(self.current_line)
            if match:
                self.readNextLine()
                continue
            match = empty_re.search(self.current_line)
            if match:
                self.readNextLine()
                if not self.current_line:
                    break
                else:
                    continue
            break

        if self.current_line:
            comment_index = self.current_line.find("//")
            if(comment_index != -1):
                self.current_line = self.current_line[0:comment_index]
            self.char_index = 0
            empty_match = self._empty_reg.search(self.current_line)
            if empty_match:
                self.char_index += empty_match.span()[1]

        return
