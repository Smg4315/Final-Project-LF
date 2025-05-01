# We import the libraries that will be used. In this case, we will use the sys library to handle errors
from collections import defaultdict
import sys

# We define the main function that will create at the moment a dictionary with the specified grammar.
def main():

    # We create the dictionary and fill it with the respective grammar
    strings = [] # We create an empty array that will be used to store the strings that we are going to analyze
    gramatica = leer_gramatica('Grammars.txt', strings)
    
    # We generate FIRST AND FOLLOW sets takin into account the specific grammar
    first_sets = FIRST(gramatica)
    follow_sets = FOLLOW(gramatica, first_sets)

    for i in range (len(strings)):
       print(f"String {i+1}: {strings[i]}")

    # We check if the grammar has left recursion (if is not the case, the create the parsing table: )
    if not check_left_recursion(gramatica):
        table = parsing_table(gramatica, first_sets, follow_sets) # We generate the parsing table
    else:
        print("Grammar his not LL(1) because it has left recursion")
        return

    # We check if the parsing table is empty, if it is we print the parsing table
    if table:
     print("grammar is LL(1)")
     for no_terminal, entradas in table.items():
        print(f"No terminal: {no_terminal}")
        for terminal, produccion in entradas.items():
            print(f"  Con terminal '{terminal}': {produccion}")

    # We print them to see that they're working
    print("\nConjuntos FIRST:")
    for nt in gramatica:
        print(f"FIRST({nt}) = {first_sets[nt]}")

    print("\nConjuntos FOLLOW:")
    for nt in gramatica:
        print(f"FOLLOW({nt}) = {follow_sets[nt]}")

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
                    print(f"Error: La regla '{linea}' no es válida. se esperaba 'no_terminal -> producciones'.")
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
def parsing_table(grammar, first, follow):

 tabla = defaultdict(lambda: defaultdict(list)) # We create a dictionary of dictionaries to store the parsing table 

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
                                         print("Grammar is not LL(1) because is ambiguous")
                                         return # the function will return None
             
             # We only take into account the FOLLOW set if the production rule is a null production because its the only posible case
             else: # If the production rule is a null production, we have to add each terminal of the FOLLOW set to the parsing table
                 for symbol in follow[nt]:
                     # if the table is empty we add the production rule
                     if not tabla[nt][symbol]: 
                         tabla[nt][symbol] = production
                     else:
                         print("Grammar is not LL(1) because is ambiguous")
                         return

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
                                 print("Grammar is not LL(1) because is ambiguous")
                                 return # the function will return None
          
         # We are checking the cases where the production rule is a null production (its like to do it again but not neccesary with only e productions)
         if derives_epsilon(production, first):
             for symbol in follow[nt]:
                 if not tabla[nt][symbol]:
                     tabla[nt][symbol] = production # We add the production rule (not neccesarily null production)
                 else:
                     if tabla[nt][symbol] != production:
                         print("Grammar is not LL(1) because is ambiguous")
                         return 

 return tabla

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

# run main
if __name__ == "__main__":
    main()