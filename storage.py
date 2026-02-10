"""
storage.py – File-based read/write logic for notes.

All data is stored in a local JSON file (data/notes.json).
"""

import json
import os


# Path to the JSON data file (relative to this script's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "notes.json")


def _ensure_file():
    """Create the data directory and notes.json if they do not exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)


def load_notes():
    """Read all notes from the JSON file and return them as a list."""
    _ensure_file()
    with open(DATA_FILE, "r") as f:
        notes = json.load(f)
    return notes


def save_notes(notes):
    """Write the full list of notes back to the JSON file."""
    _ensure_file()
    with open(DATA_FILE, "w") as f:
        json.dump(notes, f, indent=2)


def get_next_id(notes):
    """Return the next available integer ID.

    If the list is empty, start at 1.
    Otherwise, use the highest existing ID + 1.
    """
    if len(notes) == 0:
        return 1
    return max(note["id"] for note in notes) + 1
