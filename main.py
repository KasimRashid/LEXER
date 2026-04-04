# CPCS 323
# Kasim Rashid, Chau Phan, Jack Maden
# 4/5/2026
import re
from dataclasses import dataclass

@dataclass
class Token:
    """Represents a single lexical token with its metadata."""
    type: str
    value: str
    line: int
    col: int

class RAT26SLexer:
    """
    Lexical Analyzer for RAT26S. 
    Uses Regular Expressions to convert source code into a stream of tokens.
    """
    def __init__(self):
        # Reserved words that cannot be used as identifiers
        self.keywords = {
            "function", "integer", "boolean", "real", "if", 
            "otherwise", "fi", "while", "return", "read", 
            "write", "true", "false"
        }
        
        # Token specifications defining the grammar's terminal symbols
        self.token_spec = [
            ("COMMENT",   r"/\*.*?\*/"),                               
            ("REAL",      r"\d+\.\d+(?![A-Za-z0-9_.])"),               
            ("INTEGER",   r"(?<![A-Za-z0-9_.])\d+(?![A-Za-z0-9_.])"),  
            ("RELOP",     r"==|!=|<=|=>|<|>"),                         
            ("OPERATOR",  r"=|\+|-|\*|/"),                             
            ("ID",        r"(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9_]*"),  
            ("SEPARATOR", r"@|\(|\)|\{|\}|,|;"),                       
            ("NEWLINE",   r"\n"),                                     
            ("SKIP",      r"[ \t\r]+"),                               
            ("MISMATCH",  r"."),                                       
        ]
        
        # Compile the master regex pattern using named groups
        self.master_pat = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in self.token_spec), re.DOTALL)

    def tokenize(self, code: str):
        """Processes the input string and returns a list of Token objects."""
        tokens = []
        line, line_start = 1, 0
        for m in self.master_pat.finditer(code):
            kind, value = m.lastgroup, m.group()
            col = m.start() - line_start + 1
            
            if kind == "NEWLINE":
                line += 1
                line_start = m.end()
                continue
            if kind in ("SKIP", "COMMENT"): 
                continue
            
            # Check if an identifier is actually a keyword
            if kind == "ID" and value.lower() in self.keywords:
                kind, value = "KEYWORD", value.lower()
            
            if kind == "MISMATCH": 
                continue
                
            tokens.append(Token(kind, value, line, col))
        return tokens

class Node:
    """Represents a node in the Parse Tree."""
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []

