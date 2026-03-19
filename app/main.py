import tkinter as tk
import sys
import os

# allow import from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gui import PasswordGeneratorGUI


def main():
    root = tk.Tk()
    PasswordGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()