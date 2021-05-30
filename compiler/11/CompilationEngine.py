import sys
from JackTokenizer import TokenType
from SymbolTable import SymbolTable, Kind
from VMWriter import Segment, Arithmetic


class SyntaxError(Exception):
    pass


class NameError(Exception):
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
        self.label_index = 0
        if not self.tokenizer.hasMoreTokens():
            print("File is empty")
            return
        self.tokenizer.advance()
        self.next_token = self.tokenizer.current_token
        self.next_type = self.tokenizer.token_type
        self.current_token = None
        self.current_type = None
        self.function_type = None
        self.return_type = None
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
        # local var declaration
        while True:
            if self.next_token != "var":
                break
            self.compileVarDec()
        # body statements
        n_locals = self.table.varCount(Kind.VAR)
        function_label = self.class_name + "." + function_name
        self.writer.writeFunction(function_label, n_locals)
        if self.function_type == "constructor":
            # create space to store the field variable
            field_count = self.table.varCount(Kind.FIELD)
            self.writer.writePush(Segment.CONST, field_count)
            self.writer.writeCall("Memory.alloc", 1)
            # Store the based address in this
            self.writer.writePop(Segment.POINTER, 0)
        if self.function_type == "method":
            self.writer.writePush(Segment.ARG, 0)
            self.writer.writePop(Segment.POINTER, 0)
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
        argc = 0
        if self.next_token == "(":
            # Call method in the same class
            function_name = self.class_name + "." + function_name
            # Push this to stack as the first argument
            self.writer.writePush(Segment.POINTER, 0)
            argc += 1
            self.requireToken("(")
            argc += self.compileExpressionList()
            self.requireToken(")")
        elif self.next_token == ".":
            prefix = function_name
            self.requireToken(".")
            self.requireIdentifier()
            function_name = prefix + "." + self.current_token
            # If prefix is a variable, this is a method
            # If prefix is not a variable, it should be a class name, and
            # this subroutine should be a function or constructor
            if self.table.nameExist(prefix):
                v_type, v_kind, v_index = self.table.getEntry(prefix)
                self.writer.writePush(v_kind, v_index)
                function_name = v_type + "." + self.current_token
                argc += 1
            self.requireToken("(")
            argc += self.compileExpressionList()
            self.requireToken(")")
        else:
            raise SyntaxError("{}, line {}: expect subroutine\
                              call".format(self.filename,
                              self.tokenizer.line_number))
        self.requireToken(";")
        self.writer.writeCall(function_name, argc)
        self.writer.writePop(Segment.TEMP, 0)

    def compileLet(self):
        """
        Enter when next_token = let
        Return when current_token = ;
        """
        self.requireToken("let")
        self.requireIdentifier()
        v_name = self.current_token
        if self.table.nameExist(v_name):
            v_type, v_kind, v_index = self.table.getEntry(v_name)
        else:
            raise NameError("{}, line {} :{} does not exist in the current\
                            scope".format(self.filaname,
                            self.tokenizer.line_number, v_name))
        handling_array = False
        if self.next_token == "[":
            # Handling array
            handling_array = True
            self.requireToken("[")
            self.compileExpression()
            self.requireToken("]")
            self.writer.writePush(v_kind, v_index)
            self.writer.writeArithmetic(Arithmetic.ADD)
            # self.writer.writePop(Segment.POINTER, 1)
        if self.next_token == "=":
            self.advanceToken()
            self.compileExpression()
        else:
            raise SyntaxError("{}, line {}: missing = ".format(
                self.filename, self.tokenizer.line_number))
        if handling_array:
            self.writer.writePop(Segment.TEMP, 0)
            self.writer.writePop(Segment.POINTER, 1)
            self.writer.writePush(Segment.TEMP, 0)
            self.writer.writePop(Segment.THAT, 0)
        else:
            self.writer.writePop(v_kind, v_index)
        self.requireToken(";")
        return

    def compileWhile(self):
        """
        Enter when next_token = while
        """
        label1 = self.class_name + ".whileCond" + \
            str(self.label_index)
        label2 = self.class_name + ".whileFalse" + \
            str(self.label_index)
        self.label_index += 1
        self.writer.writeLabel(label1)
        self.requireToken("while")
        self.requireToken("(")
        self.compileExpression()
        self.requireToken(")")
        self.writer.writeArithmetic(Arithmetic.NOT)
        self.writer.writeIfGoto(label2)
        self.requireToken("{")
        self.compileStatements()
        self.requireToken("}")
        self.writer.writeGoto(label1)
        self.writer.writeLabel(label2)
        return

    def compileReturn(self):
        """
        Enter when next_token = return
        Return when current_token = ;
        """
        self.requireToken("return")
        if self.next_token != ";":
            self.compileExpression()
        else:
            self.writer.writePush(Segment.CONST, 0)
        self.writer.writeReturn()
        self.requireToken(";")
        return

    def compileIf(self):
        label1 = self.class_name + ".ifFalse" + \
            str(self.label_index)
        label2 = self.class_name + ".ifEnd" + \
            str(self.label_index)
        self.label_index += 1
        self.requireToken("if")
        self.requireToken("(")
        self.compileExpression()
        self.requireToken(")")
        self.writer.writeArithmetic(Arithmetic.NOT)
        self.writer.writeIfGoto(label1)
        self.requireToken("{")
        self.compileStatements()
        self.requireToken("}")
        self.writer.writeGoto(label2)
        self.writer.writeLabel(label1)
        if self.next_token == "else":
            self.requireToken("else")
            self.requireToken("{")
            self.compileStatements()
            self.requireToken("}")
        self.writer.writeLabel(label2)
        return

    def compileExpression(self):
        prev_op = None
        primitive_op = {
            "+": Arithmetic.ADD,
            "-": Arithmetic.SUB,
            "=": Arithmetic.EQ,
            ">": Arithmetic.GT,
            "<": Arithmetic.LT,
            "&": Arithmetic.AND,
            "|": Arithmetic.OR
        }
        while True:
            self.compileTerm()
            if prev_op in primitive_op:
                self.writer.writeArithmetic(primitive_op[prev_op])
            if prev_op == "*":
                self.writer.writeCall("Math.multiply", 2)
            if prev_op == "/":
                self.writer.writeCall("Math.divide", 2)
            if self.next_token in self.__op_list:
                self.advanceToken()
                prev_op = self.current_token
                continue
            else:
                break
        return

    def compileTerm(self):
        if self.next_token in ["-", "~"]:
            token = self.next_token
            self.advanceToken()
            self.compileTerm()
            if token == "-":
                self.writer.writeArithmetic(Arithmetic.NEG)
            else:
                self.writer.writeArithmetic(Arithmetic.NOT)
        elif self.next_type == TokenType.INT_CONST:
            self.advanceToken()
            self.writer.writePush(Segment.CONST, int(self.current_token))
        elif self.next_type == TokenType.STRING_CONST:
            self.advanceToken()
            str_const = self.current_token
            self.writer.writePush(Segment.CONST, len(str_const))
            self.writer.writeCall("String.new", 1)
            for c in str_const:
                self.writer.writePush(Segment.CONST, ord(c))
                self.writer.writeCall("String.appendChar", 2)
        elif self.next_type == TokenType.KEYWORD and \
            self.next_token in self.__keyword_constant_list:
            self.advanceToken()
            if self.current_token in ["null", "false"]:
                self.writer.writePush(Segment.CONST, 0)
            elif self.current_token == "true":
                self.writer.writePush(Segment.CONST, 1)
                self.writer.writeArithmetic(Arithmetic.NEG)
            else:
                self.writer.writePush(Segment.POINTER, 0)
        elif self.next_token == "(":
            self.requireToken("(")
            self.compileExpression()
            self.requireToken(")")
        elif self.next_type == TokenType.IDENTIFIER:
            self.advanceToken()
            v_name = self.current_token
            if self.next_token == "[":
                # Push array element in stack
                self.requireToken("[")
                self.compileExpression()
                self.requireToken("]")
                if self.table.nameExist(v_name):
                    v_type, v_kind, v_index = self.table.getEntry(v_name)
                    self.writer.writePush(v_kind, v_index)
                    self.writer.writeArithmetic(Arithmetic.ADD)
                    self.writer.writePop(Segment.POINTER, 1)
                    self.writer.writePush(Segment.THAT, 0)
                else:
                    raise NameError("{}, line {} :{} does not exist in the"\
                                    "current scope".format(self.filaname,
                                    self.tokenizer.line_number, v_name))
            elif self.next_token == "(":
                # Call subroutine in the same class
                argc = 0
                function_name = self.class_name + "." + v_name
                self.writer.writePush(Segment.POINTER, 0)
                argc += 1
                self.requireToken("(")
                argc += self.compileExpressionList()
                self.requireToken(")")
                self.writer.writeCall(function_name, argc)
            elif self.next_token == ".":
                # Call function or method
                argc = 0
                prefix = v_name
                self.requireToken(".")
                self.requireIdentifier()
                function_name = prefix + "." + self.current_token
                if self.table.nameExist(prefix):
                    v_type, v_kind, v_index = self.table.getEntry(prefix)
                    self.writer.writePush(v_kind, v_index)
                    function_name = v_type + "." + self.current_token
                    argc += 1
                self.requireToken("(")
                argc += self.compileExpressionList()
                self.requireToken(")")
                self.writer.writeCall(function_name, argc)
            else:
                # Just a variable
                if self.table.nameExist(v_name):
                    _, v_kind, v_index = self.table.getEntry(v_name)
                    self.writer.writePush(v_kind, v_index)
                else:
                    raise NameError("{}, line {}: variable {} not"\
                                "found".format(self.filename,
                                self.tokenizer.line_number,
                                self.current_token))
        else:
            raise SyntaxError("{}, line {}: term expected".format(
                self.filename, self.tokenizer.line_number))
        return

    def compileExpressionList(self):
        """
        Compile expression list
        Return the number of expression
        """
        count = 0
        while True:
            if self.next_token == ")":
                break
            self.compileExpression()
            count += 1
            if self.next_token == ",":
                self.advanceToken()
                continue
            elif self.next_token == ")":
                break
            else:
                raise SyntaxError("{}, line {}: missing )".format(
                    self.filename, self.tokenizer.line_number))
        return count

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
                              {}".format(self.filename,
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
