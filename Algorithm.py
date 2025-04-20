# We import the libraries that will be used. In this case, we will use the sys library to handle errors
import sys

# We define the main function that will create at the moment a dictionary with the specified grammar.
def main():
    # We create the dictionary and fill it with the respective grammar
    gramatica = leer_gramatica('Grammars.txt')

    # We print the dictionary to verify that is working correctly
    for no_terminal, producciones in gramatica.items():
        print(f"{no_terminal} -> {producciones}")

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
                    alternativas = lado_der.strip().split()

                    # We verify that the non-terminal is not already in the dictionary, if it is not, we create a new entry for it
                    if no_terminal not in gramatica:
                        gramatica[no_terminal] = []

                    # Add the production to the list of productions for the non-terminal in the dictionary
                    gramatica[no_terminal].append(alternativas)
                else:
                    print(f"Error: La regla '{linea}' no es válida.")
                    sys.exit(1)

            return gramatica
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'Grammars.txt'.")
        sys.exit(1)

# Ejecutar main
if __name__ == "__main__":
    main()
