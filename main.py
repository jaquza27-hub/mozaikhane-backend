from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MozaikHane API", version="1.0", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database = {
    "stats": {"total_visitors": 0, "active_users": 1},
    "grids": {}
}

@app.get("/api/stats")
def get_stats():
    return database["stats"]

@app.post("/api/stats/visit")
def increment_visitor():
    database["stats"]["total_visitors"] += 1
    return {"total_visitors": database["stats"]["total_visitors"]}

@app.get("/api/grid")
def get_all_grids():
    return database["grids"]

@app.get("/api/grid/{category}")
def get_grid(category: str):
    return database["grids"].get(category, {})

@app.post("/api/grid/{category}")
async def save_grid(category: str, request: Request):
    try:
        body = await request.json()
        if isinstance(body, dict) and "grid_data" in body:
            database["grids"][category] = body["grid_data"]
        else:
            database["grids"][category] = body
        return {"status": "success", "category": category}
    except Exception as e:
        return {"status": "error", "message": str(e)}
