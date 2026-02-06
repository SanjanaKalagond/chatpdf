#!/usr/bin/env python
import os
import sys
from pathlib import Path


def main():
    ROOT_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(ROOT_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatpdf_backend.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
