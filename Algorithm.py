# To find the FIRST set, we need to find the FIRST set of each non-terminal in the grammar, that is facilitated starting bottom-up.

# We import the libraries that will be used, in this case this one is for handing exceptions
import sys

def main():

    # We open the file that contains the grammar tha will be analized
    try:
        with open("Grammars.txt", "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("The file 'Grammars.txt' was not found.")
        sys.exit(1) # This will exit the program if the file is not found


if __name__ == "__main__":
    main()