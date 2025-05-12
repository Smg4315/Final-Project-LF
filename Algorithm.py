# We import the libraries that will be used. In this case, we will use the sys library to handle errors
from collections import defaultdict
from collections import namedtuple
import sys

Item = namedtuple('Item', ['lhs', 'rhs', 'dot'])  # Ej: Item("A", ["B", "C"], 1)

# We define the main function that will create at the moment a dictionary with the specified grammar.
def main():

    # We create the dictionary and fill it with the respective grammar
    strings = [] # We create an empty array that will be used to store the strings that we are going to analyze
    LL = False # We create this bools to clasify wether a grammmar is LL(1) or SLR(1) to implement it corresponding parser or both
    LR = False # supossing

    gramatica = leer_gramatica('Grammars.txt', strings)
    
    # We generate FIRST AND FOLLOW sets takin into account the specific grammar
    first_sets = FIRST(gramatica)
    follow_sets = FOLLOW(gramatica, first_sets)

    # We create a dictionary of dictionaries to store the parsing table (globaly - LL(1)) 
    tabla = defaultdict(lambda: defaultdict(list)) 

    # Verificar si es LL(1)
    tabla_ll1 = defaultdict(lambda: defaultdict(list))
    if not check_left_recursion(gramatica) and parsing_table(gramatica, first_sets, follow_sets, tabla_ll1):
        LL = True

    # Verificar si es SLR(1)
    states, transitions = build_lr0_automaton(gramatica)
    action_table, goto_table, is_slr1 = build_slr1_table(states, transitions, gramatica, follow_sets)
    if is_slr1:
        LR = True

    # Caso 1: ambas
    if LL and LR:
        while True:
            print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
            option = input().strip().upper()
            if option == 'T':
                for cadena in strings:
                    print("yes" if LL1(tabla_ll1, cadena) else "no")
            elif option == 'B':
                for cadena in strings:
                    print("yes" if slr1_parser(cadena, action_table, goto_table, trace=False) else "no")
            elif option == 'Q':
                break
            else:
                continue

    # Caso 2: solo LL(1)
    elif LL and not LR:
        print("Grammar is LL(1).")
        for cadena in strings:
            print("yes" if LL1(tabla_ll1, cadena) else "no")

    # Caso 3: solo SLR(1)
    elif LR and not LL:
        print("Grammar is SLR(1).")
        for cadena in strings:
            print("yes" if slr1_parser(cadena, action_table, goto_table, trace=False) else "no")

    # Caso 4: ninguna
    else:
        print("Grammar is neither LL(1) nor SLR(1).")

# We define the function that will read the grammar from the file and create a dictionary with it.
def leer_gramatica(archivo, arreglo):

    # We try to open the file and read its contents takin into account the posible errors that may occur
    try:
        # We open the file in read mode
        with open(archivo, 'r') as f:
            n = int(f.readline().strip())  # Read the number of rules deleting empty spaces
            gramatica = {} # We create an empty dictionary that will be fullfilled with the grammar 

            # We read line by line the grammar rules and add them into the dictionary
            for _ in range(n):
                
                # Read the line and delete empty spaces (beggining and end)
                linea = f.readline().strip()

                # We verify that the line contains a grammar rule
                if '->' in linea:

                    # We split the line into the left and right sides of the rule to separate the productions takin into account the symbol '->'
                    lado_izq, lado_der = linea.split('->')

                    # We delete empty spaces (beggining and end) in the left and right sides of the rule and we assign it corresponding function forward
                    no_terminal = lado_izq.strip()

                    # This is an array of strings that will be used to store the alternatives of the grammar rule
                    alternativas_raw = lado_der.strip().split()

                    # We separate each production in singular terms
                    alternativas = [list(alt) for alt in alternativas_raw] # ["AB2"] -> ["A", "B", "2"]

                    # We verify that the non-terminal is not already in the dictionary, if not we create a new entry for it
                    if no_terminal not in gramatica:
                        gramatica[no_terminal] = []

                    # We add the correspondive alternatives to its terminal (in a singular way)
                    for alt in alternativas:
                        gramatica[no_terminal].append(alt)

                else:
                    print(f"Error: La regla '{linea}' no es válida. se esperaba 'no_terminal -> producciones'.\n")
                    sys.exit(1)
        
            # now we read the strings that we are going to analyze

            # Skip the lines until the "Strings to be analyzed" section
            while True:
                linea = f.readline().strip()
                if linea == "<--- Strings --->":
                    break  # Found the section, break the loop

            # Read the strings and store them in the arreglo as a list of strings
            while True:
                linea = f.readline().strip()
                if not linea:
                    break  # End of the strings section
                arreglo.append(linea)

            return gramatica
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'Grammars.txt'.")
        sys.exit(1)

