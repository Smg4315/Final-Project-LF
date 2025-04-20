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

    first_sets = compute_first(gramatica)
    follow_sets = compute_follow(gramatica, first_sets, start_symbol='S')

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
                    alternativas = [list(alt) for alt in alternativas_raw]

                    if no_terminal not in gramatica:
                        gramatica[no_terminal] = []

                    for alt in alternativas:
                        gramatica[no_terminal].append(alt)

                else:
                    print(f"Error: La regla '{linea}' no es válida.")
                    sys.exit(1)

            return gramatica
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'Grammars.txt'.")
        sys.exit(1)

def compute_first(grammar):
    first = defaultdict(set)
    changed = True

    # Inicializamos FIRST para los terminales
    for nt in grammar:
        for production in grammar[nt]:
            for chunk in production:
                for symbol in chunk:
                    if not symbol.isupper():  # es terminal o símbolo especial
                        first[symbol].add(symbol)

    # Repetimos hasta que no haya más cambios en los conjuntos FIRST
    while changed:
        changed = False
        for nt in grammar:
            for production in grammar[nt]:
                i = 0
                nullable = True
                before = len(first[nt])

                # Procesamos la producción símbolo por símbolo
                while i < len(production) and nullable:
                    chunk = production[i]  # ejemplo: "S+T" o "i" o "(S)"
                    for symbol in chunk:
                        first[nt].update(first[symbol] - {'e'})
                        if 'e' in first[symbol]:
                            continue
                        else:
                            nullable = False
                            break
                    i += 1

                if nullable:
                    first[nt].add('e')

                if len(first[nt]) > before:
                    changed = True

    return first


def compute_follow(grammar, first, start_symbol):
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