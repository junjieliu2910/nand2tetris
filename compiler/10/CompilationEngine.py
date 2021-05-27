import sys
from JackTokenizer import JackTokenizer, TokenType

class CompilationEngine:
    __subroutine_keyword_list = ["constructor", "function", "method"]
    __type_keyword_list = ["int", "char", "boolean", "void"]
    __class_var_list = ["static", "field"]
    __keyword_constant_list = ["true", "false", "null", "this"]
    __op_list = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

    def __init__(self, filename, in_stream, out_stream):
        self.filename = filename
        self.input_stream = in_stream
        self.output_stream = out_stream
        self.tokenizer = JackTokenizer(self.input_stream)
        self.prefix = ""
        if not self.tokenizer.hasMoreTokens():
            print("File is empty")
            return
        self.tokenizer.advance()
        self.next_token = self.tokenizer.current_token
        self.next_type = self.tokenizer.token_type
        self.current_token = ""
        self.current_type = 0
        return

    def compileClass(self):
        """
        First subroutine called for each file
        """
        self.startNonTerminal("<class>\n")
        # compile class ClassName {
        self.requireToken("class")
        self.requireIdentifier()
        self.requireToken("{")
        # Compile the body of class until next_token = }
        while True:
            if self.next_token in self.__class_var_list:
                self.compileClassVarDec()
            elif self.next_token in self.__subroutine_keyword_list:
                break
            elif self.next_token == "}":
                break
            else:
                print("{}, line {}: expect class var or subroutine but receive {}".format(
                    self.filename, self.tokenizer.line_number, self.next_token
                ))
                sys.exit()

        while True:
            if self.next_token in self.__subroutine_keyword_list:
                self.compileSubroutine()
            elif self.next_token == "}":
                break
            else:
                print("{}, line {}: expect subroutine but receive {}".format(
                    self.filename, self.tokenizer.line_number, self.next_token
                ))
                sys.exit()
        self.requireToken("}")
        self.endNonTerminal("</class>\n")
        return

    def compileClassVarDec(self):
        """
        Enter when next_token = static, field
        Return when current_token = ;
        """
        self.startNonTerminal("<classVarDec>\n")
        self.requireInList(self.__class_var_list)
        self.requireType()
        self.requireIdentifier()
        while True:
            if self.next_token == ";":
                self.advanceToken()
                break
            elif self.next_token == ",":
                self.advanceToken()
                self.requireIdentifier()
            else:
                print("{}, line {}: expected , or ; but receive {}".format(
                    self.filename, self.tokenizer.line_number, self.next_token
                ))
                sys.exit()
        self.endNonTerminal("</classVarDec>\n")
        return

    def compileSubroutine(self):
        """
        Enter when next_token = constructor, function, method
        """
        self.startNonTerminal("<subroutineDec>\n")
        self.requireInList(self.__subroutine_keyword_list)
        self.requireType()
        self.requireIdentifier()
        self.requireToken("(")
        # Parameter list
        self.compileParameterList() # Compile untill next_token = ")"
        self.requireToken(")")
        # handle subroutine body
        self.startNonTerminal("<subroutineBody>\n")
        self.requireToken("{")
        # body var declaration
        while True:
            if self.next_token != "var":
                break
            self.compileVarDec()
        # body statements
        self.compileStatements() # Compile until next_token = "}"
        # body end
        self.requireToken("}")
        self.endNonTerminal("</subroutineBody>\n")
        # subroutineDec end
        self.endNonTerminal("</subroutineDec>\n")
        return

    def compileParameterList(self):
        """
        Enter at funciton declaration, current_token = (,
        Return when next_token = ")"
        """
        self.startNonTerminal("<parameterList>\n")
        while True:
            if self.next_token == ")":
                break
            self.requireType()
            self.requireIdentifier()
            if self.next_token == ",":
                self.advanceToken()
                continue
            elif self.next_token == ")":
                break
            else:
                print("{}, line {}: expected , or ; but receive {}".format(
                    self.filename, self.tokenizer.line_number, self.next_token
                ))
                sys.exit()
        self.endNonTerminal("</parameterList>\n")
        return

    def compileVarDec(self):
        """
        Enter when next_token = var
        Return when current_token = ;
        """
        self.startNonTerminal("<varDec>\n")
        self.requireToken("var")
        self.requireType()
        self.requireIdentifier()
        while True:
            if self.next_token == ";":
                self.advanceToken()
                break
            elif self.next_token == ",":
                self.advanceToken()
                self.requireIdentifier()
            else:
                print("{}, line {}: expected , or ; but receive {}".format(
                    self.filename, self.tokenizer.line_number, self.next_token
                ))
                sys.exit()
        self.endNonTerminal("</varDec>\n")
        return

    def compileStatements(self):
        """
        Enter when current_token = "{"
        Return when next_token = "}"
        """
        self.startNonTerminal("<statements>\n")
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
                print("{}, line {}: expect statement but receive {}".format(
                    self.filename, self.tokenizer.line_number, self.next_token))
                sys.exit()
        self.endNonTerminal("</statements>\n")
        return

    def compileDo(self):
        """
        Enter when next_token = do
        Return when current_token = ;
        """
        self.startNonTerminal("<doStatement>\n")
        self.requireToken("do")
        self.requireIdentifier()
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
            print("{}, line {}: expect subroutine call".format(
                self.filename, self.tokenizer.line_number))
        self.requireToken(";")
        self.endNonTerminal("</doStatement>\n")
        return

    def compileLet(self):
        """
        Enter when next_token = let
        Return when current_token = ;
        """
        self.startNonTerminal("<letStatement>\n")
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
        self.endNonTerminal("</letStatement>\n")
        return

    def compileWhile(self):
        """
        Enter when next_token = while
        """
        self.startNonTerminal("<whileStatement>\n")
        self.requireToken("while")
        self.requireToken("(")
        self.compileExpression()
        self.requireToken(")")
        self.requireToken("{")
        self.compileStatements()
        self.requireToken("}")
        self.endNonTerminal("</whileStatement>\n")
        return

    def compileReturn(self):
        """
        Enter when next_token = return
        Return when current_token = ;
        """
        self.startNonTerminal("<returnStatement>\n")
        self.requireToken("return")
        if self.next_token != ";":
            self.compileExpression()
        self.requireToken(";")
        self.endNonTerminal("</returnStatement>\n")
        return

    def compileIf(self):
        self.startNonTerminal("<ifStatement>\n")
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
        self.endNonTerminal("</ifStatement>\n")
        return

    def compileExpression(self):
        self.startNonTerminal("<expression>\n")
        while True:
            self.compileTerm()
            if self.next_token in self.__op_list:
                self.advanceToken()
                continue
            else:
                break
        self.endNonTerminal("</expression>\n")
        return

    def compileTerm(self):
        self.startNonTerminal("<term>\n")
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
        self.endNonTerminal("</term>\n")
        return

    def compileExpressionList(self):
        self.startNonTerminal("<expressionList>\n")
        while True:
            if self.next_token == ")":
                break
            self.compileExpression()
            if self.next_token == ",":
                self.advanceToken();
                continue
            elif self.next_token == ")":
                break;
            else:
                print("{}, line {}: missing )".format(
                    self.filename, self.tokenizer.line_number))
                sys.exit()
        self.endNonTerminal("</expressionList>\n")
        return

    def increasePrefix(self):
        self.prefix += "  "
        return

    def decreasePrefix(self):
        self.prefix = self.prefix[0:len(self.prefix)-2]
        return

    def startNonTerminal(self, NTtype):
        self.output_stream.writelines(self.prefix+NTtype)
        self.increasePrefix()
        return

    def endNonTerminal(self, NTtype):
        self.decreasePrefix()
        self.output_stream.writelines(self.prefix+NTtype)
        return

    def requireType(self):
        """
        Require next token to be a type
        if false print error message
        """
        if self.next_type == TokenType.IDENTIFIER or \
        self.next_token in self.__type_keyword_list:
            self.advanceToken()
        else:
            print("{}, line {}: A type name expected but receive {}".format( \
                self.filename, self.tokenizer.line_number, self.next_token))
        return

    def requireIdentifier(self):
        """
        Require next token to be identifier, if true, advance
        if false print error message
        """
        if self.next_type == TokenType.IDENTIFIER:
            self.advanceToken()
        else:
            print("{}, line {}: {} expected but receive {}".format( \
                self.filaname, self.tokenizer.line_number, \
                TokenType.IDENTIFIER, self.next_type))
        return


    def requireToken(self, token):
        """
        Require next token, if true, advance one step,
        if false print error message
        """
        if self.next_token != token:
            print("{}, line {}: {} expected but receive {}".
                  format(self.filaname, self.tokenizer.line_number,
                         token, self.next_token))
            sys.exit()
        else:
            self.advanceToken()
        return

    def requireInList(self, token_list):
        """
        Require next token is in the given list, if true, advance one step,
        if false print error message
        """
        if self.next_token not in token_list:
            print("{}, line {}: {} expected but receive {}".
                  format(self.filename, self.tokenizer.line_number,
                         token, self.next_token))
            sys.exit()
        else:
            self.advanceToken()
        return

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
        self.writeTerminal()

    def writeTerminal(self):
        current_token = self.current_token
        current_type = self.current_type
        line = self.prefix
        if current_type == TokenType.KEYWORD:
            line += "<keyword> " + current_token + " </keyword>\n"
        elif current_type == TokenType.SYMBOL:
            line += "<symbol> "
            if current_token == "<":
                line += "&lt;"
            elif current_token == ">":
                line += "&gt;"
            elif current_token == "\"":
                line += "&quot;"
            elif current_token == "&":
                line += "&amp;"
            else:
                line += current_token
            line += " </symbol>\n"
        elif current_type == TokenType.INT_CONST:
            line += "<integerConstant> " + current_token + " </integerConstant>\n"
        elif current_type == TokenType.STRING_CONST:
            line += "<stringConstant> " + current_token + " </stringConstant>\n"
        elif current_type == TokenType.IDENTIFIER:
            line += "<identifier> " + current_token + " </identifier>\n"
        self.output_stream.writelines(line)
        return
