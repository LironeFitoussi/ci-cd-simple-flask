"""
app.py – Flask application for the DevOps Notes / Incidents API.

Run with:
    python app.py
"""

import datetime
import os

from flask import Flask, jsonify, request

from storage import load_notes, save_notes, get_next_id


app = Flask(__name__)


# ---------- Health check ----------

@app.route("/health", methods=["GET"])
def health():
    """Health-check endpoint used by the load balancer."""
    return jsonify({"status": "ok"}), 200


# ---------- List all notes ----------

@app.route("/notes", methods=["GET"])
def list_notes():
    """Return every note stored in the JSON file."""
    notes = load_notes()
    return jsonify(notes), 200


# ---------- Create a new note ----------

@app.route("/notes", methods=["POST"])
def create_note():
    """Create a new note from a JSON body with 'title' and 'status'."""
    body = request.get_json(silent=True)

    # --- Validate the request body ---
    if body is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = body.get("title")
    status = body.get("status")

    if not title:
        return jsonify({"error": "'title' is required"}), 400

    if status not in ("open", "closed"):
        return jsonify({"error": "'status' must be 'open' or 'closed'"}), 400

    # --- Build the new note ---
    notes = load_notes()

    new_note = {
        "id": get_next_id(notes),
        "title": title,
        "status": status,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    notes.append(new_note)
    save_notes(notes)

    return jsonify(new_note), 201


# ---------- Update an existing note ----------

@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    """Update the title and/or status of an existing note."""
    body = request.get_json(silent=True)

    if body is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    notes = load_notes()

    # Find the note with the matching ID
    note = None
    for n in notes:
        if n["id"] == note_id:
            note = n
            break

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    # Update fields if provided
    if "title" in body:
        note["title"] = body["title"]

    if "status" in body:
        if body["status"] not in ("open", "closed"):
            return jsonify({"error": "'status' must be 'open' or 'closed'"}), 400
        note["status"] = body["status"]

    save_notes(notes)

    return jsonify(note), 200


# ---------- Delete a note ----------

@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    """Delete a note by its ID."""
    notes = load_notes()

    # Find the note with the matching ID
    note = None
    for n in notes:
        if n["id"] == note_id:
            note = n
            break

    if note is None:
        return jsonify({"error": "Note not found"}), 404

    notes.remove(note)
    save_notes(notes)

    return jsonify({"message": "Note deleted"}), 200


# ---------- Start the server ----------

if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
