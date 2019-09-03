from __future__ import absolute_import, division, unicode_literals

import sys

def main():
    from panel.cli import main as _main

   # Main entry point (see setup.py)
    _main(sys.argv)

if __name__ == "__main__":
    main()