class RAT26SParser:
    """
    Recursive Descent Parser for the RAT26S language.
    Outputs the production rules applied during the derivation process.
    """
    def __init__(self, tokens, output_file):
        self.tokens = tokens
        self.pos = 0
        self.output_file = output_file

    def _print_production(self, rule):
        """Helper to log the grammar production rule to the output file."""
        self.output_file.write(f"    {rule}\n")

    def current_token(self):
        """Returns the token currently being pointed to by the cursor."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, expected_value=None, expected_type=None):
        """
        Validates the current token against expected values/types.
        Advances the cursor if valid, otherwise raises a Syntax Error.
        """
        token = self.current_token()
        if not token: 
            raise SyntaxError("Unexpected End of Input")
        
        if (expected_value and token.value == expected_value) or (expected_type and token.type == expected_type):
            self.output_file.write(f"Token: {token.type:<12} Lexeme: {token.value}\n")
            self.pos += 1
            return token
        
        raise SyntaxError(f"Expected {expected_value or expected_type} but found {token.value} at line {token.line}")

    # --- Grammar Rules Implementation ---
    # R1. <Rat26S> ::= @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @
    def parse_rat26s(self):
        """<Rat26S> -> @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @"""
        self.output_file.write("<Rat26S> -> @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @\n")
        node = Node("<Rat26S>")
        node.children.append(self.match(expected_value="@"))
        node.children.append(self.parse_opt_function_definitions())
        node.children.append(self.match(expected_value="@"))
        node.children.append(self.parse_opt_declaration_list())
        node.children.append(self.match(expected_value="@"))
        node.children.append(self.parse_statement_list())
        node.children.append(self.match(expected_value="@"))
        return node

    # R2. <Opt Function Definitions> ::= <Function Definitions> | <Empty>
    def parse_opt_function_definitions(self):
        """Handles optional function definitions at the start of the program."""
        token = self.current_token()
        if token and token.value == "function":
            self._print_production("<Opt Function Definitions> -> <Function Definitions>")
            return self.parse_function_definitions()
        self._print_production("<Opt Function Definitions> -> <Empty>")
        return Node("<Empty>")

    # R3. <Function Definitions> ::= <Function> | <Function> <Function Definitions>
    def parse_function_definitions(self):
        """<Function Definitions> -> <Function> | <Function> <Function Definitions>"""
        self._print_production("<Function Definitions> -> <Function> | <Function> <Function Definitions>")
        node = Node("<Function Definitions>")
        node.children.append(self.parse_function())
        if self.current_token() and self.current_token().value == "function":
            node.children.append(self.parse_function_definitions())
        return node

    # R4. <Function> ::= function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>
    def parse_function(self):
        """<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>"""
        self._print_production("<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        node = Node("<Function>")
        node.children.append(self.match(expected_value="function"))
        node.children.append(self.match(expected_type="ID"))
        node.children.append(self.match(expected_value="("))
        node.children.append(self.parse_opt_parameter_list())
        node.children.append(self.match(expected_value=")"))
        node.children.append(self.parse_opt_declaration_list())
        node.children.append(self.parse_body())
        return node

    # R5. <Opt Parameter List> ::= <Parameter List> | <Empty>
    def parse_opt_parameter_list(self):
        """Checks for parameters within function signatures."""
        if self.current_token() and self.current_token().type == "ID":
            self._print_production("<Opt Parameter List> -> <Parameter List>")
            return self.parse_parameter_list()
        self._print_production("<Opt Parameter List> -> <Empty>")
        return Node("<Empty>")

    # R6. <Parameter List> ::= <Parameter> | <Parameter> , <Parameter List>
    def parse_parameter_list(self):
        """Handles list of parameters separated by commas."""
        self._print_production("<Parameter List> -> <Parameter> | <Parameter> , <Parameter List>")
        node = Node("<Parameter List>")
        node.children.append(self.parse_parameter())
        if self.current_token() and self.current_token().value == ",":
            node.children.append(self.match(expected_value=","))
            node.children.append(self.parse_parameter_list())
        return node

    # R7. <Parameter> ::= <IDs > <Qualifier>
    def parse_parameter(self):
        """<Parameter> -> <IDs> <Qualifier>"""
        self._print_production("<Parameter> -> <IDs> <Qualifier>")
        node = Node("<Parameter>")
        node.children.append(self.parse_ids())
        node.children.append(self.parse_qualifier())
        return node

    # R8. <Qualifier> ::= integer | boolean | real
    def parse_qualifier(self):
        """Identifies types: integer, boolean, or real."""
        token = self.current_token()
        self._print_production(f"<Qualifier> -> {token.value}")
        return Node("<Qualifier>", [self.match(expected_value=token.value)])

    # R9. <Body> ::= { < Statement List> }
    def parse_body(self):
        """<Body> -> { <Statement List> }"""
        self._print_production("<Body> -> { <Statement List> }")
        node = Node("<Body>")
        node.children.append(self.match(expected_value="{"))
        node.children.append(self.parse_statement_list())
        node.children.append(self.match(expected_value="}"))
        return node

    # R10. <Opt Declaration List> ::= <Declaration List> | <Empty>
    def parse_opt_declaration_list(self):
        """Handles optional variable declarations."""
        token = self.current_token()
        if token and token.value in ("integer", "boolean", "real"):
            self._print_production("<Opt Declaration List> -> <Declaration List>")
            return self.parse_declaration_list()
        self._print_production("<Opt Declaration List> -> <Empty>")
        return Node("<Empty>")

    # R11. <Declaration List> := <Declaration> ; | <Declaration> ; <Declaration List>
    def parse_declaration_list(self):
        """<Declaration List> -> <Declaration> ; | <Declaration> ; <Declaration List>"""
        self._print_production("<Declaration List> -> <Declaration> ; | <Declaration> ; <Declaration List>")
        node = Node("<Declaration List>")
        node.children.append(self.parse_declaration())
        node.children.append(self.match(expected_value=";"))
        if self.current_token() and self.current_token().value in ("integer", "boolean", "real"):
            node.children.append(self.parse_declaration_list())
        return node
    
    # R12. <Declaration> ::= <Qualifier > <IDs>
    def parse_declaration(self):
        """<Declaration> -> <Qualifier> <IDs>"""
        self._print_production("<Declaration> -> <Qualifier> <IDs>")
        return Node("<Declaration>", [self.parse_qualifier(), self.parse_ids()])

    # R13. <IDs> ::= <Identifier> | <Identifier>, <IDs>
    def parse_ids(self):
        """Parses one or more identifiers separated by commas."""
        self._print_production("<IDs> -> <Identifier> | <Identifier> , <IDs>")
        node = Node("<IDs>")
        node.children.append(self.match(expected_type="ID"))
        if self.current_token() and self.current_token().value == ",":
            node.children.append(self.match(expected_value=","))
            node.children.append(self.parse_ids())
        return node

    # R14. <Statement List> ::= <Statement> | <Statement> <Statement List>
    def parse_statement_list(self):
        """Recursive parsing of statements within a block."""
        self._print_production("<Statement List> -> <Statement> | <Statement> <Statement List>")
        node = Node("<Statement List>")
        node.children.append(self.parse_statement())
        token = self.current_token()
        # Lookahead to check if another statement follows
        if token and (token.value in ("{", "if", "return", "read", "write", "while") or token.type == "ID"):
            node.children.append(self.parse_statement_list())
        return node

    # R15. <Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>
    def parse_statement(self):
        """Branches based on the starting token of a statement."""
        token = self.current_token()
        if token.value == "{": return self.parse_compound()
        if token.type == "ID": return self.parse_assign()
        if token.value == "if": return self.parse_if()
        if token.value == "return": return self.parse_return()
        if token.value == "write": return self.parse_print()
        if token.value == "read": return self.parse_scan()
        if token.value == "while": return self.parse_while()
        raise SyntaxError(f"Line {token.line}: Unexpected start of statement '{token.value}'")

    # R16. <Compound> ::= { <Statement List> }
    def parse_compound(self):
        """Parses a block of statements wrapped in curly braces."""
        self._print_production("<Statement> -> <Compound>")
        self._print_production("<Compound> -> { <Statement List> }")
        node = Node("<Compound>")
        node.children.append(self.match(expected_value="{"))
        node.children.append(self.parse_statement_list())
        node.children.append(self.match(expected_value="}"))
        return node

    # R17. <Assign> ::= <Identifier> = <Expression> ;
    def parse_assign(self):
        """<Assign> -> <Identifier> = <Expression> ;"""
        self._print_production("<Statement> -> <Assign>")
        self._print_production("<Assign> -> <Identifier> = <Expression> ;")
        node = Node("<Assign>")
        node.children.append(self.match(expected_type="ID"))
        node.children.append(self.match(expected_value="="))
        node.children.append(self.parse_expression())
        node.children.append(self.match(expected_value=";"))
        return node

    # R18. <If> ::= if ( <Condition> ) <Statement> fi |
    # if ( <Condition> ) <Statement> otherwise <Statement> fi
    def parse_if(self):
        """Parses If-statements with optional 'otherwise' (else) branch."""
        self._print_production("<Statement> -> <If>")
        self._print_production("<If> -> if ( <Condition> ) <Statement> fi | if ( <Condition> ) <Statement> otherwise <Statement> fi")
        node = Node("<If>")
        node.children.append(self.match(expected_value="if"))
        node.children.append(self.match(expected_value="("))
        node.children.append(self.parse_condition())
        node.children.append(self.match(expected_value=")"))
        node.children.append(self.parse_statement())
        if self.current_token() and self.current_token().value == "otherwise":
            node.children.append(self.match(expected_value="otherwise"))
            node.children.append(self.parse_statement())
        node.children.append(self.match(expected_value="fi"))
        return node

    # R19. <Return> ::= return ; | return <Expression> ;
    def parse_return(self):
        """Parses return statements with or without an expression."""
        self._print_production("<Statement> -> <Return>")
        self._print_production("<Return> -> return ; | return <Expression> ;")
        node = Node("<Return>")
        node.children.append(self.match(expected_value="return"))
        if self.current_token() and self.current_token().value != ";":
            node.children.append(self.parse_expression())
        node.children.append(self.match(expected_value=";"))
        return node

    # R20. <Print> ::= write ( <Expression>);
    def parse_print(self):
        """<Print> -> write ( <Expression> ) ;"""
        self._print_production("<Print> -> write ( <Expression> ) ;")
        node = Node("<Print>")
        node.children.append(self.match(expected_value="write"))
        node.children.append(self.match(expected_value="("))
        node.children.append(self.parse_expression())
        node.children.append(self.match(expected_value=")"))
        node.children.append(self.match(expected_value=";"))
        return node

    # R21. <Scan> ::= read ( <IDs> );
    def parse_scan(self):
        """<Scan> -> read ( <IDs> ) ;"""
        self._print_production("<Scan> -> read ( <IDs> ) ;")
        node = Node("<Scan>")
        node.children.append(self.match(expected_value="read"))
        node.children.append(self.match(expected_value="("))
        node.children.append(self.parse_ids())
        node.children.append(self.match(expected_value=")"))
        node.children.append(self.match(expected_value=";"))
        return node

    # R22. <While> ::= while ( <Condition> ) <Statement>
    def parse_while(self):
        """<While> -> while ( <Condition> ) <Statement>"""
        self._print_production("<While> -> while ( <Condition> ) <Statement>")
        node = Node("<While>")
        node.children.append(self.match(expected_value="while"))
        node.children.append(self.match(expected_value="("))
        node.children.append(self.parse_condition())
        node.children.append(self.match(expected_value=")"))
        node.children.append(self.parse_statement())
        return node

    # R23. <Condition> ::= <Expression> <Relop> <Expression>
    def parse_condition(self):
        """Condition logic supporting standalone expressions or relational comparisons."""
        self._print_production("<Condition> -> <Expression> [ <Relop> <Expression> ]")
        node = Node("<Condition>")
        node.children.append(self.parse_expression())
        token = self.current_token()
        if token and token.type == "RELOP":
            node.children.append(self.parse_relop())
            node.children.append(self.parse_expression())
        return node

    # R24. <Relop> ::= == | != | > | < | <= | =>
    def parse_relop(self):
        """Matches a relational operator (==, !=, etc.)."""
        token = self.current_token()
        if token and token.type == "RELOP":
            self._print_production(f"<Relop> -> {token.value}")
            return Node("<Relop>", [self.match(expected_type="RELOP")])
        else:
            raise SyntaxError(f"Line {token.line}: Expected RELOP but found {token.type} ('{token.value}')")

    # R25. <Expression> ::= <Expression> + <Term> | <Expression> - <Term> | <Term>
    def parse_expression(self):
        """Standard arithmetic expression with term and expression prime for precedence."""
        self._print_production("<Expression> -> <Term> <Expression Prime>")
        node = Node("<Expression>")
        node.children.append(self.parse_term())
        node.children.append(self.parse_expression_prime())
        return node

    def parse_expression_prime(self):
        """Handles addition and subtraction (left-associative)."""
        token = self.current_token()
        if token and token.value in ("+", "-"):
            self._print_production(f"<Expression Prime> -> {token.value} <Term> <Expression Prime>")
            node = Node("<Expression Prime>")
            node.children.append(self.match(expected_value=token.value))
            node.children.append(self.parse_term())
            node.children.append(self.parse_expression_prime())
            return node
        self._print_production("<Expression Prime> -> ε")
        return Node("<Empty>")
    
    # R26. <Term> ::= <Term> * <Factor> | <Term> / <Factor> | <Factor>
    def parse_term(self):
        """Groups factors into terms."""
        self._print_production("<Term> -> <Factor> <Term Prime>")
        node = Node("<Term>")
        node.children.append(self.parse_factor())
        node.children.append(self.parse_term_prime())
        return node

    def parse_term_prime(self):
        """Handles multiplication and division (higher precedence than + and -)."""
        token = self.current_token()
        if token and token.value in ("*", "/"):
            self._print_production(f"<Term Prime> -> {token.value} <Factor> <Term Prime>")
            node = Node("<Term Prime>")
            node.children.append(self.match(expected_value=token.value))
            node.children.append(self.parse_factor())
            node.children.append(self.parse_term_prime())
            return node
        self._print_production("<Term Prime> -> ε")
        return Node("<Empty>")

    # R27. <Factor> ::= - <Primary> | <Primary>
    def parse_factor(self):
        """Handles unary minus and basic primary elements."""
        token = self.current_token()
        if token and token.value == "-":
            self._print_production("<Factor> -> - <Primary>")
            return Node("<Factor>", [self.match(expected_value="-"), self.parse_primary()])
        self._print_production("<Factor> -> <Primary>")
        return Node("<Factor>", [self.parse_primary()])

    def parse_expression_list(self):
        """Used for function calls: matches one or more expressions separated by commas."""
        self._print_production("<Expression List> -> <Expression> | <Expression> , <Expression List>")
        node = Node("<Expression List>")
        node.children.append(self.parse_expression())
        if self.current_token() and self.current_token().value == ",":
            node.children.append(self.match(expected_value=","))
            node.children.append(self.parse_expression_list())
        return node

    # R28. <Primary> ::= <Identifier> | <Integer> | <Identifier> ( <IDs> ) | ( <Expression> ) |
    # <Real> | true | false
    def parse_primary(self):
        """The base unit of expressions: IDs, Numbers, Booleans, or parenthesized expressions."""
        token = self.current_token()
        node = Node("<Primary>")
        
        if token.type == "ID":
            id_token = self.match(expected_type="ID")
            # Determine if this is a variable or a function call
            if self.current_token() and self.current_token().value == "(":
                self._print_production("<Primary> -> <Identifier> ( <Expression List> )")
                node.children.extend([id_token, self.match(expected_value="("), self.parse_expression_list(), self.match(expected_value=")")])
            else:
                self._print_production("<Primary> -> <Identifier>")
                node.children.append(id_token)
        elif token.type in ("INTEGER", "REAL"):
            self._print_production(f"<Primary> -> <{token.type.capitalize()}>")
            node.children.append(self.match(expected_type=token.type))
        elif token.value == "(":
            self._print_production("<Primary> -> ( <Expression> )")
            node.children.extend([self.match(expected_value="("), self.parse_expression(), self.match(expected_value=")")])
        elif token.value in ("true", "false"):
            self._print_production(f"<Primary> -> {token.value}")
            node.children.append(self.match(expected_value=token.value))
        return node

def main():
    """Main execution entry point."""
    input_file = input("Enter input RAT26S file: ").strip()
    output_file = input("Enter output result file (.txt): ").strip()
    try:
        # utf-8-sig handles potential BOM from some text editors
        with open(input_file, "r", encoding="utf-8-sig") as f:
            code = f.read()
            
        lexer = RAT26SLexer()
        tokens = lexer.tokenize(code)
        
        with open(output_file, "w", encoding="utf-8") as out:
            parser = RAT26SParser(tokens, out)
            parser.parse_rat26s()
            
        print(f"Success! Output written to {output_file}")
    except Exception as e:
        print(f"Error during parsing: {e}")

if __name__ == "__main__":
    main()