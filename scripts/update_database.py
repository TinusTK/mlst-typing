#!/usr/bin/env python3
"""
update_database.py - rebuild database/ for mlst-typing from PubMLST,
BIGSdb-Pasteur and EnteroBase, then write a change summary.

    python scripts/update_database.py --db database --summary CHANGES_DB.md
    python scripts/update_database.py --db database --source enterobase

The code lives in tool/mlst_typing_update.py so that a pip install carries
it (`mlst-typing --setup` uses it to build a user's own database). This
file only calls it; options and exit codes are unchanged
(0 = updated, 3 = no changes, other = error).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tool"))

from mlst_typing_update import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
