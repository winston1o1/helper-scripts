"""Backward-compatibility namespace.

Re-exports the canonical top-level packages so legacy ``helper_scripts``
imports keep working, e.g. ``from helper_scripts import DB`` and
``from helper_scripts.database_handler import DB``.
"""
import sys

from database_handler import DB, ConfigHandler
from send_mail import SendMail
from google_drive import worker, get_service
from excel_tooling import toolbox

import database_handler
import send_mail
import google_drive
import excel_tooling

# Alias subpackages so ``from helper_scripts.database_handler import ...`` resolves.
sys.modules["helper_scripts.database_handler"] = database_handler
sys.modules["helper_scripts.send_mail"] = send_mail
sys.modules["helper_scripts.google_drive"] = google_drive
sys.modules["helper_scripts.excel_tooling"] = excel_tooling
