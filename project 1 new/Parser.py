import ASTNodeDefs as AST

class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = self.code[self.position]
        self.tokens = []

    # Move to the next position in the code.
    def advance(self):
        self.position += 1  # increment position
        if self.position >= len(self.code):  #index out of range
            self.current_char = None
        else:
            self.current_char = self.code[self.position]  # update the current char
        # TODO: Students need to complete the logic to advance the position.

    # Skip whitespaces.
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():  # if current char exists and is a whitespace
            self.advance() # move to next cchar
        # TODO: Complete logic to skip whitespaces.

    # Tokenize an identifier.
    def identifier(self):
        result = ''
        if not self.current_char.isalpha() and not self.current_char.isnumeric(): #invalid indentifier
            return None
        else:
            while (self.current_char.isalnum() or self.current_char == '_'):
                result += self.current_char
                self.advance()

        # TODO: Complete logic for handling identifiers.
        return ('IDENTIFIER', result)

    # Tokenize a number.
    def number(self):
        num_result = ''
        while self.current_char is not None and self.current_char.isdigit():
            num_result += self.current_char
            self.advance()
        # TODO: Implement logic to tokenize numbers.
        return ('NUMBER', int(num_result))

    def token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                ident = self.identifier()
                if ident[1] == 'if':
                    return ('IF', 'if')
                elif ident[1] == 'else':
                    return ('ELSE', 'else')
                elif ident[1] == 'while':
                    return ('WHILE', 'while')
                return ident
            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '+':
                self.advance()
                return ('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return ('MINUS', '-')
            if self.current_char == '/':
                self.advance()
                return ('DIVIDE', '/')
            if self.current_char == '*':
                self.advance()
                return ('MULTIPLY', '*')
            if self.current_char == '=':
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    return ("EQ", "==")
                return ('EQUALS', '=')
            if self.current_char == "!":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                return ('NEQ', '!=')
            if self.current_char == '>':
                self.advance()
                return ('GREATER', '>')
            if self.current_char == '<':
                self.advance()
                return ('LESS', '<')
            if self.current_char == '(':
                self.advance()
                return ('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return ('RPAREN', ')')
            if self.current_char == ',':
                self.advance()
                return ('COMMA', ',')
            if self.current_char == ':':
                self.advance()
                return ('COLON', ':')
                
            # TODO: Add logic for operators and punctuation tokens.
            
            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)
    

    # Collect all tokens into a list.
    def tokenize(self):
        while self.current_char != None:
            token = self.token()
            self.tokens.append(token)
            if token[0] == "EOF":
                break
            

        # TODO: Implement the logic to collect tokens.
        return self.tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)  # Start with the first token

    def advance(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)
        
        # Move to the next token in the list.
        # TODO: Ensure the parser doesn't run out of tokens.

    def parse(self):
        """
        Entry point for the parser. It will process the entire program.
        TODO: Implement logic to parse multiple statements and return the AST for the entire program.
        """
        return self.program()


    def program(self): 
        """
        Program consists of multiple statements.
        TODO: Loop through and collect statements until EOF is reached.
        """
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.statement())
            # TODO: Parse each statement and append it to the list.
        # TODO: Return an AST node that represents the program.
        return statements

    def statement(self): 
        """
        Determines which type of statement to parse.
        - If it's an identifier, it could be an assignment or function call.
        - If it's 'if', it parses an if-statement.
        - If it's 'while', it parses a while-statement.
        
        TODO: Dispatch to the correct parsing function based on the current token.
        """
        if self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS':  # Assignment
                return self.assign_stmt()
            elif self.peek() == 'LPAREN':  # Function call
                return self.function_call() #AST of function call
            else:
                raise ValueError(f"Unexpected token after identifier: {self.current_token}")
        elif self.current_token[0] == 'IF':
            return self.if_stmt() #AST of if stmt
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt()#AST of while stmt
        else:
            # TODO: Handle additional statements if necessary.
            raise ValueError(f"Unexpected token: {self.current_token}")


    def assign_stmt(self): 
        """
        Parses assignment statements.
        Example:
        x = 5 + 3
        TODO: Implement parsing for assignments, where an identifier is followed by '=' and an expression.
        """
        identifier = self.current_token
        self.advance()
        self.expect('EQUALS')
        expression = self.expression()
    
        return AST.Assignment(identifier, expression)

    def if_stmt(self): 
        """
        Parses an if-statement, with an optional else block.
        Example:
        if condition:
            # statements
        else:
            # statements
        TODO: Implement the logic to parse the if condition and blocks of code.
        """
        self.advance()  # skip if condition
        condition = self.boolean_expression()
        self.advance()   # move to next token
        block = self.block()

        else_block = None
        if self.current_token[0] == "ELSE":
            self.advance()   # skip else block
            self.expect('COLON')
            else_block = self.block()
            
        return AST.IfStatement(condition, block, else_block)


    def while_stmt(self): 
        """
        Parses a while-statement.
        Example:
        while condition:
            # statements
        TODO: Implement the logic to parse while loops with a condition and a block of statements.
        """
        self.advance() # skip while
        condition = self.boolean_expression()
        self.expect("COLON")
        block = self.block()

        return AST.WhileStatement(condition, block)

    def block(self):   
        """
        Parses a block of statements. A block is a collection of statements grouped by indentation.
        Example:
        if condition:
            # This is a block
            x = 5
            y = 10
        TODO: Implement logic to capture multiple statements as part of a block.
        """
        statements = []
        block_list = ["ELSE", "EOF"]
        while self.current_token[0] not in block_list: 
            statements.append(self.statement())


        # write your code here
        return AST.Block(statements)

    def expression(self): 
        """
        Parses an expression. Handles operators like +, -, etc.
        Example:
        x + y - 5
        TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence.
        """
        left = self.term()
        op_list = ["PLUS", "MINUS"]  # Parse the first term
        while self.current_token[0] in op_list:  # Handle + and -
            op = self.current_token  # Capture the operator
            self.advance()  # Skip the operator
            right = self.term()  # Parse the next term
            left = AST.BinaryOperation(left, op, right)
    
        return left

    def boolean_expression(self): 
        """
        Parses a boolean expression. These are comparisons like ==, !=, <, >.
        Example:
        x == 5
        TODO: Implement parsing for boolean expressions.
        """
        left = self.expression()
        boolean_list = ["EQ", "NEQ", "LESS", "GREATER"]
        if self.current_token[0] in boolean_list:
            op = self.current_token  # Capture the comparison operator
            self.advance()  # Move to the next token
            right = self.term()  # Parse the right-hand side expression
            return AST.BooleanExpression(left, op, right)
        # write your code here, for reference check expression function
        return left

    def term(self): 
        """
        Parses a term. A term consists of factors combined by * or /.
        Example:
        x * y / z
        TODO: Implement the parsing for multiplication and division.
        """
        left = self.factor()
        operator_list = ["MULTIPLY", "DIVIDE"]
        while self.current_token[0] in operator_list:
            op = self.current_token  # Capture the operator (* or /)
            self.advance()  # Move to the next token
            right = self.factor()  # Parse the next factor
            left = AST.BinaryOperation(left, op, right)  # Create a binary operation node

        # write your code here, for reference check expression function
        return left

    def factor(self): 
        """
        Parses a factor. Factors are the basic building blocks of expressions.
        Example:
        - A number
        - An identifier (variable)
        - A parenthesized expression
        TODO: Handle these cases and create appropriate AST nodes.
        """
        if self.current_token[0] == 'NUMBER':
            value = self.current_token
            self.advance()  # Move to the next token
            return value
            #write your code here
        elif self.current_token[0] == 'IDENTIFIER':
            value = self.current_token
            self.advance()  # Move to the next token
            return value

            #write your code here
        elif self.current_token[0] == 'LPAREN':
            self.advance()  # Skip '('
            expr = self.expression()  # Parse the expression inside parentheses
            self.expect("RPAREN")
            return expr
            #write your code here
        else:
            raise ValueError(f"Unexpected token in factor: {self.current_token}")

    def function_call(self): 
        """
        Parses a function call.
        Example:
        myFunction(arg1, arg2)
        TODO: Implement parsing for function calls with arguments.
        """
        func_name = self.current_token  # Get the function name (identifier)
        self.advance()  # Move to the '('
        self.expect('LPAREN')  # Ensure we have a '('

        args = self.arg_list()  # Parse the arguments
        self.expect('RPAREN')  # Ensure we have a ')'

        
        return AST.FunctionCall(func_name, args)

    def arg_list(self):  
        """
        Parses a list of arguments in a function call.
        Example:
        arg1, arg2, arg3
        TODO: Implement the logic to parse comma-separated arguments.
        """
        args = []
        if self.current_token[0] != 'RPAREN':  # Check if there are arguments
            args.append(self.expression())  # Parse the first argument

            while self.current_token[0] == 'COMMA':  # Handle comma-separated arguments
                self.advance()  # Skip the comma
                args.append(self.expression())  # Parse the next argument
        return args

    def expect(self, token_type):
       
        if self.current_token[0] == token_type:
            self.advance()  # Move to the next token
        else:
            raise ValueError(f"Expected {token_type} but got {self.current_token[0]}")

    def peek(self):
        if self.tokens:
            return self.tokens[0][0]
        else:
            return None
