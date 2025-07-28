# __init__.py

from .radio import main
import curses

def main_wrapper():
    curses.wrapper(main)
