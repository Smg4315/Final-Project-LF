# We import the libraries that will be used. In this case, we will use the sys library to handle errors
from collections import defaultdict
import sys

# We define the main function that will create at the moment a dictionary with the specified grammar.
def main():
    # We create the dictionary and fill it with the respective grammar
    gramatica = leer_gramatica('Grammars.txt')

    # We print the dictionary to verify that is working correctly
    for no_terminal, producciones in gramatica.items():
        print(f"{no_terminal} -> {producciones}")

    # We generate FIRST AND FOLLOW sets takin into account the specific grammar
    first_sets = FIRST(gramatica)
    follow_sets = FOLLOW(gramatica, first_sets, start_symbol='S')

    # We print them to see that they're working
    print("\nConjuntos FIRST:")
    for nt in gramatica:
        print(f"FIRST({nt}) = {first_sets[nt]}")

    print("\nConjuntos FOLLOW:")
    for nt in gramatica:
        print(f"FOLLOW({nt}) = {follow_sets[nt]}")

# We define the function that will read the grammar from the file and create a dictionary with it.
def leer_gramatica(archivo):

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

                    # We split the line into the left and right sides of the rule to separate the productions takn into account the symbol '->'
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
                    print(f"Error: La regla '{linea}' no es válida.")
                    sys.exit(1)
            return gramatica
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'Grammars.txt'.")
        sys.exit(1)

# We create the function to generate the FIRST sets it recives the dictionary that contains the grammar. 
def FIRST(grammar):

    # We create another dictionary that will contain the FIRST set of each non-terminal where each key is the non terminal and it value its the respetive FIRST set
    first = defaultdict(set)
    # Boolean to know when to stop 
    changed = True

    # Definition of the FIRST sets of terminals

    for nt in grammar: # For each production rule in the grammar (each NT) H -> [['+', 'T', 'H'], ['e']] iteration on the dictionary
        for production in grammar[nt]: # For each array of values in the dictionary [ ['+', 'T', 'H'], ['e'] ] (will be 1 iteration)
            for chunk in production: # For each production rule ['+', 'T', 'H'] and then['e']
                for symbol in chunk: # We check each symbol of the productions to determine wich is a terminal and wich is not '+' then 'T' and then 'H'
                    if not symbol.isupper():  # is terminal or special symbol
                        first[symbol].add(symbol) # We add it to the First dictionary with the same symbol


    # Now we are finding the FIRST sets of the NON-TERMINAL taking inton account the FIRST of the terminals
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
                    i += 1

                if nullable: # If all the chars of a productions contains the e, or me are reading the e, we add it to the FIRST set.
                    first[nt].add('e')

                if len(first[nt]) > before: # If there were changes, we continue
                    changed = True

    return first # After we finish we return the respective dictionary


def FOLLOW(grammar, first, start_symbol):
    follow = defaultdict(set)
    follow[start_symbol].add('$')

    changed = True
    while changed:
        changed = False
        for lhs in grammar:
            for production in grammar[lhs]:
                trailer = follow[lhs].copy()
                for chunk in reversed(production):
                    for symbol in reversed(chunk):
                        if symbol.isupper():
                            before = len(follow[symbol])
                            follow[symbol].update(trailer)
                            if 'e' in first[symbol]:
                                trailer.update(first[symbol] - {'e'})
                            else:
                                trailer = first[symbol]
                            if len(follow[symbol]) > before:
                                changed = True
                        else:
                            trailer = first[symbol]
    return follow

# Ejecutar main
if __name__ == "__main__":
    main()