# We create the function to generate the FIRST sets it recives the dictionary that contains the grammar. 
def FIRST(grammar):

    # We create another dictionary that will contain the FIRST set of each non-terminal where each key is the non terminal and it value its the respetive FIRST set
    first = defaultdict(set)

    # Boolean to know when to stop (there is no more ads to any FIRSt set)
    changed = True

    # Definition of the FIRST sets of terminals

    for nt in grammar: # For each production rule in the grammar (each NT) H -> [['+', 'T', 'H'], ['e']] iteration on the dictionary
        for production in grammar[nt]: # For each array of values in the dictionary [ ['+', 'T', 'H'], ['e'] ] (will be 1 iteration)
            for chunk in production: # For each production rule ['+', 'T', 'H'] and then['e']
                for symbol in chunk: # We check each symbol of the productions to determine wich is a terminal and wich is not '+' then 'T' and then 'H'
                    if not symbol.isupper():  # is terminal or special symbol
                        first[symbol].add(symbol) # We add it to the First dictionary with the same symbol


    # Now we are finding the FIRST sets of the NON-TERMINAL taking into account the FIRST of the terminals
    # we'll repeat this procces til there is no more changes made (this makes sure all the NT end up with it FIRST set)
    # This procces migth be repeated multiple times because the first thing that a NT could be another NT that is not created yet, so we repeat this til the NT that we need is created
    while changed:
        changed = False # We initializate this bool

        for nt in grammar: # We iterate over the dictionary that represents each NT H -> [['+', 'T', 'H'], ['e']]
            for production in grammar[nt]: # We go inside the values of each NT in the dictionary ['+', 'T', 'H'] then ['e']

                i = 0 #This is the index of the chars of each production ['+', 'T', 'H'], '+' = 0, 'T' = 1 ...
                nullable = True # we asume that all NT produce the empty string
                before = len(first[nt]) # We store the length of the FIRST set of the NT that we are seeing and creating it (how many nt we are going to analyze) 

                # we check if there are still productions and we take into account the null production for the nonterminals
                while i < len(production) and nullable:
                    chunk = production[i]  # We assign the value of the chunk in wich we are rn.

                    # We evaluate each symbol of the production takin into account the rules of FIRST set
                    for symbol in chunk:
                            first[nt].update(first[symbol] - {'e'}) # We assign the actual symbol the first symbol of it production rule (if it has been not created we wait for a future iteration and create the specific nt that is left)
                            if 'e' in first[symbol]: # If the first symbol of the rule contains e string we continue with the other symbol til it dont or til there is no more symbols
                                continue
                            else: # If it doesnt, our work with the specific rule is done, and we can check the other rule
                                nullable = False
                                break
                    if nullable:
                         i += 1 

                if nullable: # If all the chars of a productions contains the e, or me are reading the e, we add it to the FIRST set.
                    first[nt].add('e')

                if len(first[nt]) > before: # If there were changes, we continue
                    changed = True

    return first # After we finish we return the respective dictionary

