# Rat26S Compiler Project (CPSC 323 - Spring 2026)

## Project Overview
This project implements components of a compiler for the **Rat26S programming language**, a simple imperative language designed for educational purposes.

The project is divided into three main parts:
1. **Lexical Analyzer (Lexer)**
2. **Syntax Analyzer (Parser)**
3. **(Optional/Advanced) Semantic Analysis / Code Generation**

Each group member is responsible for one major component.

---

## Group Members
- Kasim Rashid
- Chau Phan
- Jack Madaen 

---

## About Rat26S
Rat26S is a simplified programming language with:
- Clear syntax defined using BNF
- Basic data types: `integer`, `boolean`, `real`
- Control structures: `if`, `while`
- I/O operations: `read`, `write`
- Function definitions and calls

---

## Features Implemented

### 1. Lexical Analyzer (Implemented)
- Tokenizes input source code into:
  - Identifiers
  - Keywords
  - Integers
  - Reals
  - Operators
  - Separators
- Ignores:
  - Whitespaces (spaces, tabs, newlines)
  - Comments (`/* comment */`)
- Validates token formats

---

### 2. Syntax Analyzer (Implementing)
- Implements a **top-down parser** (Recursive Descent)
- Uses the provided Rat26S grammar
- Handles:
  - Function definitions
  - Declarations
  - Statements (assignment, if, while, etc.)
- Detects syntax errors and reports them

---

### 3. Semantic Rules (Implementing)
- Variables must be declared before use
- Type checking:
  - No mixing types (e.g., integer → real)
  - No arithmetic on booleans
- Function arguments passed by value

---