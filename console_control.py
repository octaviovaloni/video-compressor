import sys, main_functions

def up():
    sys.stdout.write("\033[F")

def down():
    sys.stdout.write("\n")
    
def write(msg: str):
    sys.stdout.write(msg + "\n")

def goto_begin():
    sys.stdout.write("\r")

def clean_line():
    goto_begin()
    sys.stdout.write("\033[K")

def flush():
    sys.stdout.flush()
    
def clean_upper_line():
    up()
    clean_line()
    flush()
    
def clean_upper_lines(lines: int):
    for _ in range(lines):
        clean_upper_line()

def clean():
    sys.stdout.write("\033[2J\033[H")
    flush()
    
def ask_yn(question: str): 
    while True:
        write(question + " (y/n)")
        answer = input("Answer: ").lower()
        if answer == "y":
            clean_line()
            clean_upper_line()
            clean_upper_line()
            return True
        elif answer == "n":
            clean_line()
            clean_upper_line()
            clean_upper_line()
            return False
        else:
            clean_line()
            clean_upper_line()
            clean_upper_line()

def ask_number(question: str): 
    while True:
        write(question + " (enter a number)")
        answer = input("Answer: ").strip()
        if main_functions.is_float(answer):
            clean_line()
            clean_upper_line()
            clean_upper_line()
            return float(answer)
        else:
            clean_line()
            clean_upper_line()
            clean_upper_line()