# DevOps Notes API

A simple internal API for managing text-based notes and incidents.
Built with Python and Flask as a training target for DevOps deployment
(Linux, EC2, ALB, CI/CD). All data is stored in a local JSON file -- no
database required.

---

## Project Structure

```
devops-notes-api/
├── app.py              # Flask application (API endpoints)
├── storage.py          # File-based read/write logic
├── requirements.txt    # Python dependencies
├── data/
│   └── notes.json      # Local data store (created automatically)
└── README.md
```

---

## How to Run Locally

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
source venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
python app.py
```

The server starts on **http://0.0.0.0:8000** by default.
To use a different port, set the `APP_PORT` environment variable:

```bash
APP_PORT=5000 python app.py
```

---

## API Endpoints

| Method | Path            | Description              |
| ------ | --------------- | ------------------------ |
| GET    | `/health`       | Health check (for ALB)   |
| GET    | `/notes`        | List all notes           |
| POST   | `/notes`        | Create a new note        |
| PUT    | `/notes/<id>`   | Update an existing note  |
| DELETE | `/notes/<id>`   | Delete a note            |

---

## Example curl Commands

### Health check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

### Create a note

```bash
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Server disk full", "status": "open"}'
```

Expected response (HTTP 201):

```json
{
  "id": 1,
  "title": "Server disk full",
  "status": "open",
  "created_at": "2026-02-10T12:00:00+00:00"
}
```

### List all notes

```bash
curl http://localhost:8000/notes
```

### Update a note

```bash
curl -X PUT http://localhost:8000/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "closed"}'
```

### Delete a note

```bash
curl -X DELETE http://localhost:8000/notes/1
```
# ci-cd-simple-flask