# We create the function to generate the FOLLOW sets it recives the dictionary that contains the grammar, the dictionary of the FIRST set and the start symbol (Always S). 
def FOLLOW(grammar, first):

    # We create another dictionary that will representate the FOLLOW sets of each NT
    follow = defaultdict(set)
    follow['S'].add('$') # We add at the beggining the '$' to the initial symbol

    # We create a boolean to know when to stop (there is no more ads to any FOLLOW set)
    changed = True
    while changed: # The process will be repeated until there are no more changes

        # We assume that there are no changes at the beggining
        changed = False

        for nt in grammar: # We iterate over the dictionary that represents each NT H -> [['+', 'T', 'H'], ['e']]
            for production in grammar[nt]: # We go inside the values of each NT in the dictionary ['+', 'T', 'H'] then ['e']
                
                # We are assigning a copy of what is on the FOLLOW set of the NT that we are seeing to the trailer variable (to use it later)
                trailer = follow[nt].copy() 

                # This trailer variable will be used to add the respective symbols to the FOLLOW set of the NT that we are seeing
                # taking into account the 3 rules of the FOLLOW set 

                # We are reverse the production to check the symbols from right to left (its more convenient for the FOLLOW)
                for chunk in reversed(production):
                    for symbol in reversed(chunk):

                        # We check if the symbol is a terminal or a special symbol
                        if symbol.isupper(): # If it is a non-terminal

                            # We add to the FOLLOW of the nt 
                            before = len(follow[symbol]) # We save the size of it to check if it were changed
                            follow[symbol].update(trailer) # We update the trailer taking into account the last symbol (that is really the next)

                            # WE prepare the FOLLOW (trailer) for the next iteration

                            if 'e' in first[symbol]:
                                trailer.update(first[symbol] - {'e'}) # If there is an e in the first set we put it off for the next rule (withouth delenting the FOLLOW of the producer)
                            else:
                                trailer = first[symbol].copy() # Else we just put the first set of the symbol to the next symbol to use it (Deleting the FOLLOW of the producer)
                            if len(follow[symbol]) > before: # If there were changes, we continue
                                changed = True
                        else:
                            trailer = {symbol} # If it is a terminal or special symbol we just put it in the trailer variable to use it for the next nt, because this terminal will be the FOLLOW
    return follow

# We create the function to generate the parsing table it recives the dictionary that contains the grammar, the dictionary of the FIRST set and the FOLLOW set.
# This function is used to produce the parsing table
def parsing_table(grammar, first, follow, tabla):

 # We iterate the grammar 
 for nt in grammar: # Iterate over the grammar dictionary
     for production in grammar[nt]: # For each production rule of the NT
         
         if 'e' in first[nt]: # We verify if the FIRST set of the NT contains e (in case that yes, we have to check the terminals of the FOLLOW set)
             if production != ['e']: # We check if the production rule contains e
                 
                 # If it is not a null production:

                 # We are going to iterate over the symbols of the first set of the NT
                 for symbol in first[nt]:
                     if symbol != 'e': #it must be different from e because e is not contempled in parsing table
                             
                             # We get the first terminal of the production rule, we will take into account the posible cases (its jus a nt that produce the terminal)
                             fr = fr_terminal(production, first)
                             
                             if (symbol in fr): # Here´s where we check if the production really produces the terminal that we need
                                 
                                 if not tabla[nt][symbol]: # If the parsing table is empty we add the production rule
                                     tabla[nt][symbol] = production
                                 else: # If the parsing table is not empty we have to check if the production rule is the same as the one that we are going to add
                                     if tabla[nt][symbol] != production: # If the production rule is not the same that was already there, then the grammar is not LL(1).
                                         return False# the function will return None
             
             # We only take into account the FOLLOW set if the production rule is a null production because its the only posible case
             else: # If the production rule is a null production, we have to add each terminal of the FOLLOW set to the parsing table
                 for symbol in follow[nt]:
                     # if the table is empty we add the production rule
                     if not tabla[nt][symbol]: 
                         tabla[nt][symbol] = production
                     else:
                         return False

         # If the FIRST set of the NT does not contain e, we dont take into account the FOLLOW set                      
         else:

             # We are going to iterate over the symbols of the first set of the NT
             for symbol in first[nt]:

                     # The same process as before, we get the first terminal of the production rule 
                     fr = fr_terminal(production, first)
                     
                     if (symbol in fr): # Here´s where we check if the production really produces the terminal that we need
                         # We check if the parsing table is empty, if it is we add the production rule, 
                         if not tabla[nt][symbol]: 
                             tabla[nt][symbol] = production
                         else:
                             if tabla[nt][symbol] != production: # If the production rule is not the same that was already there, then the grammar is not LL(1).
                                 return False # the function will return None
          
         # We are checking the cases where the production rule is a null production (its like to do it again but not neccesary with only e productions)
         if derives_epsilon(production, first):
             for symbol in follow[nt]:
                 if not tabla[nt][symbol]:
                     tabla[nt][symbol] = production # We add the production rule (not neccesarily null production)
                 else:
                     if tabla[nt][symbol] != production:
                         return False
 return True

