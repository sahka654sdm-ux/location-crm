from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DB = BASE / "locations.db"

app = FastAPI(title="Location CRM Demo")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Объект',
            coordinate_text TEXT,
            status TEXT NOT NULL DEFAULT 'Новый',
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    count = conn.execute("SELECT COUNT(*) AS c FROM locations").fetchone()["c"]
    if count == 0:
        demo = [
            ("Склад №1", "Логистика", "DEMO-A1", "Активный", "Демонстрационная запись"),
            ("Пункт обслуживания", "Инфраструктура", "DEMO-B2", "Проверка", "Тестовый объект"),
            ("Маршрутная точка", "Навигация", "DEMO-C3", "Архив", "Синтетические данные"),
        ]
        for row in demo:
            conn.execute(
                "INSERT INTO locations(name,category,coordinate_text,status,notes,created_at) VALUES(?,?,?,?,?,?)",
                (*row, datetime.now().isoformat(timespec="seconds"))
            )
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = "", category: str = ""):
    conn = db()
    sql = "SELECT * FROM locations WHERE 1=1"
    args = []
    if q:
        sql += " AND (name LIKE ? OR notes LIKE ? OR coordinate_text LIKE ?)"
        like = f"%{q}%"
        args += [like, like, like]
    if category:
        sql += " AND category = ?"
        args.append(category)
    sql += " ORDER BY id DESC"
    rows = conn.execute(sql, args).fetchall()
    cats = [r["category"] for r in conn.execute("SELECT DISTINCT category FROM locations ORDER BY category")]
    conn.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "rows": rows,
        "q": q,
        "category": category,
        "categories": cats
    })

@app.post("/add")
def add(
    name: str = Form(...),
    category: str = Form("Объект"),
    coordinate_text: str = Form(""),
    status: str = Form("Новый"),
    notes: str = Form("")
):
    conn = db()
    conn.execute(
        "INSERT INTO locations(name,category,coordinate_text,status,notes,created_at) VALUES(?,?,?,?,?,?)",
        (name, category, coordinate_text, status, notes, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{item_id}")
def delete(item_id: int):
    conn = db()
    conn.execute("DELETE FROM locations WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

@app.get("/api/locations")
def api_locations():
    conn = db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM locations ORDER BY id DESC").fetchall()]
    conn.close()
    return JSONResponse(rows)

@app.get("/api/preview/{item_id}")
def preview(item_id: int):
    conn = db()
    row = conn.execute("SELECT * FROM locations WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not row:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse({
        "title": row["name"],
        "category": row["category"],
        "status": row["status"],
        "coordinate_text": row["coordinate_text"],
        "notes": row["notes"],
        "message_preview": f"{row['name']} | {row['category']} | {row['status']} | {row['coordinate_text'] or 'без координаты'}"
    })
