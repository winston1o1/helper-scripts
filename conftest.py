"""Pytest configuration: make the top-level packages importable.

The project's packages (``database_handler``, ``send_mail``,
``google_drive``, ``excel_tooling``, ``helper_scripts``) live at the
repository root. Inserting the root onto ``sys.path`` lets the tests
import them directly, replacing the old per-directory ``config.py``
``sys.path`` hack.
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
