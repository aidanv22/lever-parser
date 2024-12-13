import ASTNodeDefs as AST
class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = self.code[self.position]
        self.tokens = []
    
    # Move to the next position in the code increment by one.
    def advance(self):
        self.position += 1
        if self.position >= len(self.code):
            self.current_char = None
        else:
            self.current_char = self.code[self.position]

    # If the current char is whitespace, move ahead.
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Tokenize the identifier.
    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return ('IDENTIFIER', result)
    

    # Tokenize numbers, including float handling
    def number(self):
        result = ''
        is_float = False   # set value to false, until true
        # TODO: Update this code to handle floating-point numbers 
        # while the current charachter isn't none and its either a number or period
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == "."):
            # if its a period, its a float and add to result
            if self.current_char == ".":
                is_float = True
                result += self.current_char
                self.advance()
            # if its a number add to result
            else:
                result += self.current_char
                self.advance()
        
        if is_float:
            return ('FNUMBER', float(result))
        else:
            return ('NUMBER', int(result))

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
                elif ident[1] == 'int':
                    return ('INT', 'int')
                elif ident[1] == 'float':
                    return ('FLOAT', 'float')
                return ident  # Generic identifier
            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()
            if self.current_char == '+':
                self.advance()
                return ('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return ('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return ('MULTIPLY', '*')
            if self.current_char == '/':
                self.advance()
                return ('DIVIDE', '/')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('EQ', '==')
                return ('EQUALS', '=')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('NEQ', '!=')
            if self.current_char == '<':
                self.advance()
                return ('LESS', '<')
            if self.current_char == '>':
                self.advance()
                return ('GREATER', '>')
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
            if self.current_char == "{":
                self.advance()
                return ('LBRACE', '{')
            if self.current_char == "}":
                self.advance()
                return ('RBRACE', '}')
            # TODO: Implement handling for '{' and '}' tokens here (see `tokens.txt` for exact names)
            if self.current_char == '\n':
                self.advance()
                continue

            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)

    # Collect all the tokens in a list.
    def tokenize(self):
        while True:
            token = self.token()
            self.tokens.append(token)
            if token[0] == 'EOF':
                break
        return self.tokens



