from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="MozaikHane API", version="1.0", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "stats": {"total_visitors": 0, "active_users": 1},
        "grids": {}
    }

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.get("/api/stats")
def get_stats():
    db = load_db()
    return db["stats"]

@app.post("/api/stats/visit")
def increment_visitor():
    db = load_db()
    db["stats"]["total_visitors"] += 1
    save_db(db)
    return {"total_visitors": db["stats"]["total_visitors"]}

@app.get("/api/grid")
def get_all_grids():
    db = load_db()
    return db["grids"]

@app.get("/api/grid/{category}")
def get_grid(category: str):
    db = load_db()
    return db["grids"].get(category, {})

@app.post("/api/grid/{category}")
async def save_grid(category: str, request: Request):
    try:
        body = await request.json()
        db = load_db()
        if isinstance(body, dict) and "grid_data" in body:
            db["grids"][category] = body["grid_data"]
        else:
            db["grids"][category] = body
        save_db(db)
        return {"status": "success", "category": category}
    except Exception as e:
        return {"status": "error", "message": str(e)}
