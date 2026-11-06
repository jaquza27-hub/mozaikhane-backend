from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import time

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
        "stats": {"total_visitors": 0},
        "active_sessions": {}
    }

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.get("/api/stats")
def get_stats():
    db = load_db()
    
    # Son 30 saniye içinde ping atmış aktif kullanıcıları say
    current_time = time.time()
    active_sessions = db.get("active_sessions", {})
    active_count = sum(1 for t in active_sessions.values() if current_time - t < 30)
    
    return {
        "total_visitors": db["stats"]["total_visitors"],
        "active_users": max(1, active_count)  # En az 1 göster
    }

@app.post("/api/stats/visit")
def increment_visitor():
    db = load_db()
    db["stats"]["total_visitors"] += 1
    save_db(db)
    return {"total_visitors": db["stats"]["total_visitors"]}

@app.post("/api/stats/ping")
async def active_ping(request: Request):
    try:
        body = await request.json()
        session_id = body.get("session_id")
        if session_id:
            db = load_db()
            if "active_sessions" not in db:
                db["active_sessions"] = {}
            db["active_sessions"][session_id] = time.time()
            
            # Eski oturumları temizle (1 dakikadan eski)
            current_time = time.time()
            db["active_sessions"] = {k: v for k, v in db["active_sessions"].items() if current_time - v < 60}
            
            save_db(db)
        return {"status": "ok"}
    except:
        return {"status": "error"}

@app.get("/api/grid")
def get_all_grids():
    db = load_db()
    return db.get("grids", {})

@app.get("/api/grid/{category}")
def get_grid(category: str):
    db = load_db()
    return db.get("grids", {}).get(category, {})

@app.post("/api/grid/{category}")
async def save_grid(category: str, request: Request):
    try:
        body = await request.json()
        db = load_db()
        if "grids" not in db:
            db["grids"] = {}
        if isinstance(body, dict) and "grid_data" in body:
            db["grids"][category] = body["grid_data"]
        else:
            db["grids"][category] = body
        save_db(db)
        return {"status": "success", "category": category}
    except Exception as e:
        return {"status": "error", "message": str(e)}
