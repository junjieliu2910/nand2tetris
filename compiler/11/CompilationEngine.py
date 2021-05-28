import sys
from JackTokenizer import TokenType
from SymbolTable import SymbolTable, Kind
from VMWriter import Segment, Arithmetic


class SyntaxError(Exception):
    pass


class CompilationEngine:
    __subroutine_keyword_list = ["constructor", "function", "method"]
    __type_keyword_list = ["int", "char", "boolean", "void"]
    __class_var_list = ["static", "field"]
    __keyword_constant_list = ["true", "false", "null", "this"]
    __op_list = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

    def __init__(self, filename, tokenizer, vm_writer):
        self.filename = filename
        self.class_name = ""
        self.writer = vm_writer
        self.tokenizer = tokenizer
        self.table = SymbolTable()
        if not self.tokenizer.hasMoreTokens():
            print("File is empty")
            return
        self.tokenizer.advance()
        self.next_token = self.tokenizer.current_token
        self.next_type = self.tokenizer.token_type
        self.current_token = ""
        self.current_type = 0
        self.function_type = ""
        self.return_type = ""
        return

    def compileClass(self):
        """
        First subroutine called for each file
        """
        self.requireToken("class")
        self.requireIdentifier()
        self.class_name = self.current_token
        self.requireToken("{")
        # Compile the class var
        while True:
            if self.next_token in self.__class_var_list:
                self.compileClassVarDec()
            elif self.next_token in self.__subroutine_keyword_list:
                break
            elif self.next_token == "}":
                break
            else:
                raise SyntaxError("{}, line {}: expect class var or subroutine\
                                  or end but receive {}".format(self.filename,
                                  self.tokenizer.line_number, self.next_token))
        # Compile the class subroutine
        while True:
            if self.next_token in self.__subroutine_keyword_list:
                self.compileSubroutine()
            elif self.next_token == "}":
                break
            else:
                raise SyntaxError("{}, line {}: expect end or subroutine but \
                                  receive {}".format(self.filename,
                                  self.tokenizer.line_number, self.next_token))
        self.requireToken("}")
        return

    def compileClassVarDec(self):
        """
        Enter when next_token = static, field
        Return when current_token = ;
        """
        self.requireInList(self.__class_var_list)
        cv_kind = Kind.NONE
        if self.current_token == "static":
            cv_kind = Kind.STATIC
        else:
            cv_kind = Kind.FIELD
        self.requireType()
        cv_type = self.current_token
        self.requireIdentifier()
        cv_name = self.current_token
        self.table.define(cv_name, cv_type, cv_kind)
        while True:
            if self.next_token == ";":
                self.advanceToken()
                break
            elif self.next_token == ",":
                self.advanceToken()
                self.requireIdentifier()
                cv_name = self.current_token
                self.table.define(cv_name, cv_type, cv_kind)
            else:
                raise SyntaxError("{}, line {}: expected , or ; but receive \
                                  {}".format(self.filename,
                                  self.tokenizer.line_number, self.next_token))
        return

    def compileSubroutine(self):
        """
        Enter when next_token = constructor, function, method
        Use this pointer to access class scope variables
        Need to determine the number of local variables (Kind.VAR)
        """
        self.table.startSubroutine()
        self.requireInList(self.__subroutine_keyword_list)
        self.function_type = self.current_token
        self.requireType()
        self.return_type = self.current_token
        self.requireIdentifier()
        function_name = self.current_token
        self.requireToken("(")
        self.compileParameterList()
        self.requireToken(")")
        self.requireToken("{")
        # body var declaration
        while True:
            if self.next_token != "var":
                break
            self.compileVarDec()
        # body statements
        n_locals = self.table.varCount(Kind.VAR)
        function_label = self.class_name + "." + function_name
        self.writer.writeFunction(function_label, n_locals)
        if self.function_type == "constructor":
            # TODO: complete constructor logic here
            pass
        self.compileStatements()
        self.requireToken("}")
        return

    def compileParameterList(self):
        """
        Enter at funciton declaration, current_token = (,
        Return when next_token = ")"
        Record the ARG variables in the subroutine symbol table
        """
        if self.function_type == "method":
            self.table.define("this", self.class_name, Kind.ARG)
        while True:
            if self.next_token == ")":
                break
            self.requireType()
            arg_type = self.current_token
            self.requireIdentifier()
            arg_name = self.current_token
            self.table.define(arg_name, arg_type, Kind.ARG)
            if self.next_token == ",":
                self.advanceToken()
                continue
            elif self.next_token == ")":
                break
            else:
                raise SyntaxError("{}, line {}: expected , or ; but receive \
                                  {}".format(self.filename,
                                  self.tokenizer.line_number, self.next_token))
        return

    def compileVarDec(self):
        """
        Enter when next_token = var
        Return when current_token = ;
        Record the local variable in the subtoutine symbol table
        """
        self.requireToken("var")
        kind = Kind.VAR
        self.requireType()
        v_type = self.current_token
        self.requireIdentifier()
        v_name = self.current_token
        self.table.define(v_name, v_type, kind)
        while True:
            if self.next_token == ";":
                self.advanceToken()
                break
            elif self.next_token == ",":
                self.advanceToken()
                self.requireIdentifier()
                v_name = self.current_token
                self.table.define(v_name, v_type, kind)
            else:
                raise SyntaxError("{}, line {}: expected , or ; but receive \
                                  {}".format(self.filename,
                                  self.tokenizer.line_number, self.next_token))
        return

    def compileStatements(self):
        """
        Enter when current_token = "{"
        Return when next_token = "}"
        """
        while True:
            if self.next_token == "let":
                self.compileLet()
            elif self.next_token == "if":
                self.compileIf()
            elif self.next_token == "while":
                self.compileWhile()
            elif self.next_token == "do":
                self.compileDo()
            elif self.next_token == "return":
                self.compileReturn()
            elif self.next_token == "}":
                break
            else:
                raise SyntaxError("{}, line {}: expect statement but receive\
                                  {}".format(self.filename,
                                  self.tokenizer.line_number, self.next_token))
        return

    def compileDo(self):
        """
        Enter when next_token = do
        Return when current_token = ;
        Just call the function
        """
        self.requireToken("do")
        self.requireIdentifier()
        function_name = self.current_token
        if self.next_token == "(":
            self.advanceToken()
            self.compileExpressionList()
            self.requireToken(")")
        elif self.next_token == ".":
            self.advanceToken()
            self.requireIdentifier()
            self.requireToken("(")
            self.compileExpressionList()
            self.requireToken(")")
        else:
            raise SyntaxError("{}, line {}: expect subroutine\
                              call".format(self.filename,
                              self.tokenizer.line_number))
        self.requireToken(";")

    def compileLet(self):
        """
        Enter when next_token = let
        Return when current_token = ;
        """
        self.requireToken("let")
        self.requireIdentifier()
        if self.next_token == "[":
            self.advanceToken()
            self.compileExpression()
            self.requireToken("]")

        if self.next_token == "=":
            self.advanceToken()
            self.compileExpression()
        else:
            print("{}, line {}: missing = ".format(
                self.filename, self.tokenizer.line_number))
        self.requireToken(";")
        return

    def compileWhile(self):
        """
        Enter when next_token = while
        """
        self.requireToken("while")
        self.requireToken("(")
        self.compileExpression()
        self.requireToken(")")
        self.requireToken("{")
        self.compileStatements()
        self.requireToken("}")
        return

    def compileReturn(self):
        """
        Enter when next_token = return
        Return when current_token = ;
        """
        self.requireToken("return")
        if self.next_token != ";":
            self.compileExpression()
        self.requireToken(";")
        return

    def compileIf(self):
        self.requireToken("if")
        self.requireToken("(")
        self.compileExpression()
        self.requireToken(")")
        self.requireToken("{")
        self.compileStatements()
        self.requireToken("}")
        if self.next_token == "else":
            self.requireToken("else")
            self.requireToken("{")
            self.compileStatements()
            self.requireToken("}")
        return

    def compileExpression(self):
        while True:
            self.compileTerm()
            if self.next_token in self.__op_list:
                self.advanceToken()
                continue
            else:
                break
        return

    def compileTerm(self):
        if self.next_token == "-" or self.next_token == "~":
            self.advanceToken()
            self.compileTerm()
        elif self.next_type == TokenType.INT_CONST:
            self.advanceToken()
        elif self.next_type == TokenType.STRING_CONST:
            self.advanceToken()
        elif self.next_type == TokenType.KEYWORD and \
            self.next_token in self.__keyword_constant_list:
            self.advanceToken()
        elif self.next_token == "(":
            self.advanceToken()
            self.compileExpression()
            self.requireToken(")")
        elif self.next_type == TokenType.IDENTIFIER:
            self.advanceToken()
            if self.next_token == "[":
                self.requireToken("[")
                self.compileExpression()
                self.requireToken("]")
            elif self.next_token == "(":
                self.advanceToken()
                self.compileExpressionList()
                self.requireToken(")")
            elif self.next_token == ".":
                self.advanceToken()
                self.requireIdentifier()
                self.requireToken("(")
                self.compileExpressionList()
                self.requireToken(")")
        else:
            print("{}, line {}: term expected".format(
                self.filename, self.tokenizer.line_number))
        return

    def compileExpressionList(self):
        while True:
            if self.next_token == ")":
                break
            self.compileExpression()
            if self.next_token == ",":
                self.advanceToken()
                continue
            elif self.next_token == ")":
                break
            else:
                print("{}, line {}: missing )".format(
                    self.filename, self.tokenizer.line_number))
                sys.exit()

    def requireType(self):
        """
        Require next token to be a type
        if false print error message
        """
        if self.next_type == TokenType.IDENTIFIER or self.next_token in \
                self.__type_keyword_list:
            self.advanceToken()
        else:
            raise SyntaxError("{}, line {}: A type name expected but receive\
                              {}".format(self.filename,
                              self.tokenizer.line_number, self.next_token))

    def requireIdentifier(self):
        """
        Require next token to be identifier, if true, advance
        if false print error message
        """
        if self.next_type == TokenType.IDENTIFIER:
            self.advanceToken()
        else:
            raise SyntaxError("{}, line {}: {} expected but receive\
                              {}".format(self.filaname,
                              self.tokenizer.line_number, TokenType.IDENTIFIER,
                              self.next_type))

    def requireToken(self, token):
        """
        Require next token, if true, advance one step,
        if false print error message
        """
        if self.next_token != token:
            raise SyntaxError("{}, line {}: {} expected but receive\
                              {}".format(self.filaname,
                              self.tokenizer.line_number, token,
                              self.next_token))
        else:
            self.advanceToken()

    def requireInList(self, token_list):
        """
        Require next token is in the given list, if true, advance one step,
        if false print error message
        """
        if self.next_token not in token_list:
            raise SyntaxError("{}, line {}: expected but receive \
                              {}".format(self.filename,
                              self.tokenizer.line_number, self.next_token))
        else:
            self.advanceToken()

    def advanceToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            self.current_token = self.next_token
            self.current_type = self.next_type
            self.next_token = self.tokenizer.current_token
            self.next_type = self.tokenizer.token_type
        else:
            self.current_token = self.next_token
            self.current_type = self.next_type
            self.next_token = ""
            self.next_type = TokenType.ERROR