import ASTNodeDefs as AST

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)
        # Use these to track the variables and their scope
        self.symbol_table = {'global': {}}
        self.scope_counter = 0
        self.scope_stack = ['global']
        self.messages = []

    def error(self, message):
        self.messages.append(message)
    
    def advance(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)

    # TODO: Implement logic to enter a new scope, add it to symbol table, and update `scope_stack`
    def enter_scope(self):
        # when entering scope, increase scope count
        self.scope_counter+=1
        # name our new scope as "scope1", "scope2", etc.
        new_scope = "scope" + f"{self.scope_counter}"
        #create new scope dict
        self.symbol_table[new_scope] = {}
        # add new scope to scope stack
        self.scope_stack.append(new_scope)
        

    # TODO: Implement logic to exit the current scope, removing it from `scope_stack`
    def exit_scope(self):
        # if global scope is only one in stack dont pop it
        if len(self.scope_stack) <= 1:
            self.error("Cannot exit the global scope")
        # otherwise remove scope
        else:
            self.scope_stack.pop()

    # Return the current scope name
    def current_scope(self):
        return self.scope_stack[-1]

    # TODO: Check if a variable is already declared in the current scope; if so, log an error
    def checkVarDeclared(self, identifier):
        # creeate a variable to create a dictionary of the current scope in symbol table
        current_scope_dict = self.symbol_table[self.current_scope()]
        # if the variable identifier in this current scopes dictionary already, raise error
        if identifier in current_scope_dict:
            self.error(f'Variable {identifier} has already been declared in the current scope')


    # TODO: Check if a variable is declared in any accessible scope; if not, log an error
    def checkVarUse(self, identifier):
        # loop thru the scope stack backwards, from the most recently added scope
        for scope_name in reversed(self.scope_stack):  # Traverse the scope stack in reverse
            # if the identifier already defined, skio
            if identifier in self.symbol_table[scope_name]:
                return  # Found the variable, no need to log an error
        # if not, return eerror
        self.error(f'Variable {identifier} has not been declared in the current or any enclosing scopes')


    # TODO: Check type mismatch between two entities; log an error if they do not match
    def checkTypeMatch2(self, vType, eType, var, exp):
        # make sure the types are declared, if they are skip
        if (vType is not None and eType is not None):
            # if types don't match, raise error
            if vType != eType:
                self.error(f'Type Mismatch between {vType} and {eType}')


    # TODO: Implement logic to add a variable to the current scope in `symbol_table`
    def add_variable(self, name, var_type):
        # again, create a variable that tracks the current scopes dict
        current_scope_dict = self.symbol_table[self.current_scope()]
        # if the var name hasn't been defined, add it
        if name not in current_scope_dict:
            current_scope_dict[name] = var_type

    # TODO: Retrieve the variable type from `symbol_table` if it exists
    def get_variable_type(self, name):
        # loop thru scope stack backwards from most recently added scope
        for scope_name in reversed(self.scope_stack):  # Check accessible scopes in reverse order
            # if name exist in scope, return it
            if name in self.symbol_table[scope_name]:
                return self.symbol_table[scope_name][name]
        return None  # Return None if the variable is not found

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.statement())
        return AST.Block(statements)


    # TODO: Modify the `statement` function to dispatch to declare statement
    def statement(self):
        if self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS':
                return self.assign_stmt()
            elif self.peek() == 'LPAREN':
                return self.function_call()
            else:
                raise ValueError(f"Unexpected token after identifier: {self.current_token}")
        elif self.current_token[0] == 'IF':
            return self.if_stmt()
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt()
        elif self.current_token[0] == 'INT' or 'FLOAT':
            return self.decl_stmt()
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")


    # TODO: Implement the declaration statement and handle adding the variable to the symbol table
    def decl_stmt(self):
        """
        Parses a declaration statement.
        Example:
        int x = 5
        float y = 3.5
        TODO: Implement logic to parse type, identifier, and initialization expression and also handle type checking
        """
        # var type is second one in tuple
        var_type = self.current_token[1]
        self.advance()
        # after advancing, define name
        var_name = self.current_token[1]
        # check if this name has been declared in scope
        self.checkVarDeclared(var_name)
        # if not, add it
        self.add_variable(var_name,var_type)
        self.advance()
        self.expect('EQUALS')
        expression = self.expression()
        # self.advance()

        # check if the types are compatible
        self.checkTypeMatch2(var_type, expression.value_type,var_name, expression)
        return AST.Declaration(var_type, var_name, expression)

    # TODO: Parse assignment statements, handle type checking
    def assign_stmt(self):
        """
        Parses an assignment statement.
        Example:
        x = 10
        x = y + 5
        TODO: Implement logic to handle assignment, including type checking.
        """
        
        # set var name
        var_name = self.current_token[1]
        self.advance()
        self.expect('EQUALS')
        expression = self.expression()
        # check is the var name is defined anywhere
        self.checkVarUse(var_name)
        # if it is, get the vars type
        var_type = self.get_variable_type(var_name)

        # check the type
        self.checkTypeMatch2(var_type, expression.value_type, var_name, expression)
        return AST.Assignment(var_name, expression)


    # TODO: Implement the logic to parse the if condition and blocks of code
    def if_stmt(self):
        """
        Parses an if-statement, with an optional else block.
        Example:
        if condition {
            # statements
        }
        else {
            # statements
        }
        TODO: Implement the logic to parse the if condition and blocks of code.
        """
        
        self.advance()  # skip if condition
        condition = self.boolean_expression()
        self.advance()   # move to next token
        then_block = self.block()

        else_block = None
        if self.current_token[0] == "ELSE":
            self.advance()   # skip else block
            # after if condition, there should be a left brace in this program
            self.expect('LBRACE')
            else_block = self.block()
            
        #??self.checkTypeMatch2()
        return AST.IfStatement(condition, then_block, else_block)

    # TODO: Implement the logic to parse while loops with a condition and a block of statements
    def while_stmt(self):
        """
        Parses a while-statement.
        Example:
        while condition {
            # statements
        }
        TODO: Implement the logic to parse while loops with a condition and a block of statements.
        """
        # self.checkTypeMatch2() #Fix this?
        self.advance() # skip while
        condition = self.boolean_expression()
        # again expect a Left Brace now
        self.expect("LBRACE")
        block = self.block()
        return AST.WhileStatement(condition, block)

    # TODO: Implement logic to capture multiple statements as part of a block
    def block(self):
        """
        Parses a block of statements. A block is a collection of statements grouped by `{}`.
        Example:
        
        x = 5
        y = 10
        
        TODO: Implement logic to capture multiple statements as part of a block.
        """
        self.enter_scope()
        statements = []
        # as long as the current token isnt the end of the if condition, keep adding to messages in current scope
        block_list = ["RBRACE"]
        while self.current_token[0] not in block_list: 
            statements.append(self.statement())
        self.advance()

        # if we see an Rbrace, exit the current scope
        self.exit_scope()
        return AST.Block(statements)

    # TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking
    def expression(self):
        """
        Parses an expression. Handles operators like +, -, etc.
        Example:
        x + y - 5
        TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking.
        """

        left = self.term()
        while self.current_token[0] in ['PLUS', 'MINUS']:
            op = self.current_token[0]
            self.advance()
            right = self.term()
            # check if left and right types match
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            left = AST.BinaryOperation(left, op, right, value_type=left.value_type)

        return left

    # TODO: Implement parsing for boolean expressions and check for type compatibility
    def boolean_expression(self):
        """
        Parses a boolean expression. These are comparisons like ==, !=, <, >.
        Example:
        x == 5
        TODO: Implement parsing for boolean expressions and check for type compatibility.
        """
        left = self.expression()
        boolean_list = ["EQ", "NEQ", "LESS", "GREATER"]
        if self.current_token[0] in boolean_list:
            op = self.current_token  # Capture the comparison operator
            self.advance()  # Move to the next token
            right = self.term()  # Parse the right-hand side expression
            # check if types match
            self.checkTypeMatch2(left.value_type, right.value_type, left, right )
            return AST.BooleanExpression(left, op, right)
        # write your code here, for reference check expression function
        return left
        
    # TODO: Implement parsing for multiplication and division and check for type compatibility
    def term(self):
        """
        Parses a term. A term consists of factors combined by * or /.
        Example:
        x * y / z
        TODO: Implement parsing for multiplication and division and check for type compatibility.
        """

        left = self.factor()
        operator_list = ["MULTIPLY", "DIVIDE"]
        while self.current_token[0] in operator_list:
            op = self.current_token  # Capture the operator (* or /)
            self.advance()  # Move to the next token
            right = self.factor()  # Parse the next factor
            left = AST.BinaryOperation(left, op, right, left.value_type)  # Create a binary operation node

            # check type match
            self.checkTypeMatch2(left.value_type, right.value_type, left, right )
        # write your code here, for reference check expression function
        return left

        
    def factor(self):
        if self.current_token[0] == 'NUMBER':
            # handle int
            num = self.current_token
            self.advance()  
            return AST.Factor(num, 'int')
        elif self.current_token[0] == 'FNUMBER':
            # handle float
            num = self.current_token
            self.advance()  
            return AST.Factor(num, 'float')
        elif self.current_token[0] == 'IDENTIFIER':
            var_name = self.current_token[1]  # Extract variable name
            # check if variable has ever been defined
            self.checkVarUse(var_name)
            self.advance()
            var_type = self.get_variable_type(var_name)
            # TODO: Ensure that you parse the identifier correctly, retrieve its type from the symbol table, and check if it has been declared in the current or any enclosing scopes.
            return AST.Factor(var_name, var_type)
        elif self.current_token[0] == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        else:
            raise ValueError(f"Unexpected token in factor: {self.current_token}")

    def function_call(self):
        func_name = self.current_token[1]
        self.advance()
        self.expect('LPAREN')
        args = self.arg_list()
        self.expect('RPAREN')

        return AST.FunctionCall(func_name, args)

    def arg_list(self):
        """
        Parses a list of function arguments.
        Example:
        (x, y + 5)
        """
        args = []
        if self.current_token[0] != 'RPAREN':
            args.append(self.expression())
            while self.current_token[0] == 'COMMA':
                self.advance()
                args.append(self.expression())

        return args

    def expect(self, token_type):
        if self.current_token[0] == token_type:
            self.advance()
        else:
            raise ValueError(f"Expected token {token_type}, but got {self.current_token[0]}")

    def peek(self):
        return self.tokens[0][0] if self.tokens else None
