from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "students.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT NOT NULL
            )
        """)


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    date_of_birth: date
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: date = Field(default_factory=date.today)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    date_of_birth: date
    email: EmailStr
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: date


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="EWB Students CRUD API",
    description="Student records API built with FastAPI and SQLite for the EWB internship assignment.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "EWB Students CRUD API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "database": "sqlite"}


@app.post("/students", response_model=StudentOut, status_code=201, tags=["Students"])
def create_student(student: StudentCreate):
    data = student.model_dump()
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()
    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO students
                (name, date_of_birth, email, phone, course, address, enrollment_date)
                VALUES (:name, :date_of_birth, :email, :phone, :course, :address, :enrollment_date)
            """, data)
            row = conn.execute("SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return dict(row)
    except sqlite3.IntegrityError as exc:
        if "email" in str(exc).lower():
            raise HTTPException(status_code=409, detail="A student with this email already exists.")
        raise HTTPException(status_code=400, detail="Could not create student.")


@app.get("/students", response_model=list[StudentOut], tags=["Students"])
def list_students(
    search: Optional[str] = Query(default=None, description="Search name, email, or course"),
    course: Optional[str] = None,
    born_after: Optional[date] = Query(default=None, description="Filter date of birth after this date"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    sql = "SELECT * FROM students WHERE 1=1"
    params = []
    if search:
        term = f"%{search.strip()}%"
        sql += " AND (name LIKE ? OR email LIKE ? OR course LIKE ?)"
        params.extend([term, term, term])
    if course:
        sql += " AND course LIKE ?"
        params.append(f"%{course.strip()}%")
    if born_after:
        sql += " AND date_of_birth > ?"
        params.append(born_after.isoformat())
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


@app.get("/students/{student_id}", response_model=StudentOut, tags=["Students"])
def get_student(student_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return dict(row)


@app.put("/students/{student_id}", response_model=StudentOut, tags=["Students"])
def update_student(student_id: int, student: StudentUpdate):
    changes = student.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Provide at least one field to update.")
    for key, value in changes.items():
        if isinstance(value, date):
            changes[key] = value.isoformat()
    try:
        with get_connection() as conn:
            exists = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
            if exists is None:
                raise HTTPException(status_code=404, detail="Student not found.")
            assignments = ", ".join(f"{key} = ?" for key in changes)
            conn.execute(
                f"UPDATE students SET {assignments} WHERE id = ?",
                [*changes.values(), student_id],
            )
            row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
            return dict(row)
    except sqlite3.IntegrityError as exc:
        if "email" in str(exc).lower():
            raise HTTPException(status_code=409, detail="A student with this email already exists.")
        raise HTTPException(status_code=400, detail="Could not update student.")


@app.delete("/students/{student_id}", status_code=204, tags=["Students"])
def delete_student(student_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found.")
    return Response(status_code=204)
