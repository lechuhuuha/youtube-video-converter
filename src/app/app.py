import sys


def main():
    if len(sys.argv) > 1:
        from .ui.cli import cli_main

        cli_main()
        return

    try:
        from .ui.tk_app import gui_main
    except ImportError:
        from .ui.cli import interactive_main

        interactive_main()
    else:
        gui_main()
