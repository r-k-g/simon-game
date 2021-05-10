from fltk import Fl

from game import SimonGame

def main():
    win = SimonGame(700, 730)
    win.show()
    Fl.run()

if __name__ == "__main__":
    main()