"""Run the nutmeg command with no install: python3 core/nutmeg.py <command> ..."""
import os
import sys

if sys.version_info < (3, 10):
    sys.exit("nutmeg needs Python 3.10 or newer (found %d.%d)" % sys.version_info[:2])

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nutmeg_core.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
