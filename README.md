![Banner](images\abstract-technology-banner-background.jpg)

# 💻 LL(1) and SLR(1) Grammar Parser Implementation - Final Project 📜

## 📌 Group Member Information:
- **Full names:** Andrés Felipe Vélez Alvarez, Sebastián Salazar Henao, Simón Mazo Gómez
- **Class number:** Monday SI2002-1 (7308)


# 🛠️ Development Environment:

- **Operating system:** macOS Sonoma 14.7.2
- **Programming language:** Python (interpreter version: Python 3.13.2)
- **Tools used:** Visual Studio Code, Git, GitHub, GitHub Desktop

# 📖 About This Project:
This project implements parsers for LL(1) and SLR(1) grammars. It reads a grammar from a file (Grammars.txt), analyzes it, and checks whether it is LL(1) or SLR(1) through two different parsing techniques. It uses sets of FIRST and FOLLOW to construct parsing tables and automaton for these parsers.

# 🚀 How to Run the Implementation:
### Prerequisites:
Ensure you have **Python 3.13.2** installed. You can check your version with:
```sh
python3 --version
```

### Running the Code:
1. Clone this repository:
```sh
git clone https://github.com/Smg4315/Final-Project-LF
cd <the_folder_in_which_you_saved_the_repository>
```

2. Make sure that **the Grammars.txt file already contains the grammar and strings to be processed**. Then, run the Algorithm.py file:
```sh
python Algorithm.py
```
   - This will run the program that tells whether the grammar is LL(1), SLR(1), neither, or both.

# 🧑‍💻 Code Explanation

This program determines whether a context-free grammar is **LL(1)**, **SLR(1)**, or neither, and parses strings accordingly. The implementation includes all essential components for lexical analysis: grammar reading, FIRST and FOLLOW computation, table construction, and parsing simulation.


## 🔄 Program Flow

 **main()**
- Reads the grammar and strings from Grammars.txt.
- Builds FIRST and FOLLOW sets.
- Checks whether the grammar is:
  - LL(1): using parsing_table() and check_left_recursion().
  - SLR(1): using LR(0) items and build_slr1_table().
- Based on the classification, selects the appropriate parser (LL(1) or SLR(1)) to evaluate the input strings.


## 📄 Grammar Reading

**leer_gramatica(archivo, arreglo)**

- Parses the grammar rules and strings from a file.
- Grammar format: NonTerminal -> Production1 Production2 ...
- Strings are listed after a marker: <--- Strings --->


## 🔤 FIRST and FOLLOW

**FIRST(grammar)**
- Computes the FIRST set for all symbols.
- Handles epsilon (e) productions.
- Repeatedly updates FIRST sets until no more changes.

**FOLLOW(grammar, first)**
- Computes the FOLLOW sets using standard rules:
  - Adds $ to the start symbol.
  - Uses reverse traversal of productions.
  - Considers FIRST sets to propagate lookahead.


## 📊 Table Construction

**parsing_table(grammar, first, follow, tabla)**
- Builds the LL(1) parsing table.
- Checks for conflicts: if multiple productions appear in one cell, grammar is not LL(1).
- Supports epsilon (e) derivations and FOLLOW usage.

**build_lr0_automaton(grammar)**
- Constructs LR(0) automaton (states and transitions).
- Uses closure() and goto() functions to generate canonical items.

**build_slr1_table(states, transitions, grammar, follow)**
- Builds ACTION and GOTO tables for SLR(1) parsing.
- Handles:
  - *Shift*: on terminal symbols.
  - *Reduce*: on FOLLOW sets of completed items.
  - *Accept*: for augmented start rule.


## 🧠 Utility Functions

**fr_terminal(production, first)**
- Gets the FIRST set of a production to assist in table building.

**derives_epsilon(production, first)**
- Checks if a production derives epsilon (e).

**check_left_recursion(grammar)**
- Returns True if grammar has immediate left recursion (LL(1) conflict).


## ⚙️ Parsers

**LL1(table, string)**
- Implements standard predictive parser using a stack.
- Matches terminals, expands non-terminals using the parsing table.

**slr1_parser(string, action_table, goto_table, trace=True)**
- Simulates an SLR(1) parsing stack.
- Processes actions:
  - shift: Push symbol and state.
  - reduce: Pop symbols and apply rule.
  - accept: Input string is valid.
- Includes tracing support for debugging.


## 🖨️ Output Helpers

**print_slr1_table(action_table, goto_table)**
- Nicely prints the constructed SLR(1) ACTION and GOTO tables for visualization.


## 🔄 Grammar Augmentation

**augmented_grammar(grammar)**
- Adds augmented start rule S' → S for SLR(1) analysis.

**closure(I, grammar) and goto(I, symbol, grammar)**
- Build the closure and transitions of items in the LR(0) automaton.


## ✅ Summary

- This program provides a complete simulation environment for analyzing and testing grammars under LL(1) and SLR(1) parsing strategies. It automates table construction, conflict detection, and string parsing—all from a user-defined grammar file.
---
