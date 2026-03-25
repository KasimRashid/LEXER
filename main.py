# CPCS 323
# Kasim Rashid, Chau Phan, Jack Maden
# 2/24/2026
import re
from dataclasses import dataclass

# the Token structure
@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

# RAT26S Lexer
class RAT26SLexer:
    def __init__(self):
        # Keywords 
        self.keywords = {
            "function", "integer", "boolean", "real",
            "if", "otherwise", "fi",
            "while", "return",
            "read", "write",
            "true", "false"
        }

        # Token specifications (order does  matters)
        self.token_spec = [
            ("COMMENT",   r"/\*.*?\*/"),
            ("REAL",      r"\d+\.\d+(?![A-Za-z0-9_.])"), 
            ("INTEGER",   r"(?<![A-Za-z0-9_.])\d+(?![A-Za-z0-9_.])"),
            ("ID",        r"(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9_]*"),
            ("RELOP",     r"==|!=|<=|=>|<|>"),
            ("OPERATOR",  r"=|\+|-|\*|/"),
            ("SEPARATOR", r"@|\(|\)|\{|\}|,|;"),
            ("NEWLINE",   r"\n"),
            ("SKIP",      r"[ \t\r]+"),
            ("MISMATCH",  r"."),
        ]

        # Build master regex
        self.master_pat = re.compile(
            "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.token_spec),
            re.DOTALL
        )


    # The Tokenizer
    def tokenize(self, code: str):
        tokens = []
        line = 1
        line_start = 0

        for m in self.master_pat.finditer(code):
            kind = m.lastgroup
            value = m.group()
            col = m.start() - line_start + 1

            # Handle newlines
            if kind == "NEWLINE":
                line += 1
                line_start = m.end()
                continue

            # Ignore whitespace and comments
            if kind in ("SKIP", "COMMENT"):
                continue

            # Case-insensitive keywords
            if kind == "ID":
                low = value.lower()
                if low in self.keywords:
                    kind = "KEYWORD"
                    value = low

            # Illegal characters
            if kind == "MISMATCH":
                print(f"Lexer Error: Illegal character {value!r} at line {line}, col {col}")
                continue

            tokens.append(Token(kind, value, line, col))

        return tokens

# Basic Node Class
class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []

    def display(self, level=0):
        indent = "  " * level
        print(f"{indent}{self.name}")
        for child in self.children:
            if isinstance(child, Node):
                child.display(level + 1)
            else:
                print(f"{indent}  TOKEN: {child.value} ({child.type})")

# RAT26S Parser
class RAT26SParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, expected_value=None, expected_type=None):
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected End of Input")
        
        # Match by specific value (like '@' or 'if') or by type (like 'ID')
        if (expected_value and token.value == expected_value) or \
           (expected_type and token.type == expected_type):
            self.pos += 1
            return token
        else:
            raise SyntaxError(f"Expected {expected_value or expected_type} but found {token.value} at line {token.line}")
    
    # R1. <Rat26S> ::= @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @
    def parse_rat26s(self):
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
        node = Node("<Opt Function Definitions>")
        token = self.current_token()
        # Lookahead: Does it start with 'function'?
        if token and token.value == "function":
            node.children.append(self.parse_function_definitions())
        else:
            node.children.append(Node("<Empty>"))
        return node

# File I/O stuff
def read_input_file(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_output_file(path, tokens):
    with open(path, "w", encoding="utf-8-sig") as f:

        f.write(" RAT26S LEXICAL ANALYSIS OUTPUT\n")
        #f.write(the lex\n")
        f.write("Line  Col   TokenType   Lex\n")
        f.write("----------------------------------------\n")

        for t in tokens:
            f.write(f"{t.line:<5} {t.col:<5} {t.type:<11} {t.value}\n")

        f.write("----------------------------------------\n")
        f.write(f"Total Tokens: {len(tokens)}\n")


# Main Program
def main():
    print("<><><><><><><><><><><><><><><><><><><><>")
    print("        RAT26S LEXICAL ANALYZER")
    print("<><><><><><><><><><><><><><><><><><><><>")

    input_file = input("Enter input RAT26S file path: ").strip()
    output_file = input("Enter output token file path: ").strip()

    try:
        # Read source file
        code = read_input_file(input_file)

        # Lexical analysis
        lexer = RAT26SLexer()
        tokens = lexer.tokenize(code)

        # Write output file
        write_output_file(output_file, tokens)

        print("\n Lexical analysis completed successfully.")
        print(f" Input file : {input_file}")
        print(f" Output file: {output_file}")
        print(f" Tokens generated: {len(tokens)}")

    except FileNotFoundError:
        print("\n Error: Input file not found.")
    except SyntaxError as e:
        print("\n Lexer Error:", e)
    except Exception as e:
        print("\n Unexpected Error:", e)


if __name__ == "__main__":
    main()