# Get the FIRST set for a production - to verify if the production rule produces the terminal that we need
def fr_terminal(production, first):
    # We initialize the FIRST set with the first terminal of the production
    fr = set()
    
    for symbol in production:
        if not symbol.isupper():  # terminal symbol
            fr.add(symbol)  # add terminal symbol to FIRST set
            break
        else:  # non-terminal symbol
            fr.update(first[symbol])  # add FIRST of non-terminal to FIRST set
            if 'e' not in first[symbol]:  # If the non-terminal doesn't derive epsilon, break
                break
    
    return fr  # return the FIRST set for the production
     
# We create the function to check if a production derives epsilon (e) or not (set of nt) - to take into account special cases
# This function is used to produce the parsing table
def derives_epsilon(production, first):
    for symbol in production:
        if symbol not in first or 'e' not in first[symbol]: # If the symbol is not in the FIRST set or it does not derive epsilon
            return False
    return True

# We create the function to check if the grammar has left recursion
def check_left_recursion(grammar):
    for nt in grammar:
        for production in grammar[nt]: # We verify each production rule of the NT
            if production[0] == nt:  # left recursion check
                print(f"Grammar has left recursion at {nt} → {production}")
                return True
    return False

# We create the function to do the LL(1) parsing of each string
def LL1(table, string):

    stack = [] # We create an empty array that will be used to store the strings that we are going to analyze
    stack = ['S', '$'] # This is always going to be the start of the 
    i = 0 # We initializate the counter of the string
    
    while i < len(string):

        if (stack[0] == string[i]): # If the terminal matches with the symbol in the string
            stack.pop(0)
            i = i+1 # The only way that we advance on the input string is deleting one terminal

        elif (stack[0] == 'e'):
            stack.pop(0)

        elif table[stack[0]][string[i]]: # If there is something in the parsing table in the specified position then:
            
            # We get a copy of what is on the parsing table
            production = table[stack[0]][string[i]].copy()
            stack.pop(0) # We delete the actual nt (that must be)

            for symbol in reversed(production): # we insert each symbol of the production in reverse order into the stack 
                stack.insert(0, symbol) 

        else:
            return False

    if not stack: # We verify that the stack is empty (as last verification)
        return True
    else:
        return False

def augmented_grammar(grammar):
    new_grammar = {}  # use normal dict, insertion order matters
    new_grammar["S'"] = [['S']]  # add the augmented production first

    for nt in grammar:
        new_grammar[nt] = grammar[nt]  # preserve order

    return new_grammar

def closure(I, new_grammar):
    closure_set = set(I)
    added = True

    while added:
        added = False
        new_items = set()

        for item in closure_set:
            lhs, rhs, dot = item
            if dot < len(rhs):
                symbol = rhs[dot]
                if symbol in new_grammar:
                    for production in new_grammar[symbol]:
                        nuevo = Item(symbol, tuple(production), 0)
                        if nuevo not in closure_set:
                            new_items.add(nuevo)

        if new_items:
            closure_set.update(new_items)
            added = True

    return closure_set

def goto(I, symbol, new_grammar):
    moved_items = set()

    for item in I:
        lhs, rhs, dot = item
        if dot < len(rhs) and rhs[dot] == symbol:
            moved_items.add(Item(lhs, tuple(rhs), dot + 1))

    return closure(moved_items, new_grammar)


def build_lr0_automaton(grammar):
    from collections import deque

    aug_grammar = augmented_grammar(grammar)
    I0 = closure([Item("S'", ('S',), 0)], aug_grammar)

    states = []
    transitions = {}
    state_indices = {}
    queue = deque()

    state_indices[frozenset(I0)] = 0
    states.append(I0)
    queue.append(I0)

    while queue:
        current = queue.popleft()
        current_index = state_indices[frozenset(current)]

        symbols = []
        seen = set()
        for item in current:
            if item.dot < len(item.rhs):
                sym = item.rhs[item.dot]
                if sym not in seen:
                    symbols.append(sym)
                    seen.add(sym)

        symbols.sort(key=lambda x: (x != 'S\'', x != 'S', x))  # Prioritize S', then S, then rest

        for symbol in symbols:
            next_state = goto(current, symbol, aug_grammar)
            frozen_next = frozenset(next_state)

            if frozen_next not in state_indices:
                state_indices[frozen_next] = len(states)
                states.append(next_state)
                queue.append(next_state)

            transitions[(current_index, symbol)] = state_indices[frozen_next]

    return states, transitions

