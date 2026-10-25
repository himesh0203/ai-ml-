import importlib
from datetime import date
from fastapi.testclient import TestClient
import app.main as main


def setup_client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "test_students.db")
    main.init_db()
    return TestClient(main.app)


def sample_student(email="demo.student@example.com"):
    return {
        "name": "Demo Student",
        "date_of_birth": "2005-04-12",
        "email": email,
        "phone": "9000000001",
        "course": "B.Tech IT",
        "address": "Demo address",
        "enrollment_date": "2026-10-25",
    }


def test_full_crud_flow(tmp_path, monkeypatch):
    client = setup_client(tmp_path, monkeypatch)
    created = client.post("/students", json=sample_student())
    assert created.status_code == 201
    student_id = created.json()["id"]

    listed = client.get("/students")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/students/{student_id}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "demo.student@example.com"

    updated = client.put(f"/students/{student_id}", json={"course": "Computer Science"})
    assert updated.status_code == 200
    assert updated.json()["course"] == "Computer Science"

    deleted = client.delete(f"/students/{student_id}")
    assert deleted.status_code == 204
    assert client.get(f"/students/{student_id}").status_code == 404


def test_duplicate_email_returns_conflict(tmp_path, monkeypatch):
    client = setup_client(tmp_path, monkeypatch)
    assert client.post("/students", json=sample_student()).status_code == 201
    assert client.post("/students", json=sample_student()).status_code == 409


def test_validation_and_missing_record(tmp_path, monkeypatch):
    client = setup_client(tmp_path, monkeypatch)
    bad = sample_student()
    bad["email"] = "not-an-email"
    assert client.post("/students", json=bad).status_code == 422
    assert client.get("/students/999").status_code == 404
    assert client.delete("/students/999").status_code == 404


def test_search_and_filter(tmp_path, monkeypatch):
    client = setup_client(tmp_path, monkeypatch)
    assert client.post("/students", json=sample_student()).status_code == 201
    assert len(client.get("/students?search=Demo").json()) == 1
    assert len(client.get("/students?course=B.Tech").json()) == 1
    assert len(client.get("/students?born_after=2005-01-01").json()) == 1
