try:
    import tkinter as tk
    import filedialog as filedialog
except ImportError:
    import Tkinter as tk
    import tkFileDialog as filedialog

from string import ascii_uppercase
import math

HELP_TEXT ="""
Welcome to the minimal spreadsheet.

You can use this program to calculate neatly in table format.

SPACES ARE MANDATORY:

   5 + B1 =             # Is correct
   5+B1=                # Is wrong

In order to perform the calculation please end the formula with
an equal sign `=` and press the ENTER or RETURN key.

What you write it will be executed as Python code, so you
 * Can use all built-in functions and those in the math module**
   ** cell names must be surrounded by spaces, like `min(3, B5 )`
 * Must be careful not to hand to this program to ill-intentioned people.

If a cell is modified, cells depending on it are NOT automatically updated.
You must go back to them, delete what's after the `=` sign and press enter again.

Load and save work with `.csv` format.
"""

NUMBER_OF_ROWS = 15
NUMBER_OF_COLUMNS = 7

def is_reference(t):
    try:
        return t[0] in ascii_uppercase and t[1] in "1234567890" and (len(t) == 2 or t[-1] in "1234567890")
    except IndexError:
        return False

def get_reference(t, entries):
    x = ascii_uppercase.index(t[0])
    y = int(t[1:])
    return (entries[y-1][x]).get().split("=")[-1]

def evaluate_expression(entry, expression, entries):
    # Splitting by space is easier but frustating / unintutitve for the use
    # Splitting by regex is a bit more complex but allow space-less input, (more user-friendly)
    tokens = expression.replace('=', '').split(' ')
    tokens = [get_reference(t, entries) if is_reference(t) else t for t in tokens]
    entry.insert(len(expression), " " + str(eval(' '.join(tokens))))

root = tk.Tk()

root.wm_title("Minimal spreadsheet")

def display_popup(text):
    toplevel = tk.Toplevel()
    label1 = tk.Label(toplevel, text=text, height=0, width=100)
    label1.pack()

def save():
    filename = filedialog.asksaveasfilename()
    with open(filename,"w+") as f:
        for row in entries:
            f.write(','.join(cell.get() for cell in row) + "\n")

def open_():
    filename = filedialog.askopenfilename()
    with open(filename) as f:
        for y, line in enumerate(f):
            for x, val in enumerate(line.split(',')):
                entries[y][x].delete(0, tk.END)
                entries[y][x].insert(0, val if val != '''
''' else '')
                print val


tk.Button(root, text="Open", command=open_).grid(row=0, column=0)
tk.Button(root, text="Save", command=save).grid(row=0, column=1)


tk.Button(root, text="HELP", command=lambda: display_popup(HELP_TEXT)).grid(row=1, column=0)

for i in range(1, NUMBER_OF_ROWS+1):
    tk.Label(root, text=str(i)).grid(row=i+1, column=0)

for i in range(1, NUMBER_OF_COLUMNS+1):
    tk.Label(root, text=ascii_uppercase[i-1]).grid(row=0+1, column=i)

entries = []
for y in range(NUMBER_OF_ROWS):
    temp_entries = []
    for x in range(NUMBER_OF_COLUMNS):
        e = tk.Entry(root)
        e.grid(row=y+1+1, column=x+1)
        e.bind('<Return>', lambda _, e=e: evaluate_expression(e, e.get(), entries))# Not yet defined?
        temp_entries.append(e)
    entries.append(temp_entries)

root.mainloop()