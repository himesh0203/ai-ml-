# EWB Students Database CRUD API

A small, structured Python backend project for the **EWB Edu Tech Pvt. Ltd. Python Backend Development internship assignment**. It uses FastAPI for the REST API and SQLite for persistent storage.

## Features
- Create, list, retrieve, update, and delete student records
- Automatic unique numeric student ID
- Fields: name, date of birth, email, phone, course, address, enrollment date
- Input validation using Pydantic
- Unique email constraint and useful HTTP errors
- Search by name/email/course, filter by course or date of birth
- Pagination using `limit` and `offset`
- Interactive API docs at `/docs`
- SQLite database is created automatically on first run
- Automated tests for CRUD and error cases

## Requirements
- Python 3.10 or newer
- Internet connection for installing packages
- Git (for GitHub submission)

## Setup on Windows (VS Code)
Open this folder in VS Code, then open **Terminal → New Terminal**.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, use Command Prompt terminal and run:
```bat
.venv\Scripts\activate.bat
```

Open:
- API home: http://127.0.0.1:8000/
- Interactive Swagger docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Stop the server with `Ctrl+C`.

## API quick test
Use the Swagger page at `/docs`. Expand `POST /students` → **Try it out** and send:

```json
{
  "name": "Aarav Sharma",
  "date_of_birth": "2005-04-12",
  "email": "aarav.demo@example.com",
  "phone": "9000000001",
  "course": "B.Tech IT",
  "address": "Demo address",
  "enrollment_date": "2026-10-25"
}
```

Then test:
- `GET /students` — list records
- `GET /students?search=Aarav` — search
- `GET /students?course=B.Tech` — filter by course
- `GET /students?born_after=2005-01-01` — date-of-birth filter
- `GET /students/1` — retrieve by ID (use the ID returned by POST)
- `PUT /students/1` — update, e.g. `{"course":"Computer Science"}`
- `DELETE /students/1` — delete

A successful create returns `201`; a successful delete returns `204`; a missing record returns `404`; duplicate email returns `409`; invalid data returns `422`.

## Run automated tests
In a second terminal (keep the server stopped for the default tests):
```powershell
python -m pytest -q
```

Tests use a temporary SQLite database and do not touch your normal `students.db`.

## Project structure
```text
ewb_students_crud/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_api.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Push to GitHub (easy method)
1. Create/sign in to GitHub at https://github.com.
2. Click **New repository**. Name it `ewb-students-crud-api`. Choose **Public** if your trainer needs to view it, or follow your trainer's instructions. Do not add a README on GitHub if you already have one here.
3. On your computer, open this project folder in VS Code.
4. Open **Terminal → New Terminal** and run these commands one by one:

```bash
git init
git add .
git commit -m "Complete EWB students CRUD API"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ewb-students-crud-api.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Copy the repository URL from your newly created GitHub repository. If Git asks you to sign in, complete the browser sign-in prompt. Never put a password or token in your source code.

### If Git says your identity is unknown
```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```
Then repeat `git commit`.

### If `origin` already exists
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/ewb-students-crud-api.git
git push -u origin main
```

## Security and limitations
- Use synthetic/demo records only; do not commit real student data.
- The SQLite database is intentionally ignored by Git.
- This is a local assignment-ready API, not a production deployment. Before production use, add authentication/authorization, rate limiting, audit logging, backups, HTTPS deployment, and stricter CORS settings.
- The optional Ollama AI extension is not included because it is not required by the assignment. The CRUD core is the priority.