def build_slr1_table(states, transitions, grammar, follow):
    action_table = defaultdict(dict)
    goto_table = defaultdict(dict)

    aug_grammar = augmented_grammar(grammar)

    for state_index, state in enumerate(states):
        for item in state:
            lhs, rhs, dot = item

            # Case 1: A → α • a β  → SHIFT
            if dot < len(rhs):
                symbol = rhs[dot]
                if symbol not in grammar:  # it's a terminal
                    next_state = transitions.get((state_index, symbol))
                    if next_state is not None:
                        if symbol in action_table[state_index]:
                            if action_table[state_index][symbol] != ('shift', next_state):
                                print(f"Conflict at state {state_index} on symbol '{symbol}'")
                                return None, None, False
                        else:
                            action_table[state_index][symbol] = ('shift', next_state)

            # Case 2: A → α •  → REDUCE
            elif lhs != "S'":  # not the augmented rule
                for terminal in follow[lhs]:
                    if terminal in action_table[state_index]:
                        if action_table[state_index][terminal] != ('reduce', (lhs, rhs)):
                            print(f"Conflict at state {state_index} on symbol '{terminal}'")
                            return None, None, False
                    else:
                        action_table[state_index][terminal] = ('reduce', (lhs, rhs))

            # Case 3: S' → S •  → ACCEPT
            elif lhs == "S'" and rhs == ('S',):
                action_table[state_index]['$'] = ('accept',)

        # GOTO: A → α • B β (B is non-terminal)
        for (from_idx, symbol), to_idx in transitions.items():
            if from_idx == state_index and symbol in grammar:  # it's a non-terminal
                goto_table[state_index][symbol] = to_idx

    return action_table, goto_table, True


def print_slr1_table(action_table, goto_table):
    # Collect all terminals and non-terminals from the tables
    terminals = set()
    non_terminals = set()

    for state in action_table:
        terminals.update(action_table[state].keys())

    for state in goto_table:
        non_terminals.update(goto_table[state].keys())

    terminals = sorted([t for t in terminals if t != '$']) + ['$']
    non_terminals = sorted(non_terminals)

    # Header
    header = ['State'] + [f'a:{t}' for t in terminals] + [f'g:{nt}' for nt in non_terminals]
    print('\t'.join(header))

    # Rows
    for state in sorted(set(action_table.keys()) | set(goto_table.keys())):
        row = [str(state)]
        for t in terminals:
            action = action_table[state].get(t, '')
            if action:
                if action[0] == 'shift':
                    row.append(f's{action[1]}')
                elif action[0] == 'reduce':
                    lhs, rhs = action[1]
                    rhs_str = ''.join(rhs)
                    row.append(f'r:{lhs}->{rhs_str}')
                elif action[0] == 'accept':
                    row.append('acc')
            else:
                row.append('')
        for nt in non_terminals:
            goto = goto_table[state].get(nt, '')
            row.append(str(goto) if goto != '' else '')
        print('\t'.join(row))

def slr1_parser(string, action_table, goto_table, trace=True):
    stack = [0]
    input_string = list(string) + ['$']
    pointer = 0

    if trace:
        print("\nSLR(1) Parsing Trace:")
        print(f"{'Stack':<20} {'Input':<20} {'Action'}")

    while True:
        state = stack[-1]
        symbol = input_string[pointer]
        action = action_table.get(state, {}).get(symbol, None)

        stack_str = ' '.join(map(str, stack))
        input_str = ''.join(input_string[pointer:])
        action_str = ""

        if action is None:
            if trace:
                print(f"{stack_str:<20} {input_str:<20} ERROR: Unexpected symbol '{symbol}'")
            return False

        if action[0] == 'shift':
            action_str = f"shift s{action[1]}"
            stack.append(symbol)
            stack.append(action[1])
            pointer += 1

        elif action[0] == 'reduce':
            lhs, rhs = action[1]
            action_str = f"reduce {lhs} → {''.join(rhs)}"
            if rhs != ('e',):  # not epsilon
                for _ in range(len(rhs) * 2):
                    stack.pop()
            current_state = stack[-1]
            stack.append(lhs)
            stack.append(goto_table[current_state][lhs])

        elif action[0] == 'accept':
            if trace:
                print(f"{stack_str:<20} {input_str:<20} ACCEPT")
            return True

        if trace:
            print(f"{stack_str:<20} {input_str:<20} {action_str}")


# run main
if __name__ == "__main__":
    main()